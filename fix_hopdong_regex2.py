import sys

path = r'd:\DoAnCuNhan\RentalSystem\Areas\Admin\Controllers\HopDongController.cs'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if '// Lưu số kỳ hạn vào GhiChu tạm để dùng khi Giao máy' in line:
        skip = True
        new_lines.append('            hd.SoKyHan = SoKyHan > 0 ? SoKyHan : 1;\n')
        continue
    
    if skip and '}' in line and 'hd.GhiChu =' not in line:
        skip = False
        continue
        
    if skip:
        continue
        
    new_lines.append(line)

lines = new_lines
new_lines = []
skip = False
brace_count = 0

for line in lines:
    if '// Đọc số kỳ từ GhiChu' in line:
        skip = True
        new_lines.append('                    int soKy = hopDong.SoKyHan > 0 ? hopDong.SoKyHan : 1;\n')
        continue
        
    if skip:
        if 'else' in line:
            pass
        if '{' in line:
            brace_count += line.count('{')
        if '}' in line:
            brace_count -= line.count('}')
            if brace_count <= 0 and 'else' not in line:
                skip = False
        continue
        
    new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Done!')
