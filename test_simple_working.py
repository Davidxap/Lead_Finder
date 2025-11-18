# test_simple_working.py
import requests
import json

url = "https://linkedin.programando.io/fetch_lead2"

body = {
    "limit": 10,
    "location": ["United States"]
}

headers = {
    "Content-Type": "application/json",
    "User-Agent": "PostmanRuntime/7.49.1"
}

print("Simple test - let requests handle everything")
print("="*80)

response = requests.get(
    url,
    data=json.dumps(body),
    headers=headers,
    timeout=30
)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    results = data.get('results', [])
    print(f"SUCCESS - {len(results)} results")
    
    if results:
        print(f"First: {results[0]['name']} {results[0]['surname']}")
else:
    print(f"Failed: {response.text[:200]}")