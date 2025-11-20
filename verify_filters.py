

import traceback


def run_tests():
    # Patch __init__ to avoid requests dependency issues in test env
    original_init = LinkedInAPIService.__init__
    LinkedInAPIService.__init__ = lambda self: None

    try:
        print("Instantiating service (mocked init)...")
        service = LinkedInAPIService()
        # Manually set logger if needed, though it's global in the module
        print("Service instantiated.")
    except Exception:
        with open('error.log', 'w') as f:
            traceback.print_exc(file=f)
        return

    # Mock Data
    leads = [
        {
            'name': 'John', 'surname': 'Doe', 'position': 'Software Engineer',
            'company_name': 'Tech Corp', 'location': 'United States', 'region': 'Northern America',
            'level': 'Senior', 'company_headcount': '1001-5000', 'company_industry': 'Technology'
        },
        {
            'name': 'Jane', 'surname': 'Smith', 'position': 'Product Manager',
            'company_name': 'Biz Inc', 'location': 'United Kingdom', 'region': 'Europe',
            'level': 'Mid', 'company_headcount': '51-200', 'company_industry': 'Business'
        },
        {
            'name': 'Carlos', 'surname': 'Garcia', 'position': 'CTO',
            'company_name': 'Startup IO', 'location': 'Spain', 'region': 'Southern Europe',
            'level': 'C-Level', 'company_headcount': '11-50', 'company_industry': 'Technology'
        },
        {
            'name': 'Anna', 'surname': 'Muller', 'position': 'Director of Sales',
            'company_name': 'Global Sales', 'location': 'Germany', 'region': 'Western Europe',
            'level': 'Director', 'company_headcount': '5001-10000', 'company_industry': 'Sales'
        }
    ]

    print(f"--- Starting Filter Tests with {len(leads)} mock leads ---\n")

    # Test 1: Name Filter (Partial & Case Insensitive)
    filters = {'name': 'john'}
    results = service.filter_leads_locally(leads, filters)
    assert len(results) == 1, f"Test 1 Failed: Expected 1, got {len(results)}"
    assert results[0]['name'] == 'John', "Test 1 Failed: Wrong lead found"
    print("✅ Test 1 Passed: Name Filter (Simple)")

    # Test 2: Name Filter (Token based)
    filters = {'name': 'doe john'}
    results = service.filter_leads_locally(leads, filters)
    assert len(results) == 1, f"Test 2 Failed: Expected 1, got {len(results)}"
    print("✅ Test 2 Passed: Name Filter (Token Swap)")

    # Test 3: Title Filter
    filters = {'title': 'engineer'}
    results = service.filter_leads_locally(leads, filters)
    assert len(results) == 1, f"Test 3 Failed: Expected 1, got {len(results)}"
    assert results[0]['position'] == 'Software Engineer', "Test 3 Failed: Wrong lead found"
    print("✅ Test 3 Passed: Title Filter")

    # Test 4: Company Filter
    filters = {'company': 'tech'}
    results = service.filter_leads_locally(leads, filters)
    assert len(results) == 1, f"Test 4 Failed: Expected 1, got {len(results)}"
    print("✅ Test 4 Passed: Company Filter")

    # Test 5: Region Filter (Exact Region)
    filters = {'region': 'europe'}
    results = service.filter_leads_locally(leads, filters)
    # Should match Jane (Europe), Carlos (Southern Europe), Anna (Western Europe)
    assert len(results) == 3, f"Test 5 Failed: Expected 3, got {len(results)}"
    print("✅ Test 5 Passed: Region Filter (Broad)")

    # Test 6: Region Filter (Matching Location/Country)
    filters = {'region': 'spain'}
    results = service.filter_leads_locally(leads, filters)
    assert len(results) == 1, f"Test 6 Failed: Expected 1, got {len(results)}"
    assert results[0]['location'] == 'Spain', "Test 6 Failed: Wrong lead found"
    print("✅ Test 6 Passed: Region Filter (Matches Location)")

    # Test 7: Combined Filters (Name + Region)
    filters = {'name': 'carlos', 'region': 'europe'}
    results = service.filter_leads_locally(leads, filters)
    assert len(results) == 1, f"Test 7 Failed: Expected 1, got {len(results)}"
    assert results[0]['name'] == 'Carlos', "Test 7 Failed: Wrong lead found"
    print("✅ Test 7 Passed: Combined Filters (Name + Region)")

    # Test 8: Combined Filters (Title + Company)
    filters = {'title': 'manager', 'company': 'biz'}
    results = service.filter_leads_locally(leads, filters)
    assert len(results) == 1, f"Test 8 Failed: Expected 1, got {len(results)}"
    print("✅ Test 8 Passed: Combined Filters (Title + Company)")

    # Test 9: No Results
    filters = {'name': 'NonExistent'}
    results = service.filter_leads_locally(leads, filters)
    assert len(results) == 0, f"Test 9 Failed: Expected 0, got {len(results)}"
    print("✅ Test 9 Passed: No Results")

    print("\n🎉 All Tests Passed Successfully!")


if __name__ == "__main__":
    run_tests()
