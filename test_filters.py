# test_filters.py
import requests
import json

url = "https://linkedin.programando.io/fetch_lead2"

tests = [
    {
        "name": "TEST 1: Solo Title",
        "body": {"limit": 5, "position": "Engineer"}
    },
    {
        "name": "TEST 2: Solo Company ARRAY (Top 000)",
        "body": {"limit": 5, "company_name": ["Top 000"]}
    },
    {
        "name": "TEST 3: Solo Company ARRAY (0-One)",
        "body": {"limit": 5, "company_name": ["0-One"]}
    },
    {
        "name": "TEST 4: Solo Industry",
        "body": {"limit": 5, "company_industry": "Construction"}
    },
    {
        "name": "TEST 5: Solo Location",
        "body": {"limit": 5, "location": ["United States"]}
    },
    {
        "name": "TEST 6: Company + Location",
        "body": {"limit": 5, "company_name": ["PK-0"], "location": ["United States"]}
    },
    {
        "name": "TEST 7: Title + Industry",
        "body": {"limit": 5, "position": "Director", "company_industry": "Construction"}
    },
]

headers = {"Content-Type": "application/json"}

print("🔍 Testing LinkedIn API Filters")
print("=" * 70)

for i, test in enumerate(tests, 1):
    print(f"\n{test['name']}")
    print("-" * 70)
    print(f"Body: {json.dumps(test['body'])}")
    
    try:
        response = requests.request(
            "GET", 
            url, 
            data=json.dumps(test['body']), 
            headers=headers, 
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            print(f"✅ SUCCESS - Status: {response.status_code} | Results: {len(results)}")
            if results:
                first = results[0]
                print(f"   📋 Sample: {first.get('name')} {first.get('surname')} at {first.get('company_name')}")
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            error_text = response.text[:200]
            print(f"   Error: {error_text}")
    
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")

print("\n" + "=" * 70)
print("✅ Tests completed")