# -*- coding: utf-8 -*-
import os, sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

figs = [
    "figures/hinh_2_2_2_2_1_activity_dat_thue_inventory.png",
    "figures/hinh_3_4_2_2_sequence_3lop_dat_thue_inventory.png",
    "figures/hinh_3_4_3_2_sequence_3lop_thanh_toan_vietqr.png",
    "figures/hinh_3_4_3_3_collab_3lop_thanh_toan_vietqr.png",
    "figures/hinh_3_4_4_2_sequence_3lop_ban_giao_ky_so.png",
    "figures/hinh_3_4_6_3_collab_3lop_gia_han_cong_no.png"
]

print("=== CHECKING FIGURE IMAGE FILES ===")
for f in figs:
    if os.path.exists(f):
        size = os.path.getsize(f)
        try:
            im = Image.open(f)
            w, h = im.size
            print(f"[EXISTS] {f}: size={size:,} bytes | {w}x{h} px | format={im.format}")
        except Exception as e:
            print(f"[CORRUPT] {f}: size={size} bytes | error={e}")
    else:
        print(f"[MISSING] {f}")
