#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys
from pathlib import Path
from PIL import Image
import numpy as np

PROJECT_ROOT = Path("d:/DoAnCuNhan")
FIGURES_DIR = PROJECT_ROOT / "figures"

sys.path.insert(0, str(PROJECT_ROOT / "tools"))
from sync_thesis_documents import CANONICAL_MEDIA_MAP

# Technical diagrams are all 78 images EXCEPT logo_huit.png (image1) and the 11 UI screenshots (image34-image44)
EXCLUDED = {"logo_huit.png"}
for i in range(10, 21):
    EXCLUDED.add(f"hinh_3_{i}")

technical_diagrams = []
for img_id, fig_name in sorted(CANONICAL_MEDIA_MAP.items(), key=lambda x: int(x[0].replace("image", "").replace(".png", ""))):
    if fig_name == "logo_huit.png":
        continue
    if any(fig_name.startswith(f"hinh_3_{i}_ui") for i in range(10, 21)):
        continue
    technical_diagrams.append((img_id, fig_name))

print(f"Total technical diagrams to analyze: {len(technical_diagrams)}")

purity_issues = []
bg_issues = []

for img_id, fig_name in technical_diagrams:
    p = FIGURES_DIR / fig_name
    if not p.exists():
        print(f"MISSING: {fig_name}")
        continue
    
    with Image.open(p) as im:
        rgb = im.convert("RGB")
        arr = np.array(rgb)
        h, w, _ = arr.shape
        
        # Check 4 corners for pure white background (#ffffff = 255, 255, 255)
        corners = [
            tuple(arr[0, 0]),
            tuple(arr[0, w - 1]),
            tuple(arr[h - 1, 0]),
            tuple(arr[h - 1, w - 1])
        ]
        non_white_corners = [c for c in corners if c != (255, 255, 255)]
        if non_white_corners:
            bg_issues.append((img_id, fig_name, non_white_corners))
            
        # Check colored pixels
        # Grayscale: R == G == B
        # Allowed exception: Neutral dark header #27272a -> (39, 39, 42)
        # In #27272a, |R - G| = 0, |R - B| = 3, |G - B| = 3.
        # Also Zinc neutral accents in matplotlib:
        # Let's measure max saturation / color deviation: max(|R-G|, |G-B|, |B-R|)
        r = arr[:, :, 0].astype(int)
        g = arr[:, :, 1].astype(int)
        b = arr[:, :, 2].astype(int)
        
        diff_rg = np.abs(r - g)
        diff_gb = np.abs(g - b)
        diff_br = np.abs(b - r)
        max_channel_diff = np.maximum(np.maximum(diff_rg, diff_gb), diff_br)
        
        # Count pixels with significant color: max_channel_diff > 15
        # (Header #27272a has max diff 3; antialiasing might produce up to ~10-15)
        colored_mask = max_channel_diff > 15
        colored_count = np.sum(colored_mask)
        
        if colored_count > 0:
            sample_colored = arr[colored_mask][:5]
            purity_issues.append((img_id, fig_name, colored_count, sample_colored.tolist()))

print("\n--- BACKGROUND PURITY RESULTS ---")
print(f"Total diagrams checked: {len(technical_diagrams)}")
print(f"Diagrams with non-white corners: {len(bg_issues)}")
for item in bg_issues:
    print(f"  {item[0]} ({item[1]}): non-white corners: {item[2]}")

print("\n--- COLOR SATURATION / PIXEL PURITY RESULTS ---")
print(f"Diagrams with colored pixels (max channel diff > 15): {len(purity_issues)}")
for item in purity_issues:
    print(f"  {item[0]} ({item[1]}): {item[2]} colored pixels. Samples: {item[3]}")
