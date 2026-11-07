# -*- coding: utf-8 -*-
import os, shutil, sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
updated = os.path.join(PROJECT_ROOT, "KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025_Updated.docx")
master = os.path.join(PROJECT_ROOT, "KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx")

if not os.path.exists(updated):
    print("Updated file does not exist.")
    sys.exit(0)

try:
    if os.path.exists(master):
        os.remove(master)
    shutil.move(updated, master)
    print("Master document updated successfully!")
except Exception as e:
    print(f"Could not replace master doc yet (Word may still be open): {e}")
