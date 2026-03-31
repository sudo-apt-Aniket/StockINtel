
import requests
import json

def test_radar():
    try:
        url = "http://127.0.0.1:8000/radar"
        payload = {"symbols": ["RELIANCE", "TCS", "INFY"]}
        print(f"Sending request to {url}...")
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        data = response.json()
        results = data.get("results", [])
        if not results:
            print("No results returned.")
            print(f"Full response: {json.dumps(data, indent=2)}")
        for item in results:
            print(f"SYMBOL: {item['symbol']} -> CONFIDENCE: {item['confidence']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_radar()
