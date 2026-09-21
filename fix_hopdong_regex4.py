import sys

path = r'd:\DoAnCuNhan\RentalSystem\Areas\Admin\Controllers\HopDongController.cs'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

start_idx = content.find('if (!hasInstallments)')
end_idx = content.find('decimal tienMoiKy =', start_idx)

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + 'if (!hasInstallments)\n                {\n                    int soKy = hopDong.SoKyHan > 0 ? hopDong.SoKyHan : 1;\n\n                    ' + content[end_idx:]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Done replacing exactly by index!')
else:
    print('Could not find indices')
