# test_production_api.py
"""
Production API Testing Script
Run this when API is back online to validate all filters
"""

import requests
import json
import time
from datetime import datetime

API_URL = "https://linkedin.programando.io/fetch_lead2"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "PostmanRuntime/7.49.1"
}

# Test cases based on known working configurations
PRODUCTION_TESTS = [
    {
        "name": "Position Filter (Known Working)",
        "body": {"limit": 10, "position": ["Engineer"]},
        "expected_status": 200,
        "timeout": 30
    },
    {
        "name": "Position Filter - Director",
        "body": {"limit": 10, "position": ["Director"]},
        "expected_status": 200,
        "timeout": 30
    },
    {
        "name": "Seniority Level - Senior",
        "body": {"limit": 10, "level": ["Senior"]},
        "expected_status": 200,
        "timeout": 30
    },
    {
        "name": "Seniority Level - Manager",
        "body": {"limit": 10, "level": ["Manager"]},
        "expected_status": 200,
        "timeout": 30
    },
    {
        "name": "Industry Filter - Technology",
        "body": {"limit": 10, "company_industry": ["Technology"]},
        "expected_status": 200,
        "timeout": 30
    },
    {
        "name": "Industry Filter - Construction",
        "body": {"limit": 10, "company_industry": ["Construction"]},
        "expected_status": 200,
        "timeout": 30
    },
    {
        "name": "Location Filter - United States (May Timeout)",
        "body": {"limit": 10, "location": ["United States"]},
        "expected_status": 200,
        "timeout": 60,
        "allow_timeout": True
    },
    {
        "name": "Company Filter (May Timeout)",
        "body": {"limit": 10, "company_name": ["Google"]},
        "expected_status": 200,
        "timeout": 60,
        "allow_timeout": True
    },
]

def run_production_tests():
    """Run all production API tests"""
    
    print("=" * 100)
    print(f"PRODUCTION API TESTING - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)
    print(f"API URL: {API_URL}")
    print(f"Total Tests: {len(PRODUCTION_TESTS)}\n")
    
    results = []
    passed = 0
    failed = 0
    timeouts = 0
    
    for i, test in enumerate(PRODUCTION_TESTS, 1):
        print(f"\n[TEST {i}/{len(PRODUCTION_TESTS)}] {test['name']}")
        print("-" * 100)
        print(f"Body: {json.dumps(test['body'])}")
        
        try:
            start = time.time()
            
            response = requests.get(
                API_URL,
                data=json.dumps(test['body']),
                headers=HEADERS,
                timeout=test['timeout']
            )
            
            elapsed = round(time.time() - start, 2)
            
            if response.status_code == test['expected_status']:
                data = response.json()
                count = len(data.get('results', []))
                
                print(f"✅ PASS - {count} results in {elapsed}s")
                
                if count > 0:
                    first = data['results'][0]
                    print(f"   Sample: {first.get('name')} {first.get('surname')} at {first.get('company_name')}")
                
                passed += 1
                results.append({
                    'test': test['name'],
                    'status': 'PASS',
                    'count': count,
                    'time': elapsed
                })
            else:
                print(f"❌ FAIL - Status {response.status_code}")
                failed += 1
                results.append({
                    'test': test['name'],
                    'status': 'FAIL',
                    'error': f"Status {response.status_code}"
                })
                
        except requests.Timeout:
            if test.get('allow_timeout'):
                print(f"⚠️  TIMEOUT (expected) - Filter may not be supported")
                timeouts += 1
                results.append({
                    'test': test['name'],
                    'status': 'TIMEOUT_EXPECTED'
                })
            else:
                print(f"❌ TIMEOUT - Unexpected")
                failed += 1
                results.append({
                    'test': test['name'],
                    'status': 'TIMEOUT_FAIL'
                })
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            failed += 1
            results.append({
                'test': test['name'],
                'status': 'ERROR',
                'error': str(e)
            })
        
        # Wait between tests
        if i < len(PRODUCTION_TESTS):
            time.sleep(2)
    
    # Summary
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"✅ Passed: {passed}/{len(PRODUCTION_TESTS)}")
    print(f"❌ Failed: {failed}/{len(PRODUCTION_TESTS)}")
    print(f"⚠️  Timeouts: {timeouts}/{len(PRODUCTION_TESTS)}")
    
    print("\n📋 WORKING FILTERS:")
    for r in results:
        if r['status'] == 'PASS':
            print(f"  ✅ {r['test']}: {r.get('count', 0)} results in {r.get('time', 0)}s")
    
    print("\n⚠️  PROBLEMATIC FILTERS:")
    for r in results:
        if r['status'] in ['TIMEOUT_EXPECTED', 'TIMEOUT_FAIL', 'FAIL', 'ERROR']:
            print(f"  ❌ {r['test']}: {r['status']}")
    
    # Save results
    with open('production_api_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total': len(PRODUCTION_TESTS),
                'passed': passed,
                'failed': failed,
                'timeouts': timeouts
            },
            'results': results
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: production_api_test_results.json")

if __name__ == "__main__":
    run_production_tests()