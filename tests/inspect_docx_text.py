#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import zipfile, re, sys
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DOCX_1 = Path("KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx")

with zipfile.ZipFile(DOCX_1, "r") as z:
    doc_xml = z.read("word/document.xml").decode("utf-8")

paragraphs = re.findall(r'<w:p[ >].*?</w:p>', doc_xml)
print(f"Total paragraphs in DOCX_1: {len(paragraphs)}")

for i, p in enumerate(paragraphs):
    txt = re.sub(r'<[^>]+>', '', p)
    if re.search(r"Phan\s+Minh\s+Quân|PHAN\s+MINH\s+QUAN", txt, re.I):
        print(f"[Author in p {i}]: {txt}")
    if re.search(r"MBBank|MB\s+Bank", txt, re.I):
        print(f"[MBBank in p {i}]: {txt}")
    if re.search(r"0783406516", txt):
        print(f"[Phone in p {i}]: {txt}")
    if re.search(r"động\s+cơ", txt, re.I):
        print(f"[dong co in p {i}]: {txt}")
