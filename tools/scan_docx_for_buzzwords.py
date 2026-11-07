# -*- coding: utf-8 -*-
import sys, docx

sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document('KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx')

buzzwords = [
    'sang trọng',
    'thanh lịch',
    'Executive Dot Pill',
    'Executive Deep Navy',
    'Executive Navy',
    'tuân thủ tuyệt đối',
    'chuẩn mực',
    'khắt khe',
    'nghiêm ngặt',
    'điểm nghẽn nghiêm trọng nhất',
]

print("=== SCANNING GENERATED DOCX FOR BUZZWORDS ===")
found_any = False
for i, p in enumerate(doc.paragraphs):
    for b in buzzwords:
        if b.lower() in p.text.lower():
            # Exclude table of contents or figure captions if any
            print(f"P#{i+1} [{b}]: {p.text[:120]}...")
            found_any = True

if not found_any:
    print("[ALL CLEAR] Zero hyperbolic AI buzzwords found in the document!")
