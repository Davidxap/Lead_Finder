#!/usr/bin/env python
"""Fix pagination {{ num }} display bug."""
import re

# Read the file
with open(r'leads\templates\leads\search.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the split {{ num }} across two lines
# Pattern: href="...">{{NEWLINE num }}
pattern = r'(href=\"\?page=\{\{ num \}\}\{% for key, value in request\.GET\.items %\}\{% if key != \'page\' %\}&\{\{ key \}\}=\{\{ value \}\}\{% endif %\}\{% endfor %\}\">)\{\{[\r\n\s]+num \}\}'
replacement = r'\1{{ num }}'

content_fixed = re.sub(pattern, replacement, content)

# Write the fixed content back
with open(r'leads\templates\leads\search.html', 'w', encoding='utf-8') as f:
    f.write(content_fixed)

print("✅ Pagination {{ num }} fixed!")
