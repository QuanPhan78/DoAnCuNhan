#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, zipfile, re
from pathlib import Path

PROJECT_ROOT = Path("d:/DoAnCuNhan")
FIGURES_DIR = PROJECT_ROOT / "figures"
DOCX_1 = PROJECT_ROOT / "KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx"
DOCX_2 = PROJECT_ROOT / "BaoCao_KLCN058_Final.docx"
TOOLS_DIR = PROJECT_ROOT / "tools"

sys.path.insert(0, str(TOOLS_DIR))
from sync_thesis_documents import CANONICAL_MEDIA_MAP

PATTERNS = [
    ("Phone / Account Number", re.compile(r"0783406516", re.IGNORECASE)),
    ("Author Name ASCII", re.compile(r"PHAN\s+MINH\s+QUAN", re.IGNORECASE)),
    ("Author Name Unicode", re.compile(r"Phan\s+Minh\s+Quân", re.IGNORECASE)),
    ("MBBank", re.compile(r"MBBank|MB\s+Bank|970422", re.IGNORECASE)),
    ("Machine Translation (động cơ)", re.compile(r"động\s+cơ", re.IGNORECASE)),
]

findings = []

print("=" * 80)
print("SCANNING TOOLS/*.PY FOR SENSITIVE DATA")
print("=" * 80)
for p in TOOLS_DIR.glob("*.py"):
    text = p.read_text(encoding="utf-8", errors="ignore")
    for label, pat in PATTERNS:
        matches = pat.findall(text)
        if matches:
            # Check if it's in a comment describing what was replaced or if it's actual data
            # Let's inspect each line
            for line_no, line in enumerate(text.splitlines(), 1):
                if pat.search(line):
                    findings.append((f"tools/{p.name}:{line_no}", label, line.strip()))
                    print(f"[FOUND] {p.name}:{line_no} [{label}]: {line.strip()[:100]}")

print("\n" + "=" * 80)
print("SCANNING DOCX 1 FOR SENSITIVE DATA")
print("=" * 80)
with zipfile.ZipFile(DOCX_1, "r") as z1:
    for name in z1.namelist():
        if name.endswith(".xml") or name.endswith(".rels"):
            content = z1.read(name).decode("utf-8", errors="ignore")
            for label, pat in PATTERNS:
                if pat.search(content):
                    findings.append((f"DOCX_1/{name}", label, "Found in XML content"))
                    print(f"[FOUND] DOCX_1/{name} [{label}]")

print("\n" + "=" * 80)
print("SCANNING DOCX 2 FOR SENSITIVE DATA")
print("=" * 80)
with zipfile.ZipFile(DOCX_2, "r") as z2:
    for name in z2.namelist():
        if name.endswith(".xml") or name.endswith(".rels"):
            content = z2.read(name).decode("utf-8", errors="ignore")
            for label, pat in PATTERNS:
                if pat.search(content):
                    findings.append((f"DOCX_2/{name}", label, "Found in XML content"))
                    print(f"[FOUND] DOCX_2/{name} [{label}]")

print("\n" + "=" * 80)
print("SCANNING ALL 78 IMAGE FILES IN FIGURES/ (BINARY & TEXT CHUNKS)")
print("=" * 80)
for img_id, fig_name in sorted(CANONICAL_MEDIA_MAP.items(), key=lambda x: int(x[0].replace("image", "").replace(".png", ""))):
    p = FIGURES_DIR / fig_name
    if not p.exists():
        continue
    data = p.read_bytes()
    # Search binary data decoded with utf-8 / latin1
    text_latin1 = data.decode("latin1", errors="ignore")
    for label, pat in PATTERNS:
        if pat.search(text_latin1):
            findings.append((f"figures/{fig_name}", label, "Found in binary payload"))
            print(f"[FOUND] figures/{fig_name} [{label}]")

print("\n" + "=" * 80)
print(f"TOTAL SENSITIVE DATA FINDINGS: {len(findings)}")
print("=" * 80)
