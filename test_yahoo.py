import httpx
symbol = "RELIANCE.NS"
base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}
try:
    response = httpx.get(
        "{}/{}".format(base_url, symbol),
        params={"range": "1mo", "interval": "1d"},
        headers=headers,
        timeout=10.0,
    )
    print(f"Status Code: {response.status_code}")
    payload = response.json()
    chart_result = payload.get("chart", {}).get("result", [])
    if not chart_result:
        print("No result")
    else:
        print("Data found!")
        print(f"Meta: {chart_result[0].get('meta', {}).get('symbol')}")
except Exception as e:
    print(f"Error: {e}")
