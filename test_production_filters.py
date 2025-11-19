# test_production_filters.py
"""
Production Filter Testing Script
Tests actual API calls with real filters
Execute: python test_production_filters.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from leads.services.linkedin_api import LinkedInAPIService


def test_filter(name, filters):
    """Test a specific filter configuration"""
    print("\n" + "="*80)
    print(f"TEST: {name}")
    print("="*80)
    print(f"Filters: {filters}")
    
    api_service = LinkedInAPIService()
    
    # Build request body
    body = api_service._build_request_body(filters)
    print(f"API Body: {body}")
    
    # Fetch leads (will use cache or API)
    try:
        result = api_service.fetch_leads(filters)
        
        if result['success']:
            count = len(result['results'])
            is_mock = result.get('is_mock', False)
            cached = result.get('cached', False)
            
            print(f"✅ SUCCESS")
            print(f"   Results: {count} leads")
            print(f"   Source: {'MOCK' if is_mock else 'API'}")
            print(f"   Cached: {cached}")
            
            if count > 0:
                first = result['results'][0]
                parsed = api_service.parse_lead_data(first)
                print(f"\n   Sample Lead:")
                print(f"   - Name: {parsed['full_name']}")
                print(f"   - Title: {parsed['current_title']}")
                print(f"   - Company: {parsed['current_company']}")
                print(f"   - Location: {parsed['location']}")
        else:
            print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")


def main():
    """Run all filter tests"""
    print("\n" + "="*80)
    print("PRODUCTION FILTER TESTING")
    print("Testing LinkedIn API with real filters")
    print("="*80)
    
    # Test 1: Position filter (PRIMARY)
    test_filter(
        "1. Position Filter (Engineer)",
        {'title': 'Engineer', 'limit': 10}
    )
    
    # Test 2: Seniority filter (PRIMARY)
    test_filter(
        "2. Seniority Filter (Manager)",
        {'seniority_level': 'manager', 'limit': 10}
    )
    
    # Test 3: Industry filter (PRIMARY)
    test_filter(
        "3. Industry Filter (Technology)",
        {'industry': 'Technology', 'limit': 10}
    )
    
    # Test 4: Position + Company (CLIENT-SIDE)
    test_filter(
        "4. Position + Company Filter",
        {'title': 'Director', 'company': 'Google', 'limit': 10}
    )
    
    # Test 5: Multiple filters (PRIORITY TESTING)
    test_filter(
        "5. Multiple Filters (Position wins)",
        {
            'title': 'Director',
            'seniority_level': 'senior',
            'industry': 'Technology',
            'limit': 10
        }
    )
    
    # Test 6: Client-side filters only
    test_filter(
        "6. Client-Side Filters (Name + Location)",
        {'name': 'John', 'location': 'United States', 'limit': 50}
    )
    
    print("\n" + "="*80)
    print("FILTER TESTING COMPLETED")
    print("="*80)
    print("\nNOTE: If using MOCK data, API might be unavailable.")
    print("Check logs for actual API calls and responses.")


if __name__ == '__main__':
    main()