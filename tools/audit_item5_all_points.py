# -*- coding: utf-8 -*-
"""
Auditing the 5 items in the user's feedback across both:
- KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx (Master)
- BỘ CÔNG THƯƠNG.docx (Old file)
- tools/build_master_thesis.py (Generator code)
"""
import sys, os, docx, re

sys.stdout.reconfigure(encoding='utf-8')

master_path = 'KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx'
old_path = 'BỘ CÔNG THƯƠNG.docx'

def audit_doc(file_path, label):
    print(f"\n{'='*20} AUDITING {label}: {file_path} {'='*20}")
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    doc = docx.Document(file_path)
    
    # --- 1. Mojibake characters ---
    mojibake_pat = re.compile(r'[¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ]{10,}')
    mojibake_found = []
    for i, p in enumerate(doc.paragraphs):
        if mojibake_pat.search(p.text) or '¡¢£¤¥' in p.text:
            mojibake_found.append((i+1, p.text[:80]))
    print(f"\n1. Mojibake strings found: {len(mojibake_found)}")
    for pnum, snippet in mojibake_found[:5]:
        print(f"   P#{pnum}: {snippet}")

    # --- 2. Vietnamese accents ---
    # Pos 1: Bang dac ta use case
    p1_found = [p.text for p in doc.paragraphs if 'Bang dac ta' in p.text or 'tir dien dir lieu' in p.text]
    print(f"\n2.1 Bang dac ta / tir dien dir lieu: {len(p1_found)} matches")
    for s in p1_found[:3]:
        print(f"   {s[:80]}")

    # Pos 2: Bang dac ta quy trinh nghiep v / Ngi dung
    p2_found = [p.text for p in doc.paragraphs if 'Bang dac ta quy trinh' in p.text or 'Ngi dung quy trinh' in p.text or 'Luong syt' in p.text]
    # Also check tables
    t2_found = []
    for t_idx, t in enumerate(doc.tables):
        for r in t.rows:
            for c in r.cells:
                if 'Ngi dung' in c.text or 'Luong syt' in c.text or 'Bang dac ta quy trinh' in c.text:
                    t2_found.append((t_idx, c.text[:60]))
    print(f"2.2 Bang dac ta quy trinh (Pos 2): {len(p2_found)} in P, {len(t2_found)} in Tables")

    # Pos 3: Garbage numbers 3.1.1.1.1.1.1.1...
    p3_found = [p.text for p in doc.paragraphs if re.search(r'(3\.1\.1\.1\.1|1\.1\.1\.1\.1\.1\.1)', p.text)]
    print(f"2.3 Garbage numbers (3.1.1.1.1...): {len(p3_found)} matches")
    for s in p3_found[:3]:
        print(f"   {s[:80]}")

    # Pos 4: 4.2. 4: So do may trang thai biu dien
    p4_found = [p.text for p in doc.paragraphs if 'So do may trang thai biu dien' in p.text or 'biu dien vong doi' in p.text]
    print(f"2.4 Caption 4.2.4 without accents: {len(p4_found)} matches")
    for s in p4_found[:3]:
        print(f"   {s[:80]}")

    # --- 3. Database merged text ---
    db_errors = ['MaVaiTroint', 'TenVaiTronvarchar', 'MoTanvarchar', 'TrangThaibit', 'TamDungTinhTie', 'MaNhanVienKyT', 'MoTaLoinvarchar', 'MaGiaoDichNga']
    db_found = []
    for t_idx, t in enumerate(doc.tables):
        for r_idx, r in enumerate(t.rows):
            for c_idx, c in enumerate(r.cells):
                for err in db_errors:
                    if err in c.text:
                        db_found.append((t_idx, err, c.text[:50]))
    print(f"\n3. DB merged text errors: {len(db_found)} matches")
    for t_idx, err, snip in db_found[:5]:
        print(f"   Table {t_idx} - {err}: {snip}")

    # --- 4. Missing images / broken figures ---
    # Check paragraphs with 'Hình 2.2.2.2. 1' or 'Hình 2.2.2.2.1'
    fig_check = ['2.2.2.2. 1', '2.2.2.2.1', '3.4.2. 2', '3.4.2.2', '3.4.3. 2', '3.4.3. 3', '3.4.4. 2', '3.4.6. 3']
    print("\n4. Figure checks:")
    for fig in fig_check:
        matches = [(i+1, p.text) for i, p in enumerate(doc.paragraphs) if f'Hình {fig}' in p.text]
        for pnum, txt in matches:
            # Check if previous paragraph has an inline shape / image
            has_prev_img = False
            if pnum > 1:
                prev_p = doc.paragraphs[pnum - 2] # 0-indexed is pnum-2
                if 'drawing' in prev_p._element.xml or 'blip' in prev_p._element.xml:
                    has_prev_img = True
            print(f"   Fig '{fig}' at P#{pnum}: has_prev_img={has_prev_img} | text='{txt[:60]}'")

    # --- 5. References check (aspxnet) ---
    p5_found = [p.text for p in doc.paragraphs if 'aspxnet' in p.text]
    print(f"\n5. Reference link typo ('aspxnet'): {len(p5_found)} matches")
    for s in p5_found:
        print(f"   {s}")

print("STARTING AUDIT...")
audit_doc(master_path, "MASTER THESIS")
audit_doc(old_path, "OLD THESIS DRAFT")
