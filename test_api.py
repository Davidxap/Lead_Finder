# test_api.py
import requests
import json
import time

url = "https://linkedin.programando.io/fetch_lead2"
headers = {"Content-Type": "application/json"}

tests = [
    {
        "name": "TEST 1: Solo Title",
        "body": {"limit": 10, "position": "Engineer"}
    },
    {
        "name": "TEST 2: Solo Company (Top 000)",
        "body": {"limit": 10, "company_name": ["Top 000"]}
    },
    {
        "name": "TEST 3: Solo Company (0-One)",
        "body": {"limit": 10, "company_name": ["0-One"]}
    },
    {
        "name": "TEST 4: Solo Company (PK-0)",
        "body": {"limit": 10, "company_name": ["PK-0"]}
    },
    {
        "name": "TEST 5: Solo Industry (Construction)",
        "body": {"limit": 10, "company_industry": "Construction"}
    },
    {
        "name": "TEST 6: Solo Location (United States)",
        "body": {"limit": 10, "location": ["United States"]}
    },
    {
        "name": "TEST 7: Title + Industry",
        "body": {"limit": 10, "position": "Director", "company_industry": "Construction"}
    },
    {
        "name": "TEST 8: Company + Location",
        "body": {"limit": 10, "company_name": ["Various Companies"], "location": ["United States"]}
    },
    {
        "name": "TEST 9: Title + Location + Industry",
        "body": {"limit": 10, "position": "Manager", "location": ["United States"], "company_industry": "Technology"}
    },
]

print("🔍 Testing LinkedIn API - All Filter Combinations")
print("=" * 80)

total_tests = len(tests)
passed_tests = 0
failed_tests = 0

for i, test in enumerate(tests, 1):
    print(f"\n[{i}/{total_tests}] {test['name']}")
    print("-" * 80)
    print(f"📤 Request Body: {json.dumps(test['body'])}")
    
    try:
        start_time = time.time()
        
        response = requests.request(
            "GET", 
            url, 
            data=json.dumps(test['body']), 
            headers=headers, 
            timeout=60
        )
        
        elapsed = round(time.time() - start_time, 2)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            print(f"✅ SUCCESS - Status: {response.status_code} | Results: {len(results)} | Time: {elapsed}s")
            
            if results:
                first = results[0]
                print(f"   📋 First Lead: {first.get('name', 'N/A')} {first.get('surname', 'N/A')} at {first.get('company_name', 'N/A')}")
                print(f"   🏢 Company: {first.get('company_name')} ({first.get('company_headcount', 'N/A')})")
                print(f"   📍 Location: {first.get('location', 'N/A')}")
            else:
                print(f"   ⚠️  No results found")
            
            passed_tests += 1
            
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Error: {response.text[:300]}")
            
            failed_tests += 1
    
    except requests.exceptions.Timeout:
        print(f"⏱️  TIMEOUT - Request took longer than 60 seconds")
        failed_tests += 1
        
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        failed_tests += 1

print("\n" + "=" * 80)
print(f"📊 SUMMARY: {passed_tests}/{total_tests} tests passed, {failed_tests} failed")
print("=" * 80)

if passed_tests == total_tests:
    print("🎉 ALL TESTS PASSED! Your API integration is working correctly.")
else:
    print(f"⚠️  {failed_tests} test(s) failed. Review the errors above.")