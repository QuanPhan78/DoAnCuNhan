import re

path = r'd:\DoAnCuNhan\RentalSystem\Models\AppModels.cs'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'public int SoKyHan { get; set; } = 1;' not in content:
    content = content.replace(
        'public int TrangThai { get; set; }',
        'public int TrangThai { get; set; } \n        public int SoKyHan { get; set; } = 1;'
    )
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Added SoKyHan to AppModels.cs')
else:
    print('Already has SoKyHan')
