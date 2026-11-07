#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from PIL import Image, ImageChops
import numpy as np

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path("d:/DoAnCuNhan")
FIGURES_DIR = PROJECT_ROOT / "figures"

ui_files = [
    ("hinh_3_10_ui_trang_chu.png", "Client Trang chu"),
    ("hinh_3_11_ui_chi_tiet_san_pham.png", "Client Chi tiet SP"),
    ("hinh_3_12_ui_checkout.png", "Client Checkout"),
    ("hinh_3_13_ui_ky_hop_dong.png", "Client Ky hop dong"),
    ("hinh_3_14_ui_hop_dong_khach_hang.png", "Client Hop dong KH"),
    ("hinh_3_15_ui_cong_no_khach_hang.png", "Client Cong no KH"),
    ("hinh_3_16_ui_phieu_bao_tri.png", "Client Phieu bao tri"),
    ("hinh_3_17_ui_admin_dashboard.png", "Admin Dashboard"),
    ("hinh_3_18_ui_admin_cong_no.png", "Admin Thiet bi Serial"),
    ("hinh_3_19_ui_admin_bao_tri.png", "Admin Tham dinh HD"),
    ("hinh_3_20_ui_in_hop_dong.png", "Admin Quan ly cong no"),
]

print("=" * 80)
print("AUTHENTICITY & CONTENT DIVERSITY VERIFICATION OF 11 UI SCREENSHOTS")
print("=" * 80)

images = []
for fname, label in ui_files:
    p = FIGURES_DIR / fname
    im = Image.open(p).convert("RGB")
    arr = np.array(im)
    images.append((fname, label, im, arr))
    
    # Check dimensions
    w, h = im.size
    size_kb = p.stat().st_size / 1024
    print(f"[{label:22s}] Dimensions: {w}x{h} | Size: {size_kb:6.1f} KB")
    
    # Check top navbar color for client (should contain Deep Navy #0f2b5c = (15, 43, 92))
    # Or admin sidebar for admin (left side)
    navy_target = np.array([15, 43, 92])
    dist = np.sqrt(np.sum((arr - navy_target) ** 2, axis=2))
    navy_pixels = np.sum(dist < 15)
    print(f"  -> Deep Navy pixels (#0f2b5c): {navy_pixels:6d} pixels ({navy_pixels / (w*h) * 100:.2f}% of canvas)")

print("\n" + "=" * 80)
print("PAIRWISE MEAN ABSOLUTE DIFFERENCE (MAD) MATRIX (STRESS-TESTING DIVERSITY)")
print("=" * 80)
min_diff = 999999
min_pair = None

for i in range(len(images)):
    for j in range(i + 1, len(images)):
        name1, lbl1, _, arr1 = images[i]
        name2, lbl2, _, arr2 = images[j]
        mad = np.mean(np.abs(arr1.astype(float) - arr2.astype(float)))
        if mad < min_diff:
            min_diff = mad
            min_pair = (lbl1, lbl2)
        print(f"  {lbl1:22s} vs {lbl2:22s} -> MAD = {mad:5.2f}")

print("\n" + "=" * 80)
print(f"MINIMUM PAIRWISE DIFFERENCE: {min_diff:.2f} between {min_pair[0]} and {min_pair[1]}")
if min_diff > 10.0:
    print("SUCCESS: High visual diversity confirmed across all 11 screenshots. NO DUPLICATE PAGES!")
else:
    print("FAIL: Near-duplicate UI screenshots detected!")
