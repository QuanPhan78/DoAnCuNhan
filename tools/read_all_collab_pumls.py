# -*- coding: utf-8 -*-
import os, sys

sys.stdout.reconfigure(encoding='utf-8')

puml_files = [
    "diagrams/plantuml/hinh_3_4_1_3_collab_3lop_dang_ky_xac_thuc.puml",
    "diagrams/plantuml/hinh_3_4_2_3_collab_3lop_dat_thue_inventory.puml",
    "diagrams/plantuml/hinh_3_4_3_3_collab_3lop_thanh_toan_vietqr.puml",
    "diagrams/plantuml/hinh_3_4_4_3_collab_3lop_ban_giao_ky_so.puml",
    "diagrams/plantuml/hinh_3_4_5_3_collab_3lop_bao_tri_su_co.puml",
    "diagrams/plantuml/hinh_3_4_6_3_collab_3lop_gia_han_cong_no.puml",
    "diagrams/plantuml/hinh_3_4_7_3_collab_3lop_tra_may_hoan_coc.puml",
]

for p in puml_files:
    print(f"\n{'='*20} {os.path.basename(p)} {'='*20}")
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            print(f.read())
    else:
        print("FILE NOT FOUND")
