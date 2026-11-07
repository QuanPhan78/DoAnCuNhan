#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import zipfile
from PIL import Image, ImageChops
from pathlib import Path
import io

DOCX = Path("KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx")
FIG = Path("figures/hinh_1_1_quy_trinh_truyen_thong.png")

with zipfile.ZipFile(DOCX) as z:
    d_bytes = z.read("word/media/image2.png")

img_docx = Image.open(io.BytesIO(d_bytes))
img_fig = Image.open(FIG)

print(f"Docx img size: {img_docx.size}, mode: {img_docx.mode}")
print(f"Fig  img size: {img_fig.size}, mode: {img_fig.mode}")

diff = ImageChops.difference(img_docx.convert("RGBA"), img_fig.convert("RGBA"))
bbox = diff.getbbox()
print(f"Difference bbox: {bbox}")
if bbox:
    # Check max difference
    diff_data = diff.getextrema()
    print(f"Diff extrema: {diff_data}")
