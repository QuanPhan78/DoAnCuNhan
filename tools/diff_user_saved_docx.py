# -*- coding: utf-8 -*-
"""
Compare KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025_USER_SAVED.docx with the generator output.
Inspect what was modified by the user.
"""
import sys, os, docx, difflib

sys.stdout.reconfigure(encoding='utf-8')

user_doc_path = 'KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025_USER_SAVED.docx'
doc_user = docx.Document(user_doc_path)

print(f"=== INSPECTING USER SAVED DOCX: {user_doc_path} ===")
print(f"Total paragraphs in user doc: {len(doc_user.paragraphs)}")
print(f"Total tables in user doc: {len(doc_user.tables)}")
print(f"Total sections in user doc: {len(doc_user.sections)}")

# Let's inspect paragraphs around Section 1.2, Chapter 5, and any other modified sections
print("\n--- Sample Paragraphs in Chapter 1 ---")
for i, p in enumerate(doc_user.paragraphs):
    if '1.2.' in p.text or 'Hình 1.2' in p.text:
        print(f"P#{i+1}: {p.text}")
        if i > 0:
            print(f"  Prev P#{i}: {doc_user.paragraphs[i-1].text}")
        if i < len(doc_user.paragraphs) - 1:
            print(f"  Next P#{i+2}: {doc_user.paragraphs[i+1].text}")

print("\n--- Checking Chapter 5 & Testing Content ---")
for i, p in enumerate(doc_user.paragraphs):
    if '5.2.' in p.text or 'TC-' in p.text or 'Challenger' in p.text:
        print(f"P#{i+1}: {p.text[:100]}")

print("\n--- Checking Headings List in User Doc ---")
for i, p in enumerate(doc_user.paragraphs):
    if p.style.name.startswith('Heading 1') or p.text.startswith('CHƯƠNG') or p.text.startswith('PHẦN'):
        print(f"P#{i+1} [{p.style.name}]: {p.text[:80]}")
