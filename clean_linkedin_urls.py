#!/usr/bin/env python
"""
Script to clean up corrupted LinkedIn URLs in the database.
Fixes URLs that have escaped characters like /u002D and %C3%B3.
"""
import re
import urllib.parse
from leads.models import Lead
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lead_finder.settings')
django.setup()


def clean_linkedin_url(url):
    """Clean a corrupted LinkedIn URL."""
    if not url:
        return url

    # Decode unicode escapes like /u002D
    try:
        # Replace unicode escape sequences
        url = url.encode('utf-8').decode('unicode-escape')
    except:
        pass

    # URL decode characters like %C3%B3
    try:
        url = urllib.parse.unquote(url)
    except:
        pass

    return url


def main():
    """Clean all corrupted LinkedIn URLs."""
    # Find leads with potentially corrupted URLs
    leads_with_urls = Lead.objects.exclude(
        linkedin_url='').exclude(linkedin_url__isnull=True)

    fixed_count = 0
    error_count = 0

    for lead in leads_with_urls:
        original_url = lead.linkedin_url

        # Check if URL contains escaped characters
        if '/u002D' in original_url or '%' in original_url:
            cleaned_url = clean_linkedin_url(original_url)

            if cleaned_url != original_url:
                try:
                    lead.linkedin_url = cleaned_url
                    lead.save()
                    fixed_count += 1
                    print(f"✅ Fixed: {lead.full_name}")
                    print(f"   Before: {original_url}")
                    print(f"   After:  {cleaned_url}\n")
                except Exception as e:
                    error_count += 1
                    print(f"❌ Error fixing {lead.full_name}: {str(e)}\n")

    print(f"\n{'='*60}")
    print(f"✅ Fixed {fixed_count} LinkedIn URLs")
    if error_count > 0:
        print(f"❌ {error_count} errors encountered")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
