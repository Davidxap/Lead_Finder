# test_api.py
import requests
import json

url = "https://linkedin.programando.io/fetch_lead2"

# Parámetros como JSON body (en un GET - inusual pero válido)
body = {
    "limit": 10,
    "location": ["United States"]  # Array como dijiste al inicio
}

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Lead-Finder/1.0"
}

print("Testing GET with JSON body...")

# GET con body (usando requests permite esto)
response = requests.request(
    "GET",
    url,
    data=json.dumps(body),
    headers=headers,
    timeout=30
)

print(f"Status: {response.status_code}")
print(f"URL: {response.url}")

if response.status_code == 200:
    data = response.json()
    print(f"\n✅ SUCCESS!")
    print(f"Total results: {len(data.get('results', []))}")
    print(f"\nFirst result:")
    if data.get('results'):
        print(json.dumps(data['results'][0], indent=2))
else:
    print(f"\n❌ Error: {response.status_code}")
    print(f"Response: {response.text[:500]}")