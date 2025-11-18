# test_exact_postman_fixed.py
import requests
import json
import brotli

url = "https://linkedin.programando.io/fetch_lead2"

body = {
    "limit": 10,
    "location": ["United States"]
}

# Headers exactos de Postman SIN Accept-Encoding
# Esto evita que requests intente descomprimir automáticamente
headers = {
    "Content-Type": "application/json",
    "User-Agent": "PostmanRuntime/7.49.1",
    "Accept": "*/*",
    "Cache-Control": "no-cache",
    "Host": "linkedin.programando.io",
    "Connection": "keep-alive"
}

print("Testing WITHOUT Accept-Encoding (let server send uncompressed)")
print("="*80)

session = requests.Session()

# Disable automatic decompression
session.headers.update(headers)

response = session.get(
    url,
    data=json.dumps(body),
    stream=True,  # Get raw response
    timeout=30
)

print(f"Status: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")
print(f"Content-Encoding: {response.headers.get('Content-Encoding')}")

if response.status_code == 200:
    # Get raw content without decompression
    raw_content = response.raw.read()
    
    print(f"Raw content length: {len(raw_content)}")
    print(f"First 20 bytes: {raw_content[:20]}")
    
    # Check if it's Brotli compressed
    encoding = response.headers.get('Content-Encoding')
    
    try:
        if encoding == 'br':
            print("Manually decompressing Brotli...")
            decompressed = brotli.decompress(raw_content)
            data = json.loads(decompressed.decode('utf-8'))
        else:
            # Try to parse as-is
            data = json.loads(raw_content.decode('utf-8'))
        
        results = data.get('results', [])
        print(f"\nSUCCESS - {len(results)} results")
        
        if results:
            print(f"\nFirst lead:")
            print(f"  Name: {results[0]['name']} {results[0]['surname']}")
            print(f"  Position: {results[0]['position']}")
            print(f"  Company: {results[0]['company_name']}")
            
    except Exception as e:
        print(f"Error processing response: {e}")
        print(f"Trying alternative method...")
        
        # Alternative: force response.content to get decoded version
        try:
            data = response.json()
            results = data.get('results', [])
            print(f"\nSUCCESS (alternative method) - {len(results)} results")
        except Exception as e2:
            print(f"Alternative also failed: {e2}")
else:
    print(f"FAILED - Status {response.status_code}")
    print(response.text[:300])