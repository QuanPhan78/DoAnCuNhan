# -*- coding: utf-8 -*-
import sys, re

sys.stdout.reconfigure(encoding='utf-8')

with open('tools/build_master_thesis.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

targets = [
    ('Section 3.2.2', 1740, 1750),
    ('Introduction Ziele', 890, 905),
    ('Section 2.3.3 API', 1430, 1445),
    ('Section 3.1.1 DB intro', 1490, 1500),
    ('Section 3.1.2 Constraints', 1715, 1730),
    ('Chapter 3 Conclusion', 1830, 1840),
    ('Chapter 4 Architecture', 1865, 1875),
    ('Chapter 4 Security & API', 1890, 1915),
    ('General Conclusion', 1980, 2000),
]

for name, start, end in targets:
    print(f"\n==================== {name} (Lines {start}-{end}) ====================")
    for j in range(start - 1, min(len(lines), end)):
        print(f"L{j+1}: {lines[j]}", end='')
