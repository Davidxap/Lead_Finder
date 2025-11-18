# test_real_api_data.py
import requests
import json
import time

url = "https://linkedin.programando.io/fetch_lead2"

headers = {
    "Content-Type": "application/json",
    "User-Agent": "PostmanRuntime/7.49.1",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

# Tests using REAL data from the API
tests = [
    {
        "name": "✅ TEST 1: Location only (known to work)",
        "body": {"limit": 10, "location": ["United States"]}
    },
    {
        "name": "🧪 TEST 2: Specific company from results",
        "body": {"limit": 10, "company_name": ["Top 000"]}
    },
    {
        "name": "🧪 TEST 3: Another company",
        "body": {"limit": 10, "company_name": ["0-One"]}
    },
    {
        "name": "🧪 TEST 4: Industry from results",
        "body": {"limit": 10, "company_industry": "Construction"}
    },
    {
        "name": "🧪 TEST 5: Position from results",
        "body": {"limit": 10, "position": "Director"}
    },
    {
        "name": "🧪 TEST 6: Position + Location",
        "body": {"limit": 10, "position": "Director", "location": ["United States"]}
    },
    {
        "name": "🧪 TEST 7: Company + Location",
        "body": {"limit": 10, "company_name": ["PK-0"], "location": ["United States"]}
    },
    {
        "name": "🧪 TEST 8: Name search",
        "body": {"limit": 10, "name": "Fred"}
    },
    {
        "name": "🧪 TEST 9: Level search",
        "body": {"limit": 10, "level": "Director"}
    },
    {
        "name": "🧪 TEST 10: Multiple filters",
        "body": {
            "limit": 10,
            "position": "Director",
            "company_industry": "Construction",
            "location": ["United States"]
        }
    },
]

def safe_request(test_config, timeout=60):
    """Make request with proper error handling"""
    print(f"\n{'='*80}")
    print(f"{test_config['name']}")
    print(f"{'='*80}")
    print(f"📤 Body: {json.dumps(test_config['body'], indent=2)}")
    
    try:
        start = time.time()
        
        # Create request exactly like working script
        req = requests.Request(
            "GET",
            url,
            data=json.dumps(test_config['body']),
            headers=headers
        )
        prepared = req.prepare()
        
        # Send with session
        session = requests.Session()
        response = session.send(prepared, timeout=timeout)
        
        elapsed = round(time.time() - start, 2)
        
        # Check status code first
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ HTTP Error {response.status_code}")
            print(f"   Response text: {response.text[:500]}")
            return {'success': False, 'error': f'HTTP {response.status_code}'}
        
        # Try to parse JSON
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response")
            print(f"   Response text: {response.text[:500]}")
            return {'success': False, 'error': 'Invalid JSON'}
        
        # Get results
        results = data.get('results', [])
        
        print(f"✅ SUCCESS - {len(results)} leads in {elapsed}s")
        
        if results:
            first = results[0]
            print(f"   📋 Sample Lead:")
            print(f"      Name: {first.get('name')} {first.get('surname')}")
            print(f"      Position: {first.get('position')}")
            print(f"      Company: {first.get('company_name')}")
            print(f"      Location: {first.get('location')}")
        
        return {
            'success': True,
            'count': len(results),
            'time': elapsed,
            'sample': results[0] if results else None
        }
    
    except requests.Timeout:
        print(f"⏱️  TIMEOUT after {timeout}s")
        return {'success': False, 'error': 'timeout'}
    
    except requests.RequestException as e:
        print(f"❌ Request Error: {str(e)}")
        return {'success': False, 'error': str(e)}
    
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

# Run tests
print("🔬 Testing LinkedIn API with Real Data")
print("="*80)

results = []

for i, test in enumerate(tests, 1):
    print(f"\n[TEST {i}/{len(tests)}]")
    result = safe_request(test, timeout=90)  # Increased timeout
    results.append({
        'name': test['name'],
        'body': test['body'],
        'result': result
    })
    
    # Wait between requests to avoid rate limiting
    if i < len(tests):
        print("\n⏳ Waiting 3 seconds before next test...")
        time.sleep(3)

# Summary
print("\n" + "="*80)
print("📊 FINAL SUMMARY")
print("="*80)

successful = [r for r in results if r['result'].get('success')]
failed = [r for r in results if not r['result'].get('success')]

print(f"\n✅ Successful Tests: {len(successful)}/{len(tests)}")
for r in successful:
    print(f"\n   {r['name']}")
    print(f"   Body: {json.dumps(r['body'])}")
    print(f"   Results: {r['result'].get('count', 0)} leads in {r['result'].get('time', 0)}s")

print(f"\n❌ Failed Tests: {len(failed)}/{len(tests)}")
for r in failed:
    print(f"\n   {r['name']}")
    print(f"   Body: {json.dumps(r['body'])}")
    print(f"   Error: {r['result'].get('error', 'unknown')}")

# Patterns analysis
if successful:
    print("\n" + "="*80)
    print("🎯 WORKING PATTERNS ANALYSIS")
    print("="*80)
    
    # Analyze which parameters work
    working_bodies = [r['body'] for r in successful]
    
    all_keys = set()
    for body in working_bodies:
        all_keys.update(body.keys())
    
    print("\n📋 Parameters that worked:")
    for key in sorted(all_keys):
        if key == 'limit':
            continue
        count = sum(1 for body in working_bodies if key in body)
        print(f"   - {key}: appeared in {count}/{len(working_bodies)} successful tests")
    
    # Check if arrays vs strings matter
    print("\n🔍 Format analysis:")
    for r in successful:
        body = r['body']
        for key, value in body.items():
            if key != 'limit':
                value_type = 'array' if isinstance(value, list) else 'string'
                print(f"   - {key}: {value_type} format works")