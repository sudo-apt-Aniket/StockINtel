
import httpx
import json

def test_radar():
    try:
        url = "http://127.0.0.1:8000/radar"
        payload = {"symbols": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"]}
        response = httpx.post(url, json=payload, timeout=60.0)
        print(f"Status: {response.status_code}")
        results = response.json().get("results", [])
        for item in results:
            print(f"Symbol: {item['symbol']} -> Confidence: {item['confidence']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_radar()
