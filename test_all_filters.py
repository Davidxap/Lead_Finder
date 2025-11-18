# test_all_filters.py
import requests
import json
import time

url = "https://linkedin.programando.io/fetch_lead2"

headers = {
    "Content-Type": "application/json",
    "User-Agent": "PostmanRuntime/7.49.1"
}

# Using REAL data from the API you shared
tests = [
    {
        "name": "1. Only Location (United States)",
        "body": {"limit": 10, "location": ["United States"]}
    },
    {
        "name": "2. Only Level (Senior)",
        "body": {"limit": 10, "level": ["Senior"]}
    },
    {
        "name": "3. Only Level (Director)",
        "body": {"limit": 10, "level": ["Director"]}
    },
    {
        "name": "4. Only Level (Specialist)",
        "body": {"limit": 10, "level": ["Specialist"]}
    },
    {
        "name": "5. Only Position (Director)",
        "body": {"limit": 10, "position": ["Director"]}
    },
    {
        "name": "6. Only Industry (Construction)",
        "body": {"limit": 10, "company_industry": ["Construction"]}
    },
    {
        "name": "7. Only Company (Top 000)",
        "body": {"limit": 10, "company_name": ["Top 000"]}
    },
    {
        "name": "8. Only Company (PK-0)",
        "body": {"limit": 10, "company_name": ["PK-0"]}
    },
    {
        "name": "9. Only Company (Various Companies)",
        "body": {"limit": 10, "company_name": ["Various Companies"]}
    },
    {
        "name": "10. Location + Position",
        "body": {"limit": 10, "location": ["United States"], "position": ["Director"]}
    },
    {
        "name": "11. Location + Industry",
        "body": {"limit": 10, "location": ["United States"], "company_industry": ["Construction"]}
    },
    {
        "name": "12. Location + Level (FAILING BEFORE)",
        "body": {"limit": 10, "location": ["United States"], "level": ["Senior"]}
    },
    {
        "name": "13. Position + Level",
        "body": {"limit": 10, "position": ["Director"], "level": ["Director"]}
    },
    {
        "name": "14. Position + Industry",
        "body": {"limit": 10, "position": ["Director"], "company_industry": ["Construction"]}
    },
    {
        "name": "15. Company + Location",
        "body": {"limit": 10, "company_name": ["PK-0"], "location": ["United States"]}
    },
    {
        "name": "16. Location + Position + Industry",
        "body": {"limit": 10, "location": ["United States"], "position": ["Director"], "company_industry": ["Construction"]}
    },
]

results = []

for i, test in enumerate(tests, 1):
    print(f"\n{'='*80}")
    print(f"[{i}/{len(tests)}] {test['name']}")
    print(f"{'='*80}")
    print(f"Body: {json.dumps(test['body'])}")
    
    try:
        response = requests.get(
            url,
            data=json.dumps(test['body']),
            headers=headers,
            timeout=60
        )
        
        status = response.status_code
        print(f"Status: {status}")
        
        if status == 200:
            data = response.json()
            count = len(data.get('results', []))
            print(f"SUCCESS - {count} results")
            results.append({'test': test['name'], 'status': 'SUCCESS', 'count': count})
        else:
            print(f"FAILED - HTTP {status}")
            print(f"Response preview: {response.text[:200]}")
            results.append({'test': test['name'], 'status': f'HTTP {status}'})
            
    except requests.Timeout:
        print("TIMEOUT (>60s)")
        results.append({'test': test['name'], 'status': 'TIMEOUT'})
    except Exception as e:
        print(f"ERROR: {e}")
        results.append({'test': test['name'], 'status': f'ERROR: {str(e)}'})
    
    if i < len(tests):
        print("Waiting 2 seconds...")
        time.sleep(2)

print("\n" + "="*80)
print("FINAL SUMMARY")
print("="*80)

successful = [r for r in results if r['status'] == 'SUCCESS']
failed = [r for r in results if r['status'] != 'SUCCESS']
timeouts = [r for r in results if r['status'] == 'TIMEOUT']
errors = [r for r in results if r['status'].startswith('HTTP') or r['status'].startswith('ERROR')]

print(f"\nSuccessful: {len(successful)}/{len(tests)}")
for r in successful:
    print(f"  {r['test']}: {r.get('count', 0)} results")

print(f"\nTimeouts: {len(timeouts)}/{len(tests)}")
for r in timeouts:
    print(f"  {r['test']}")

print(f"\nErrors: {len(errors)}/{len(tests)}")
for r in errors:
    print(f"  {r['test']}: {r['status']}")

print("\n" + "="*80)
print("WORKING FILTER COMBINATIONS:")
print("="*80)
for r in successful:
    print(f"  - {r['test']}")

if timeouts:
    print("\n" + "="*80)
    print("FILTERS THAT CAUSE TIMEOUT (avoid these):")
    print("="*80)
    for r in timeouts:
        print(f"  - {r['test']}")

if errors:
    print("\n" + "="*80)
    print("FILTERS THAT CAUSE ERRORS (avoid these):")
    print("="*80)
    for r in errors:
        print(f"  - {r['test']}")