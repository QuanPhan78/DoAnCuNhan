# -*- coding: utf-8 -*-
import re, sys, os

sys.stdout.reconfigure(encoding='utf-8')

script_path = 'tools/build_master_thesis.py'
with open(script_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

buzzwords = [
    'sang trọng', 'thanh lịch', 'Executive', 'Dot Pill', 'tuân thủ tuyệt đối',
    'tuyệt đối', 'nghiêm ngặt', 'khắt khe', 'vững chắc', 'triệt để',
    'tối tân', 'đột phá', 'chuẩn mực', 'hoàn hảo', 'vượt trội',
    'tinh tế', 'đẳng cấp', 'tự động hóa hoàn toàn', 'tiền đề vững chắc'
]

print("=== SCANNING HYPERBOLIC / AI BUZZWORDS IN BUILD_MASTER_THESIS.PY ===")
matches_by_word = {w: [] for w in buzzwords}

for idx, line in enumerate(lines, 1):
    # Skip comments that are just metadata or css class names
    stripped = line.strip()
    if stripped.startswith('#') or 'class' in stripped:
        continue
    for w in buzzwords:
        if re.search(rf'{re.escape(w)}', line, re.I):
            matches_by_word[w].append((idx, line.strip()))

total_matches = 0
for w, occurrences in matches_by_word.items():
    if occurrences:
        total_matches += len(occurrences)
        print(f"\n--- '{w}' ({len(occurrences)} matches) ---")
        for line_no, text in occurrences[:5]:
            print(f"  [L{line_no}] {text[:120]}")
        if len(occurrences) > 5:
            print(f"  ... and {len(occurrences) - 5} more")

print(f"\nTotal hyperbolic word occurrences: {total_matches}")
