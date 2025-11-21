"""
Django shell script to clean corrupted LinkedIn URLs.
Run with: python manage.py shell < clean_urls_shell.py
"""
from leads.models import Lead
import urllib.parse

# Find leads with escaped characters
leads = Lead.objects.filter(
    linkedin_url__contains='/u002D') | Lead.objects.filter(linkedin_url__contains='%')

fixed_count = 0
for lead in leads:
    original = lead.linkedin_url
    # Decode unicode escapes
    try:
        cleaned = original.encode().decode('unicode-escape')
    except:
        cleaned = original
    # URL decode
    try:
        cleaned = urllib.parse.unquote(cleaned)
    except:
        pass

    if cleaned != original:
        lead.linkedin_url = cleaned
        lead.save()
        fixed_count += 1
        print(f"Fixed: {lead.full_name} - {cleaned}")

print(f"\n✅ Fixed {fixed_count} URLs")
