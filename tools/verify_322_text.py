# -*- coding: utf-8 -*-
import sys, docx

sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document('KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx')

found = False
count = 0
for p in doc.paragraphs:
    if '3.2.2' in p.text:
        found = True
    if found:
        print(f"[{p.text}]")
        count += 1
        if count >= 10:
            break
