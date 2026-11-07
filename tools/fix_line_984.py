# -*- coding: utf-8 -*-
with open('tools/build_master_thesis.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    'add_p(doc, "Bốn bất cập và điểm nghẽn nghiêm trọng nhất trong quy trình thủ công được ghi nhận gồm:")',
    'add_p(doc, "Bốn bất cập và hạn chế chính trong quy trình quản lý thủ công bao gồm:")'
)

with open('tools/build_master_thesis.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Replaced line 984 successfully")
