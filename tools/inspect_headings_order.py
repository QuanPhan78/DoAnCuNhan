# -*- coding: utf-8 -*-
import docx, sys

sys.stdout.reconfigure(encoding='utf-8')
doc = docx.Document('KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx')

print("=== INSPECTING ALL HEADINGS AND MAJOR SECTIONS ===")
for i, p in enumerate(doc.paragraphs):
    if p.style.name.startswith('Heading') or p.text.startswith('CHƯƠNG') or p.text.startswith('PHẦN') or 'DANH MỤC' in p.text:
        print(f"P#{i+1} [{p.style.name}]: {p.text[:80]}")
