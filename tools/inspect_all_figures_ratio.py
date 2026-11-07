# -*- coding: utf-8 -*-
import os, sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

print("=== INSPECTING ALL IMAGES IN FIGURES/ ===")
for f in sorted(os.listdir('figures')):
    if f.endswith('.png') or f.endswith('.jpg'):
        p = os.path.join('figures', f)
        im = Image.open(p)
        w, h = im.size
        ratio = w / h if h > 0 else 0
        h_cm_at_14_5 = 14.5 / ratio if ratio > 0 else 0
        warning = " [SQUISHED < 3cm!]" if h_cm_at_14_5 < 3.0 else ""
        print(f"{f}: {w}x{h} px | ratio={ratio:.2f} | height_in_word={h_cm_at_14_5:.2f}cm{warning}")
