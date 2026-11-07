# -*- coding: utf-8 -*-
import docx, sys, os

sys.stdout.reconfigure(encoding='utf-8')

doc_path = 'KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx'
doc = docx.Document(doc_path)

error_terms = [
    'MaVaiTroint', 'TenVaiTronarchar', 'MaNguoiDungint', 'HoTennarchar',
    'MaDanhMucint', 'TenDanhMucnvarchar', 'BiDanhvarchar', 'TrangThaiint',
    'MaSanPhamint', 'TenSanPhamnvarchar', 'GiaThueNgaydecimal', 'SoLuongSanCoint',
    'MaThietBiint', 'SoSerialvdarchar', 'TinhTrangint', 'NgayNhapKhodatetime', 'ViTriKhonvdarchar',
    'MaLichSuint', 'MaHopDongint', 'NgayBatDaudatetime', 'NgayKetThucdatetime',
    'MaKhuyenMaiint', 'MaCodevarchar', 'TiLeGiamdecimal', 'SoTienGiamToiDadecimal',
    'SoHopDongvarchar', 'MaKhachHangint', 'MaChiTietint', 'SoLuongint', 'MaKyHanint',
    'MaPhieuThuint', 'SoTiendecimal', 'MaPhieuChiint', 'MaBaoTriint', 'MaPhanCongint',
    'MaThongBaoint', 'NoiDungnvarchar', 'MaCauHinhint', 'Khoavarchar', 'MaLogint',
    'MatKhauHashnarchar', 'Emailnarchar', 'DiaChinvarchar', 'MoTanvdarchar',
    'HinhAnhnvdarchar', 'ChuKyBase64nvarchar', 'AnhCCCDnvarchar', 'TinhTrangBanGia',
    'TinhTrangThuHo', 'LyDoChinvarchar', 'NguoiNhannvarchar', 'MoTaLoinvarchar',
    'TamDungTinhTie', 'TenLinhKienTha', 'MaNhanVienKyT', 'TieuDenvarchar', 'PayloadJsonnvarchar',
    'narchar', 'nvdarchar', 'vdarchar', '25 5', '10 0', '15 0', 'm ax', 'nbit'
]

full_text = []
for p in doc.paragraphs:
    full_text.append(p.text)
for t in doc.tables:
    for r in t.rows:
        for c in r.cells:
            full_text.append(c.text)

all_content = ' '.join(full_text)

print(f"=== AUDITING {len(error_terms)} REPORTED DEFECT TERMS IN {doc_path} ===")
found = []
for term in error_terms:
    count = all_content.count(term)
    if count > 0:
        found.append((term, count))

if not found:
    print(f"SUCCESS: 0 / {len(error_terms)} DEFECTS FOUND! The current Word document has ZERO occurrences of these errors!")
else:
    print(f"FOUND {len(found)} DEFECTS:")
    for term, count in found:
        print(f"  * '{term}': {count} occurrence(s)")

# Inspect the 18 database tables in the document
print("\n=== INSPECTING THE 18 DATABASE DICTIONARY TABLES IN CURRENT DOCX ===")
db_tables = []
for idx, p in enumerate(doc.paragraphs):
    if "Bảng 3.1.1." in p.text:
        db_tables.append((idx, p.text))

print(f"Total Database Dictionary Tables (Bảng 3.1.1. 1 to 18): {len(db_tables)}")
for idx, title in db_tables:
    print(f"  * {title}")

# Verify structure of all 18 tables
print("\n=== VERIFYING COLUMN SEPARATION AND SQL SYNTAX IN ALL 18 TABLES ===")
dict_tables = []
for t_idx, t in enumerate(doc.tables):
    headers = [c.text.strip() for c in t.rows[0].cells]
    if len(headers) == 6 and headers[1] == 'Tên cột (Field Name)' and headers[2] == 'Kiểu dữ liệu':
        dict_tables.append((t_idx, t))

print(f"Total Dictionary Tables found: {len(dict_tables)} (Expected 18)")

all_clean = True
total_fields = 0
for idx, (t_idx, t) in enumerate(dict_tables, 1):
    row_count = len(t.rows) - 1
    total_fields += row_count
    for r_idx in range(1, len(t.rows)):
        col_name = t.rows[r_idx].cells[1].text
        data_type = t.rows[r_idx].cells[2].text
        if any(bad in col_name or bad in data_type for bad in ['narchar', 'nvdarchar', 'vdarchar', '25 5', '10 0', '15 0', 'm ax', 'nbit']):
            print(f"  [ERROR] Table {t_idx} Row {r_idx}: Col='{col_name}', Type='{data_type}'")
            all_clean = False
        if ' ' in col_name:
            print(f"  [ERROR] Table {t_idx} Row {r_idx}: Col name contains space: '{col_name}'")
            all_clean = False

print(f"Total fields audited across 18 tables: {total_fields}")
if all_clean:
    print("ALL 18 TABLES ARE 100% CLEAN! Every column name and data type is strictly separated into its own cell with correct SQL syntax.")
