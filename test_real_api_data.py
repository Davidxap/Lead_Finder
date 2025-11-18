# test_real_api_data.py
import requests
import json
import time
import gzip

url = "https://linkedin.programando.io/fetch_lead2"

headers = {
    "Content-Type": "application/json",
    "User-Agent": "PostmanRuntime/7.49.1",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

# ALL FILTERS AS ARRAYS (based on API error message showing 'level' must be list)
tests = [
    {
        "name": "TEST 1: Location array",
        "body": {"limit": 10, "location": ["United States"]}
    },
    {
        "name": "TEST 2: Position array",
        "body": {"limit": 10, "position": ["Director"]}
    },
    {
        "name": "TEST 3: Company array",
        "body": {"limit": 10, "company_name": ["Top 000"]}
    },
    {
        "name": "TEST 4: Industry array",
        "body": {"limit": 10, "company_industry": ["Construction"]}
    },
    {
        "name": "TEST 5: Name array",
        "body": {"limit": 10, "name": ["Fred"]}
    },
    {
        "name": "TEST 6: Level array (CRITICAL - failed as string before)",
        "body": {"limit": 10, "level": ["Director"]}
    },
    {
        "name": "TEST 7: Position + Location arrays",
        "body": {"limit": 10, "position": ["Director"], "location": ["United States"]}
    },
    {
        "name": "TEST 8: Industry + Location arrays",
        "body": {"limit": 10, "company_industry": ["Construction"], "location": ["United States"]}
    },
]

def safe_request(test_config, timeout=90):
    """Make request with GZIP decompression handling"""
    print(f"\n{'='*80}")
    print(f"{test_config['name']}")
    print(f"{'='*80}")
    print(f"Request Body: {json.dumps(test_config['body'], indent=2)}")
    
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
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Encoding: {response.headers.get('Content-Encoding', 'none')}")
        
        if response.status_code != 200:
            print(f"FAILED - HTTP Error {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error Details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Response Text: {response.text[:200]}")
            return {'success': False, 'error': f'HTTP {response.status_code}'}
        
        # Handle GZIP decompression
        try:
            # First try normal JSON decode
            data = response.json()
        except json.JSONDecodeError:
            # Manual decompression
            print("Normal JSON decode failed, attempting manual decompression...")
            content = response.content
            
            # Check if GZIP (magic number check)
            if content[:2] == b'\x1f\x8b':
                print("Detected GZIP compression, decompressing...")
                content = gzip.decompress(content)
            
            # Decode and parse
            text = content.decode('utf-8')
            data = json.loads(text)
        
        results = data.get('results', [])
        
        print(f"SUCCESS - {len(results)} leads in {elapsed}s")
        
        if results:
            first = results[0]
            print(f"Sample Lead:")
            print(f"  Name: {first.get('name')} {first.get('surname')}")
            print(f"  Position: {first.get('position')}")
            print(f"  Company: {first.get('company_name')}")
            print(f"  Location: {first.get('location')}")
        
        return {'success': True, 'count': len(results), 'time': elapsed}
    
    except requests.Timeout:
        print(f"TIMEOUT after {timeout}s")
        return {'success': False, 'error': 'timeout'}
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

# Run tests
print("Testing LinkedIn API with Array Formats and GZIP Handling")
print("="*80)

results = []
for i, test in enumerate(tests, 1):
    print(f"\n[TEST {i}/{len(tests)}]")
    result = safe_request(test)
    results.append({'name': test['name'], 'result': result})
    
    if i < len(tests):
        print("\nWaiting 3 seconds before next test...")
        time.sleep(3)

# Summary
print("\n" + "="*80)
print("FINAL SUMMARY")
print("="*80)

successful = [r for r in results if r['result'].get('success')]
failed = [r for r in results if not r['result'].get('success')]

print(f"\nSuccessful Tests: {len(successful)}/{len(tests)}")
for r in successful:
    print(f"  {r['name']}: {r['result'].get('count', 0)} leads in {r['result'].get('time', 0)}s")

print(f"\nFailed Tests: {len(failed)}/{len(tests)}")
for r in failed:
    print(f"  {r['name']}: {r['result'].get('error', 'unknown')}")

if successful:
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    print("The following filter configurations work:")
    for r in successful:
        print(f"  - {r['name']}")