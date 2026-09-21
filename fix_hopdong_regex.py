import re

path = r'd:\DoAnCuNhan\RentalSystem\Areas\Admin\Controllers\HopDongController.cs'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Create
pattern_create = r'// Lưu số kỳ hạn vào GhiChu tạm để dùng khi Giao máy\s*if \(SoKyHan > 1\)\s*\{\s*hd\.GhiChu = \(string\.IsNullOrEmpty\(hd\.GhiChu\) \? "" : hd\.GhiChu \+ " \| "\) \+ \$"\[SoKy:\{SoKyHan\}\]";\s*\}'
content = re.sub(pattern_create, 'hd.SoKyHan = SoKyHan > 0 ? SoKyHan : 1;', content)

# Replace UpdateStatus
pattern_update = r'// Đọc số kỳ từ GhiChu \(nếu Admin đã chỉ định lúc tạo đơn\)\s*int soKy = 1;\s*var ghiChu = hopDong\.GhiChu \?\? "";\s*var match = System\.Text\.RegularExpressions\.Regex\.Match\(ghiChu, @"\\\[SoKy:\\(\d\+\)\\\]"\);\s*if \(match\.Success && int\.TryParse\(match\.Groups\[1\]\.Value, out int parsedSoKy\) && parsedSoKy > 0\)\s*\{\s*soKy = parsedSoKy;\s*\}\s*else\s*\{\s*// Nếu không chỉ định -> tự chia theo 30 ngày\s*var totalDays = \(hopDong\.NgayKetThuc - hopDong\.NgayBatDau\)\.TotalDays;\s*soKy = \(int\)Math\.Ceiling\(totalDays / 30\.0\);\s*if \(soKy <= 0\) soKy = 1;\s*\}'
content = re.sub(pattern_update, 'int soKy = hopDong.SoKyHan > 0 ? hopDong.SoKyHan : 1;', content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done HopDong Regex Fix')
