# -*- coding: utf-8 -*-
import sys, os

sys.stdout.reconfigure(encoding='utf-8')

with open('tools/build_master_thesis.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

targets = [
    'vững chắc',
    'Web Shell',
    'hai chiều',
    'DatabaseController.cs'
]

for kw in targets:
    print(f'=== Keyword: {kw} ===')
    for i, line in enumerate(lines):
        if kw in line:
            print(f'Line {i+1}: {line.strip()[:140]}')
