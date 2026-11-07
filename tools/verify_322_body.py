# -*- coding: utf-8 -*-
import sys, docx

sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document('KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx')

found = False
count = 0
for p in doc.paragraphs:
    if '3.2.2. Thiết kế giao diện phân hệ quản trị (Admin)' in p.text:
        found = True
    if found:
        print(f">> {p.text}\n")
        count += 1
        if count >= 8:
            break
