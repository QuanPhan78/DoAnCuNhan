# -*- coding: utf-8 -*-
"""
Deep diff between user saved file and script output.
"""
import sys, os, docx

sys.stdout.reconfigure(encoding='utf-8')

user_path = 'KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025_USER_SAVED.docx'
doc = docx.Document(user_path)

print(f"=== CHECKING SPECIFIC SECTIONS IN USER FILE ===")

# Check Cover & Preliminary
print("\n--- Preliminary / Cover ---")
for i, p in enumerate(doc.paragraphs[:50]):
    txt = p.text.strip()
    if txt and ('ĐẠI HỌC' in txt or 'GIẢNG VIÊN' in txt or 'SINH VIÊN' in txt or 'LỜI CẢM ƠN' in txt or 'CAM ĐOAN' in txt):
        print(f"P#{i+1}: {txt}")

# Check Section 1.2
print("\n--- Section 1.2 (Where user saw image) ---")
for i, p in enumerate(doc.paragraphs):
    if '1.2. CƠ CẤU' in p.text or 'Bộ máy vận hành' in p.text or 'Hình 1.2' in p.text:
        print(f"P#{i+1}: {p.text}")

# Check if there are any specific user edits in Section 3, 4, 5
print("\n--- Check AI / Testing Section (Chapter 5) ---")
for i, p in enumerate(doc.paragraphs):
    if '5.2.' in p.text or '5.3.' in p.text or 'Trí tuệ Nhân tạo' in p.text:
        print(f"P#{i+1}: {p.text}")

print("\n--- Check Comments or Revisions in User Doc ---")
# Check if doc has comments
print("Doc comments part:", [p for p in doc.part.related_parts if 'comments' in str(p)])
