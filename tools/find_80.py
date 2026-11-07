# -*- coding: utf-8 -*-
import docx, sys, re

sys.stdout.reconfigure(encoding='utf-8')

def find_80(path, label):
    print(f"\n--- Checking for '80' in {label} ({path}) ---")
    doc = docx.Document(path)
    for i, p in enumerate(doc.paragraphs):
        txt = p.text.strip()
        if txt == '80':
            print(f"LONE '80' at P#{i+1}")
        elif ' 80 ' in f" {txt} ":
            # print if short paragraph
            if len(txt) < 40:
                print(f"Short P#{i+1} with 80: '{txt}'")

find_80('KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx', 'MASTER')
find_80('BỘ CÔNG THƯƠNG.docx', 'OLD DRAFT')
