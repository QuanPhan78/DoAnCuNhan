import os, sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open('tools/build_master_thesis.py', 'r', encoding='utf-8') as f:
    content = f.read()

codes_ch2 = ['2.2.2.1', '2.2.2.2', '2.2.2.3', '2.2.2.4', '2.2.2.5', '2.2.2.6', '2.2.2.7']
slug_map = {
    '2.2.2.1': 'dang_ky_xac_thuc',
    '2.2.2.2': 'dat_thue_may',
    '2.2.2.3': 'thanh_toan_vietqr',
    '2.2.2.4': 'ban_giao_ky_so',
    '2.2.2.5': 'bao_tri_su_co',
    '2.2.2.6': 'gia_han_cong_no',
    '2.2.2.7': 'tra_may_hoan_coc'
}

missing = []
existing = []
for c in codes_ch2:
    for diag in ['1_activity', '2_sequence', '3_collaboration']:
        c_str = c.replace('.', '_')
        slug = slug_map[c]
        img = f'figures/hinh_{c_str}_{diag}_{slug}.png'
        if not os.path.exists(img):
            missing.append(img)
        else:
            existing.append(img)

slug_map_ch3 = {
    '3.4.1': 'dang_ky_xac_thuc',
    '3.4.2': 'dat_thue_may',
    '3.4.3': 'thanh_toan_vietqr',
    '3.4.4': 'ban_giao_ky_so',
    '3.4.5': 'bao_tri_su_co',
    '3.4.6': 'gia_han_cong_no',
    '3.4.7': 'tra_may_hoan_coc'
}
for c, slug in slug_map_ch3.items():
    for diag in ['1_bce', '2_sequence', '3_collaboration']:
        c_str = c.replace('.', '_')
        img = f'figures/hinh_{c_str}_{diag}_{slug}.png'
        if not os.path.exists(img):
            missing.append(img)
        else:
            existing.append(img)

for m in re.finditer(r'[\'\"](figures/[^\'\"]+\.png)[\'\"]', content):
    img = m.group(1)
    if not os.path.exists(img):
        missing.append(img)
    else:
        existing.append(img)

print(f'Total figures checked: {len(missing) + len(existing)}')
print(f'Missing figures count: {len(set(missing))}')
for m in sorted(set(missing)):
    print('  MISSING:', m)
