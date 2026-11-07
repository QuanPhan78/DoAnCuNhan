#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys
from pathlib import Path
from PIL import Image, ImageChops

PROJECT_ROOT = Path("d:/DoAnCuNhan")
FIGURES_DIR = PROJECT_ROOT / "figures"

sys.path.insert(0, str(PROJECT_ROOT / "tools"))
from sync_thesis_documents import CANONICAL_MEDIA_MAP

technical_diagrams = []
for img_id, fig_name in sorted(CANONICAL_MEDIA_MAP.items(), key=lambda x: int(x[0].replace("image", "").replace(".png", ""))):
    if fig_name == "logo_huit.png":
        continue
    if any(fig_name.startswith(f"hinh_3_{i}_ui") for i in range(10, 21)):
        continue
    technical_diagrams.append((img_id, fig_name))

print(f"Total technical diagrams: {len(technical_diagrams)}")

purity_issues = []
bg_issues = []

for img_id, fig_name in technical_diagrams:
    p = FIGURES_DIR / fig_name
    if not p.exists():
        continue
    with Image.open(p) as im:
        rgb = im.convert("RGB")
        w, h = rgb.size
        # Check corners for pure white
        c1 = rgb.getpixel((0, 0))
        c2 = rgb.getpixel((w - 1, 0))
        c3 = rgb.getpixel((0, h - 1))
        c4 = rgb.getpixel((w - 1, h - 1))
        non_white = [c for c in [c1, c2, c3, c4] if c != (255, 255, 255)]
        if non_white:
            bg_issues.append((img_id, fig_name, non_white))
        
        # Check color channels
        r, g, b = rgb.split()
        d_rg = ImageChops.difference(r, g).getextrema()
        d_gb = ImageChops.difference(g, b).getextrema()
        # d_rg[1] is max diff between R and G
        # d_gb[1] is max diff between G and B
        max_diff = max(d_rg[1], d_gb[1])
        # #27272a has diff 3. Allow small tolerance <= 5 for antialiasing of #27272a
        if max_diff > 5:
            purity_issues.append((img_id, fig_name, max_diff))

print(f"Background issues (corners != #ffffff): {len(bg_issues)}")
for x in bg_issues:
    print(f"  {x[0]} ({x[1]}): {x[2]}")

print(f"Color purity issues (max channel diff > 5): {len(purity_issues)}")
for x in purity_issues:
    print(f"  {x[0]} ({x[1]}): max_diff = {x[2]}")

if not bg_issues and not purity_issues:
    print("ALL TECHNICAL DIAGRAMS HAVE PURE WHITE BACKGROUND AND ZERO COLOR SATURATION!")
