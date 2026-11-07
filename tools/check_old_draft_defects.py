# -*- coding: utf-8 -*-
import docx, re, sys, os

sys.stdout.reconfigure(encoding='utf-8')

old_path = 'BỘ CÔNG THƯƠNG.docx'
if not os.path.exists(old_path):
    print("Old file not found")
    sys.exit(0)

doc = docx.Document(old_path)
print(f"Total paragraphs in old draft: {len(doc.paragraphs)}")
print(f"Total tables in old draft: {len(doc.tables)}")

# Check for aspxnet
for i, p in enumerate(doc.paragraphs):
    if 'aspxnet' in p.text:
        print(f"FOUND 'aspxnet' in P#{i+1}: {p.text}")

# Check for 2.2.2.2. 1
for i, p in enumerate(doc.paragraphs):
    if '2.2.2.2. 1' in p.text or '2.2.2.2.1' in p.text:
        prev = doc.paragraphs[i-1] if i > 0 else None
        prev_has_img = False
        if prev and ('drawing' in prev._element.xml or 'blip' in prev._element.xml):
            prev_has_img = True
        print(f"Old draft 2.2.2.2.1 at P#{i+1}: prev_has_img={prev_has_img} | text='{p.text[:60]}'")

# Check for 3.4.2.2
for i, p in enumerate(doc.paragraphs):
    if '3.4.2. 2' in p.text or '3.4.2.2' in p.text:
        prev = doc.paragraphs[i-1] if i > 0 else None
        prev_has_img = False
        if prev and ('drawing' in prev._element.xml or 'blip' in prev._element.xml):
            prev_has_img = True
        print(f"Old draft 3.4.2.2 at P#{i+1}: prev_has_img={prev_has_img} | text='{p.text[:60]}'")

# Check for single paragraph with just a number like '80'
for i, p in enumerate(doc.paragraphs):
    if p.text.strip() == '80':
        print(f"Old draft lone number '80' at P#{i+1}")

# Check for garbage numbers like 3.1.1.1.1.1
for i, p in enumerate(doc.paragraphs):
    if '3.1.1.1.1.1' in p.text:
        print(f"Old draft garbage numbers at P#{i+1}: {p.text[:60]}")
