import re

path = r'd:\DoAnCuNhan\RentalSystem\Models\AppModels.cs'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Revert the blind replacement first
content = content.replace(' \n        public int SoKyHan { get; set; } = 1;', '')

# Now target exactly HopDong
pattern = r'(public class HopDong \{[\s\S]*?public int TrangThai \{ get; set; \})'
match = re.search(pattern, content)
if match:
    content = content[:match.end()] + ' \n        public int SoKyHan { get; set; } = 1;' + content[match.end():]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed properly')
else:
    print('Not found')
