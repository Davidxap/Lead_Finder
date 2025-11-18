# test_exact_postman.py
import requests
import json
import brotli

url = "https://linkedin.programando.io/fetch_lead2"

body = {
    "limit": 10,
    "location": ["United States"]
}

# EXACT headers from Postman (removing Postman-Token as it's auto-generated)
headers = {
    "Content-Type": "application/json",
    "User-Agent": "PostmanRuntime/7.49.1",
    "Accept": "*/*",
    "Cache-Control": "no-cache",
    "Host": "linkedin.programando.io",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

print("Testing exact Postman configuration")
print("="*80)

response = requests.get(
    url,
    data=json.dumps(body),
    headers=headers,
    timeout=30
)

print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"Content-Encoding: {response.headers.get('Content-Encoding')}")
print(f"CF-Cache-Status: {response.headers.get('cf-cache-status')}")

if response.status_code == 200:
    # Handle Brotli decompression
    if response.headers.get('Content-Encoding') == 'br':
        print("Decompressing Brotli...")
        content = brotli.decompress(response.content)
        data = json.loads(content.decode('utf-8'))
    else:
        data = response.json()
    
    results = data.get('results', [])
    print(f"\nSUCCESS - {len(results)} results")
    
    if results:
        print(f"\nFirst lead:")
        print(f"  Name: {results[0]['name']} {results[0]['surname']}")
        print(f"  Position: {results[0]['position']}")
        print(f"  Company: {results[0]['company_name']}")
else:
    print(f"FAILED")
    print(f"Response: {response.text[:300]}")