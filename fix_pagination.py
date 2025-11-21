#!/usr/bin/env python
"""Fix pagination in search.html safely."""
import re

# Read the file
with open(r'leads\templates\leads\search.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The problem pattern: "{% elif ... %} <li" on the same line (line 272)
# We need to find and replace this specific pattern

# Pattern to fix:  {% elif num > page_obj.number|add:'-3' and num < page_obj.number|add:'3' %} <li
# Should be:       {% elif num > page_obj.number|add:'-3' and num < page_obj.number|add:'3' %}\n<li

pattern = r"({%\s*elif\s+num\s*>\s*page_obj\.number\|add:'-3'\s+and\s+num\s*<\s*page_obj\.number\|add:'3'\s*%})\s*<li"
replacement = r"\1\n                                <li"

content_fixed = re.sub(pattern, replacement, content)

# Write the fixed content back
with open(r'leads\templates\leads\search.html', 'w', encoding='utf-8') as f:
    f.write(content_fixed)

print("✅ Pagination fixed successfully!")
print("The {% elif %} tag is now on its own line.")
