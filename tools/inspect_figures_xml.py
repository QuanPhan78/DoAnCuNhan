# -*- coding: utf-8 -*-
import docx, os, sys

sys.stdout.reconfigure(encoding='utf-8')
doc = docx.Document('KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx')

fig_targets = [
    '2.2.2.2. 1',
    '3.4.2. 2',
    '3.4.3. 2',
    '3.4.3. 3',
    '3.4.4. 2',
    '3.4.6. 3'
]

print("=== CHECKING FIGURE TARGETS IN KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx ===")
for target in fig_targets:
    for i, p in enumerate(doc.paragraphs):
        if f'Hình {target}' in p.text and not p.text.endswith('\t35') and not p.text.endswith('\t45') and not p.text.endswith('\t98') and not p.text.endswith('\t148'): # exclude list of figures
            prev_p = doc.paragraphs[i-1] if i > 0 else None
            has_drawing = False
            rId = None
            if prev_p:
                xml = prev_p._element.xml
                has_drawing = 'w:drawing' in xml or 'a:blip' in xml
                # extract rId
                if 'r:embed="' in xml:
                    rId = xml.split('r:embed="')[1].split('"')[0]
            
            # resolve rId to target part
            target_image = "N/A"
            if rId and prev_p.part.rels.get(rId):
                target_image = prev_p.part.rels[rId].target_ref

            print(f"Fig {target} (P#{i+1}): caption='{p.text[:60]}'")
            print(f"   Prev P#{i}: has_drawing={has_drawing}, rId={rId}, image_ref={target_image}")
