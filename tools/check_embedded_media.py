# -*- coding: utf-8 -*-
import zipfile, os, sys

sys.stdout.reconfigure(encoding='utf-8')

docx_path = 'KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025_USER_SAVED.docx'
with zipfile.ZipFile(docx_path, 'r') as z:
    media_files = [f for f in z.namelist() if f.startswith('word/media/')]
    print(f"Total media files embedded in user docx: {len(media_files)}")
    for m in media_files[:10]:
        info = z.getinfo(m)
        print(f"  {m}: {info.file_size:,} bytes")
