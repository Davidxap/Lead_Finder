# test_filters.py
import requests
import json

url = "https://linkedin.programando.io/fetch_lead2"

# Test 1: Solo por title
print("=" * 50)
print("TEST 1: Solo por Title")
print("=" * 50)
body1 = {
    "limit": 5,
    "position": "Engineer"
}

response1 = requests.request("GET", url, data=json.dumps(body1), 
                             headers={"Content-Type": "application/json"}, 
                             timeout=30)
print(f"Status: {response1.status_code}")
if response1.status_code == 200:
    print(f"Results: {len(response1.json().get('results', []))}")
else:
    print(f"Error: {response1.text[:200]}")

# Test 2: Solo por company
print("\n" + "=" * 50)
print("TEST 2: Solo por Company")
print("=" * 50)
body2 = {
    "limit": 5,
    "company_name": "Google"
}

response2 = requests.request("GET", url, data=json.dumps(body2), 
                             headers={"Content-Type": "application/json"}, 
                             timeout=30)
print(f"Status: {response2.status_code}")
if response2.status_code == 200:
    print(f"Results: {len(response2.json().get('results', []))}")
else:
    print(f"Error: {response2.text[:200]}")

# Test 3: Solo por industry
print("\n" + "=" * 50)
print("TEST 3: Solo por Industry")
print("=" * 50)
body3 = {
    "limit": 5,
    "company_industry": "Technology"
}

response3 = requests.request("GET", url, data=json.dumps(body3), 
                             headers={"Content-Type": "application/json"}, 
                             timeout=30)
print(f"Status: {response3.status_code}")
if response3.status_code == 200:
    print(f"Results: {len(response3.json().get('results', []))}")
else:
    print(f"Error: {response3.text[:200]}")

# Test 4: Combinado
print("\n" + "=" * 50)
print("TEST 4: Combinado (Title + Location + Industry)")
print("=" * 50)
body4 = {
    "limit": 5,
    "position": "Manager",
    "location": ["United States"],
    "company_industry": "Technology"
}

response4 = requests.request("GET", url, data=json.dumps(body4), 
                             headers={"Content-Type": "application/json"}, 
                             timeout=30)
print(f"Status: {response4.status_code}")
if response4.status_code == 200:
    print(f"Results: {len(response4.json().get('results', []))}")
    print(f"First result: {response4.json().get('results', [{}])[0].get('name', 'N/A')}")
else:
    print(f"Error: {response4.text[:200]}")