# run_tests.py
"""
Test runner for Lead Finder System
Execute: python run_tests.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command

def run_all_tests():
    """Run all tests"""
    print("=" * 80)
    print("RUNNING ALL TESTS")
    print("=" * 80)
    
    call_command('test', 'leads.tests', verbosity=2)

def run_model_tests():
    """Run model tests only"""
    print("=" * 80)
    print("RUNNING MODEL TESTS")
    print("=" * 80)
    
    call_command('test', 'leads.tests.test_models', verbosity=2)

def run_service_tests():
    """Run service tests only"""
    print("=" * 80)
    print("RUNNING SERVICE TESTS")
    print("=" * 80)
    
    call_command('test', 'leads.tests.test_services', verbosity=2)

def run_api_tests():
    """Run API filter tests only"""
    print("=" * 80)
    print("RUNNING API FILTER TESTS")
    print("=" * 80)
    
    call_command('test', 'leads.tests.test_api_filters', verbosity=2)

def check_system():
    """Run system checks"""
    print("=" * 80)
    print("RUNNING SYSTEM CHECKS")
    print("=" * 80)
    
    call_command('check')
    print("\n✅ System checks passed!\n")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        
        if test_type == 'models':
            run_model_tests()
        elif test_type == 'services':
            run_service_tests()
        elif test_type == 'api':
            run_api_tests()
        elif test_type == 'check':
            check_system()
        else:
            print(f"Unknown test type: {test_type}")
            print("Usage: python run_tests.py [models|services|api|check]")
    else:
        check_system()
        run_all_tests()