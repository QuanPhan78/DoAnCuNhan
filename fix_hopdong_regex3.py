import sys

path = r'd:\DoAnCuNhan\RentalSystem\Areas\Admin\Controllers\HopDongController.cs'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

import re

# We will just replace the whole block from "bool hasInstallments" to "decimal tienMoiKy"
old_block_pattern = r'bool hasInstallments = await _context\.KyHanThanhToans\.AnyAsync\(k => k\.MaHopDong == id\);\s*if \(\!hasInstallments\)\s*\{\s*int soKy = hopDong\.SoKyHan > 0 \? hopDong\.SoKyHan : 1;\s*else\s*\{\s*// Nếu không chỉ định -> tự chia theo 30 ngày\s*var totalDays = \(hopDong\.NgayKetThuc - hopDong\.NgayBatDau\)\.TotalDays;\s*soKy = \(int\)Math\.Ceiling\(totalDays / 30\.0\);\s*if \(soKy <= 0\) soKy = 1;\s*\}\s*decimal tienMoiKy'

new_block = '''bool hasInstallments = await _context.KyHanThanhToans.AnyAsync(k => k.MaHopDong == id);
                if (!hasInstallments)
                {
                    int soKy = hopDong.SoKyHan > 0 ? hopDong.SoKyHan : 1;

                    decimal tienMoiKy'''

content = re.sub(old_block_pattern, new_block, content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
