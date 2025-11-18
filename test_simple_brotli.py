# test_simple_brotli.py
import requests
import json
import brotli

url = "https://linkedin.programando.io/fetch_lead2"
body = json.dumps({"limit": 10, "location": ["United States"]})

headers = {
    "Content-Type": "application/json",
    "User-Agent": "PostmanRuntime/7.49.1",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

req = requests.Request("GET", url, data=body, headers=headers)
prepared = req.prepare()

session = requests.Session()
response = session.send(prepared, timeout=90)

print(f"Status: {response.status_code}")
print(f"Encoding: {response.headers.get('Content-Encoding')}")

content = response.content
print(f"First bytes: {content[:10]}")

if response.headers.get('Content-Encoding') == 'br':
    content = brotli.decompress(content)
    print("Decompressed with Brotli")

text = content.decode('utf-8')
data = json.loads(text)

print(f"Results: {len(data.get('results', []))}")
print(f"First lead: {data['results'][0]['name'] if data.get('results') else 'None'}")