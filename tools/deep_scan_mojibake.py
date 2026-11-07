# -*- coding: utf-8 -*-
import sys, os, docx

sys.stdout.reconfigure(encoding='utf-8')

test_chars = ['¡', '¢', '£', '€', '‚', 'ƒ', '„', '…', '†', '‡', 'ˆ', '‰', 'Š', '‹', 'Œ', 'Ž', '‘', '’', '“', '”', '•', '–', '—', '˜', '™', 'š', '›', 'œ', 'ž', 'Ÿ']

def check_file(path):
    print(f"\nChecking: {path}")
    try:
        doc = docx.Document(path)
    except Exception as e:
        print(f"  Cannot open: {e}")
        return

    # Check paragraphs
    moji_p = []
    for i, p in enumerate(doc.paragraphs):
        # Check if contains at least 3 consecutive characters from test_chars or ¡¢£
        if '¡¢£' in p.text or '€ ‚' in p.text or 'œ ž' in p.text:
            moji_p.append((i+1, p.text[:80]))
    print(f"  Paragraphs with mojibake: {len(moji_p)}")
    for pnum, s in moji_p[:5]:
        print(f"    P#{pnum}: {s}")

    # Check headers and footers
    hf_moji = []
    for s_idx, section in enumerate(doc.sections):
        for h in [section.header, section.first_page_header, section.footer, section.first_page_footer]:
            if h:
                for hp in h.paragraphs:
                    if '¡¢£' in hp.text or '€ ‚' in hp.text or 'œ ž' in hp.text:
                        hf_moji.append((s_idx, hp.text[:80]))
    print(f"  Header/Footer mojibake: {len(hf_moji)}")
    for s_idx, s in hf_moji[:5]:
        print(f"    Sec#{s_idx}: {s}")

    # Check tables
    tbl_moji = []
    for t_idx, t in enumerate(doc.tables):
        for r in t.rows:
            for c in r.cells:
                if '¡¢£' in c.text or '€ ‚' in c.text or 'œ ž' in c.text:
                    tbl_moji.append((t_idx, c.text[:60]))
    print(f"  Table mojibake: {len(tbl_moji)}")

check_file('KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx')
check_file('BỘ CÔNG THƯƠNG.docx')
