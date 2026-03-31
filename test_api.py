
import httpx
import json

def test_api():
    try:
        url = "http://127.0.0.1:8000/analyze"
        payload = {"symbol": "RELIANCE.NS"}
        response = httpx.post(url, json=payload, timeout=30.0)
        print(f"Status: {response.status_code}")
        print(f"Body: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
