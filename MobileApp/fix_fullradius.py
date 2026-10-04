import os

files_to_fix = [
    "lib/screens/reports/reports_screen.dart",
    "lib/screens/search/search_screen.dart"
]

for p in files_to_fix:
    with open(p, "r", encoding="utf-8") as f:
        c = f.read()
    c = c.replace("AppRadius.fullRadius", "BorderRadius.circular(100)")
    with open(p, "w", encoding="utf-8") as f:
        f.write(c)

print("Fixed AppRadius.fullRadius errors.")