import requests
import json

base_url = "http://127.0.0.1:8000"

def test_radar():
    print("Testing Opportunity Radar...")
    payload = {
        "symbols": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "INVALID_TICKER"],
        "timeframe": "1d",
        "include_news": True
    }
    try:
        response = requests.post(f"{base_url}/radar", json=payload, timeout=60)
        print(f"Status Code: {response.status_code}")
        results = response.json().get("results", [])
        print(f"Found {len(results)} results")
        for res in results:
            print(f"- {res['symbol']}: {res['action']} ({res['confidence']*100:.1f}%) | {res['explanation'][:50]}...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_radar()
