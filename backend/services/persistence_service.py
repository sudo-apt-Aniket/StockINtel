"""Persistence service for analysis history and alert records."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from backend.services.database import Database


class PersistenceService:
    """Store and retrieve completed analyses and generated alerts."""

    def __init__(self, database: Database, alert_confidence_threshold: float = 0.7) -> None:
        self.database = database
        self.alert_confidence_threshold = alert_confidence_threshold

    def initialize(self) -> None:
        """Ensure storage schema exists."""
        self.database.initialize()

    def save_analysis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Persist an analysis result and create an alert when it is actionable."""
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO analyses (
                    symbol,
                    timeframe,
                    request_payload,
                    summary_payload,
                    market_snapshot_payload,
                    signals_payload,
                    patterns_payload,
                    pipeline_payload,
                    confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["request"]["symbol"],
                    payload["request"]["timeframe"],
                    json.dumps(payload["request"]),
                    json.dumps(payload["summary"]),
                    json.dumps(payload["market_snapshot"]),
                    json.dumps(payload["signals"]),
                    json.dumps(payload["patterns"]),
                    json.dumps(payload["pipeline"]),
                    payload["summary"]["confidence"],
                ),
            )
            analysis_id = cursor.lastrowid
            alert_id = self._create_alert_if_needed(connection, analysis_id, payload)
            connection.commit()

        return {
            "analysis_id": analysis_id,
            "alert_id": alert_id,
        }

    def list_recent_analyses(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Return recently stored analyses with decoded payload fields."""
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, symbol, timeframe, summary_payload, confidence, created_at
                FROM analyses
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        analyses: List[Dict[str, Any]] = []
        for row in rows:
            summary_payload = json.loads(row["summary_payload"])
            analyses.append(
                {
                    "analysis_id": row["id"],
                    "symbol": row["symbol"],
                    "timeframe": row["timeframe"],
                    "confidence": row["confidence"],
                    "created_at": row["created_at"],
                    "summary": summary_payload,
                }
            )
        return analyses

    def get_analysis(self, analysis_id: int) -> Optional[Dict[str, Any]]:
        """Return a fully decoded persisted analysis by id."""
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT id, symbol, timeframe, request_payload, summary_payload,
                       market_snapshot_payload, signals_payload, patterns_payload,
                       pipeline_payload, confidence, created_at
                FROM analyses
                WHERE id = ?
                """,
                (analysis_id,),
            ).fetchone()

        if row is None:
            return None

        return {
            "analysis_id": row["id"],
            "symbol": row["symbol"],
            "timeframe": row["timeframe"],
            "confidence": row["confidence"],
            "created_at": row["created_at"],
            "request": json.loads(row["request_payload"]),
            "summary": json.loads(row["summary_payload"]),
            "market_snapshot": json.loads(row["market_snapshot_payload"]),
            "signals": json.loads(row["signals_payload"]),
            "patterns": json.loads(row["patterns_payload"]),
            "pipeline": json.loads(row["pipeline_payload"]),
        }

    def list_open_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Return the most recent open alerts."""
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, analysis_id, symbol, alert, recommendation, confidence, status, created_at, updated_at
                FROM alerts
                WHERE status = 'open'
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            {
                "alert_id": row["id"],
                "analysis_id": row["analysis_id"],
                "symbol": row["symbol"],
                "alert": row["alert"],
                "recommendation": row["recommendation"],
                "confidence": row["confidence"],
                "status": row["status"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
            for row in rows
        ]

    def update_alert_status(self, alert_id: int, status: str) -> Optional[Dict[str, Any]]:
        """Update an alert lifecycle status and return the updated record."""
        allowed_statuses = {"open", "acknowledged", "closed"}
        if status not in allowed_statuses:
            raise ValueError("Unsupported alert status.")

        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE alerts
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (status, alert_id),
            )
            if cursor.rowcount == 0:
                return None
            connection.commit()

        return self.get_alert(alert_id)

    def get_alert(self, alert_id: int) -> Optional[Dict[str, Any]]:
        """Return a single alert by id."""
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT id, analysis_id, symbol, alert, recommendation, confidence, status, created_at, updated_at
                FROM alerts
                WHERE id = ?
                """,
                (alert_id,),
            ).fetchone()

        if row is None:
            return None

        return {
            "alert_id": row["id"],
            "analysis_id": row["analysis_id"],
            "symbol": row["symbol"],
            "alert": row["alert"],
            "recommendation": row["recommendation"],
            "confidence": row["confidence"],
            "status": row["status"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def _create_alert_if_needed(
        self, connection: Any, analysis_id: int, payload: Dict[str, Any]
    ) -> Optional[int]:
        """Create an alert record when the analysis appears actionable."""
        confidence = payload["summary"]["confidence"]
        actionable_statuses = {"bullish", "bearish", "watch", "overbought", "oversold"}
        has_actionable_signal = any(
            signal["status"] in actionable_statuses for signal in payload["signals"]["signals"]
        )
        has_actionable_pattern = any(
            pattern["status"] in actionable_statuses for pattern in payload["patterns"]["patterns"]
        )

        if confidence < self.alert_confidence_threshold and not (has_actionable_signal or has_actionable_pattern):
            return None

        cursor = connection.execute(
            """
            INSERT INTO alerts (analysis_id, symbol, alert, recommendation, confidence)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                analysis_id,
                payload["summary"]["symbol"],
                payload["summary"]["alert"],
                payload["summary"]["recommendation"],
                confidence,
            ),
        )
        return cursor.lastrowid

    def save_portfolio(self, name: str, symbols: List[str]) -> Dict[str, Any]:
        """Create or update a portfolio."""
        symbols_json = json.dumps(list(set(s.upper() for s in symbols)))
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO portfolios (name, symbols)
                VALUES (?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    symbols = excluded.symbols,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (name, symbols_json),
            )
            portfolio_id = cursor.lastrowid
            connection.commit()
            
        return self.get_portfolio(name)

    def get_portfolio(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a portfolio by name."""
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT id, name, symbols, created_at, updated_at FROM portfolios WHERE name = ?",
                (name,)
            ).fetchone()
            
        if not row:
            return None
            
        return {
            "id": row["id"],
            "name": row["name"],
            "symbols": json.loads(row["symbols"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    def list_portfolios(self) -> List[Dict[str, Any]]:
        """Retrieve all portfolios."""
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT id, name, symbols, created_at, updated_at FROM portfolios ORDER BY id DESC"
            ).fetchall()
            
        return [
            {
                "id": row["id"],
                "name": row["name"],
                "symbols": json.loads(row["symbols"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
            for row in rows
        ]
