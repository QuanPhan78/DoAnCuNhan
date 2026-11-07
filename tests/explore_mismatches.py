#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, hashlib, zipfile
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path("d:/DoAnCuNhan")
FIGURES_DIR = PROJECT_ROOT / "figures"
DOCX_1 = PROJECT_ROOT / "KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx"

sys.path.insert(0, str(PROJECT_ROOT / "tools"))
from sync_thesis_documents import CANONICAL_MEDIA_MAP

def sha256_bytes(b): return hashlib.sha256(b).hexdigest()
def sha256_file(p):
    with open(p, "rb") as f: return hashlib.sha256(f.read()).hexdigest()

with zipfile.ZipFile(DOCX_1, "r") as z1:
    for img_name, fig_name in sorted(CANONICAL_MEDIA_MAP.items(), key=lambda x: int(x[0].replace("image", "").replace(".png", ""))):
        b = z1.read(f"word/media/{img_name}")
        h_docx = sha256_bytes(b)
        h_fig = sha256_file(FIGURES_DIR / fig_name)
        if h_docx != h_fig:
            print(f"MISMATCH: {img_name} -> {fig_name}")
            print(f"  docx size: {len(b)}, hash: {h_docx[:16]}")
            fig_size = (FIGURES_DIR / fig_name).stat().st_size
            print(f"  fig  size: {fig_size}, hash: {h_fig[:16]}")
