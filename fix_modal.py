import re

# Leer el archivo
with open('leads/templates/leads/search.html', 'r', encoding='utf-8') as f:
    content = f.read()

# El problema: después de la línea 390, hay una línea en blanco (391) que no debería estar
# Buscar el patrón específico donde está el cierre prematuro del div
# Patrón: después de </small> y antes de <div class="mb-3">
# hay un </div> seguido de línea en blanco que debemos eliminar

pattern = r'(</small>\r?\n)(\s*</div>\r?\n)(\r?\n)(\s*<div class="mb-3">\r?\n\s*<label for="notesTextarea")'
replacement = r'\1\3\4'

# Aplicarel fix
fixed_content = re.sub(pattern, replacement, content)

# Verificar que se hizo el cambio
if fixed_content != content:
    with open('leads/templates/leads/search.html', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    print("✅ Fixed: Removed extra closing div tag at line 391")
    print("Modal structure is now correct")
else:
    print("⚠️  Pattern not found or already fixed")
