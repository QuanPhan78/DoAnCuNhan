#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import hashlib
import zipfile
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path("d:/DoAnCuNhan")
FIGURES_DIR = PROJECT_ROOT / "figures"
DOCX_1 = PROJECT_ROOT / "KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx"
DOCX_2 = PROJECT_ROOT / "BaoCao_KLCN058_Final.docx"

sys.path.insert(0, str(PROJECT_ROOT / "tools"))
from sync_thesis_documents import CANONICAL_MEDIA_MAP

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

print("--- REQUIREMENT 1: MEDIA EQUALITY ---")
print(f"Canonical map entries: {len(CANONICAL_MEDIA_MAP)}")

# Extract media from DOCX_1
docx1_hashes = {}
with zipfile.ZipFile(DOCX_1, "r") as z1:
    for name in z1.namelist():
        if name.startswith("word/media/"):
            img_name = os.path.basename(name)
            docx1_hashes[img_name] = sha256_bytes(z1.read(name))

# Extract media from DOCX_2
docx2_hashes = {}
with zipfile.ZipFile(DOCX_2, "r") as z2:
    for name in z2.namelist():
        if name.startswith("word/media/"):
            img_name = os.path.basename(name)
            docx2_hashes[img_name] = sha256_bytes(z2.read(name))

figures_hashes = {}
for media_name, fig_name in CANONICAL_MEDIA_MAP.items():
    fig_path = FIGURES_DIR / fig_name
    if not fig_path.exists():
        print(f"MISSING FIGURE: {fig_path}")
    else:
        figures_hashes[media_name] = sha256_file(fig_path)

mismatch_d1_d2 = []
mismatch_d1_fig = []
mismatch_d2_fig = []

for i in range(1, 79):
    img = f"image{i}.png"
    h1 = docx1_hashes.get(img)
    h2 = docx2_hashes.get(img)
    hf = figures_hashes.get(img)
    if h1 != h2:
        mismatch_d1_d2.append((img, h1, h2))
    if h1 != hf:
        mismatch_d1_fig.append((img, CANONICAL_MEDIA_MAP.get(img), h1, hf))
    if h2 != hf:
        mismatch_d2_fig.append((img, CANONICAL_MEDIA_MAP.get(img), h2, hf))

print(f"Docx1 media count: {len(docx1_hashes)}")
print(f"Docx2 media count: {len(docx2_hashes)}")
print(f"Figures mapped count: {len(figures_hashes)}")
print(f"Mismatches between Docx1 and Docx2: {len(mismatch_d1_d2)}")
print(f"Mismatches between Docx1 and figures/: {len(mismatch_d1_fig)}")
print(f"Mismatches between Docx2 and figures/: {len(mismatch_d2_fig)}")

if not mismatch_d1_d2 and not mismatch_d1_fig and not mismatch_d2_fig:
    print("SUCCESS: 100% SHA-256 MATCH ACROSS ALL 78 ASSETS IN BOTH DOCX PACKAGES AND FIGURES/")
else:
    print("FAILURES DETECTED IN MEDIA EQUALITY!")

print("\n--- REQUIREMENT 3: UI SCREENSHOTS AUTHENTICITY ---")
ui_files = [f"hinh_3_{i}_ui_{suf}.png" for i, suf in [
    (10, "trang_chu"),
    (11, "chi_tiet_san_pham"),
    (12, "checkout"),
    (13, "ky_hop_dong"),
    (14, "hop_dong_khach_hang"),
    (15, "cong_no_khach_hang"),
    (16, "phieu_bao_tri"),
    (17, "admin_dashboard"),
    (18, "admin_cong_no"),
    (19, "admin_bao_tri"),
    (20, "in_hop_dong")
]]

ui_hashes = set()
for ui_file in ui_files:
    p = FIGURES_DIR / ui_file
    if not p.exists():
        print(f"MISSING UI FILE: {ui_file}")
        continue
    sz = p.stat().st_size
    h = sha256_file(p)
    im = Image.open(p)
    w, h_px = im.size
    fmt = im.format
    print(f"{ui_file:35s}: size={sz:7d} B, format={fmt}, res={w}x{h_px}, sha256={h[:16]}")
    assert fmt == "PNG", f"Not PNG: {fmt}"
    assert (w, h_px) == (1920, 1080), f"Wrong res: {w}x{h_px}"
    assert sz > 100 * 1024, f"File too small: {sz}"
    ui_hashes.add(h)

print(f"Unique UI SHA-256 hashes: {len(ui_hashes)} / {len(ui_files)}")
assert len(ui_hashes) == len(ui_files), "Duplicate UI screenshots found!"
print("SUCCESS: All 11 UI screenshot files are valid 1920x1080 PNG, >100KB, and 100% unique!")
