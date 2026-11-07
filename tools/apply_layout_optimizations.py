# -*- coding: utf-8 -*-
"""
Script to apply page layout and widowControl optimizations to tools/build_master_thesis.py.
"""
import sys, os

sys.stdout.reconfigure(encoding='utf-8')

script_path = os.path.join(os.path.dirname(__file__), 'build_master_thesis.py')
with open(script_path, 'r', encoding='utf-8') as f:
    text = f.read()

has_crlf = '\r\n' in text
text = text.replace('\r\n', '\n')

# 1. Update format_p to enable widow_control
old_format_p = """    p.alignment = align
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.space_before = Pt(space_before_pt)
    p.paragraph_format.space_after = Pt(space_after_pt)"""

new_format_p = """    p.alignment = align
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.space_before = Pt(space_before_pt)
    p.paragraph_format.space_after = Pt(space_after_pt)
    p.paragraph_format.widow_control = True"""

# 2. Update add_bullet to enable widow_control
old_add_bullet = """    p.paragraph_format.left_indent = Cm(left_ind)
    p.paragraph_format.first_line_indent = Cm(first_ind)
    p.paragraph_format.line_spacing = 1.3
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY"""

new_add_bullet = """    p.paragraph_format.left_indent = Cm(left_ind)
    p.paragraph_format.first_line_indent = Cm(first_ind)
    p.paragraph_format.line_spacing = 1.3
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.widow_control = True
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY"""

# 3. Update Section 1.2 layout in build_chapter1_survey
old_sec_1_2 = """    add_figure_with_caption(doc, "1.1.2", 1, "Sơ đồ luồng quy trình nghiệp vụ cho thuê thiết bị truyền thống",
                            "figures/hinh_1_1_quy_trinh_truyen_thong.png", width_cm=14.5)

    add_heading_2(doc, "1.2. CƠ CẤU TỔ CHỨC VÀ CÁC PHÂN HỆ VẬN HÀNH")
    add_p(doc, "Bộ máy vận hành chu trình cho thuê thiết bị công nghệ được cơ cấu thành 4 vai trò tác nhân chuyên trách:")
    add_bullet(doc, "Quản trị viên hệ thống (Admin): Quản trị người dùng, phân quyền truy cập, thiết lập cấu hình giá thuê, tỷ lệ cọc và giám sát toàn diện hoạt động của hệ thống.")
    add_bullet(doc, "Phòng Kinh doanh & Dịch vụ khách hàng: Tiếp nhận nhu cầu thuê, tư vấn cấu hình, kiểm tra số lượng tồn kho khả dụng, lập báo giá, duyệt hợp đồng, theo dõi lịch thanh toán phân kỳ và hỗ trợ đối soát công nợ.")
    add_bullet(doc, "Phòng Quản lý kho & Kỹ thuật: Tiếp nhận lệnh xuất kho, kiểm định phần cứng, dán tem serial, niêm phong thiết bị, giao nhận máy tận nơi, thực hiện bảo trì sự cố và nghiệm thu thu hồi máy khi kết thúc hợp đồng.")
    add_bullet(doc, "Khách hàng (Cá nhân & Doanh nghiệp): Đăng ký tài khoản, lựa chọn cấu hình máy, ký hợp đồng điện tử trực tuyến, thanh toán cọc qua mã VietQR và gửi yêu cầu hỗ trợ kỹ thuật.")

    add_figure_with_caption(doc, "1.2", 1, "Sơ đồ luồng quy trình nghiệp vụ tổng thể sau khi tin học hóa",
                            "figures/hinh_1_2_quy_trinh_tong_the_de_xuat.png", width_cm=14.5)

    add_heading_2(doc, "1.3. QUY TRÌNH NGHIỆP VỤ TRUYỀN THỐNG VÀ PHÂN TÍCH ĐIỂM NGHẼN")"""

new_sec_1_2 = """    add_figure_with_caption(doc, "1.1.2", 1, "Sơ đồ luồng quy trình nghiệp vụ cho thuê thiết bị truyền thống",
                            "figures/hinh_1_1_quy_trinh_truyen_thong.png", width_cm=14.5)

    doc.add_page_break()
    add_heading_2(doc, "1.2. CƠ CẤU TỔ CHỨC VÀ CÁC PHÂN HỆ VẬN HÀNH")
    add_p(doc, "Bộ máy vận hành chu trình cho thuê thiết bị công nghệ được cơ cấu thành 4 vai trò tác nhân chuyên trách:")
    add_bullet(doc, "Quản trị viên hệ thống (Admin): Quản trị người dùng, phân quyền truy cập, thiết lập cấu hình giá thuê, tỷ lệ cọc và giám sát toàn diện hoạt động của hệ thống.")
    add_bullet(doc, "Phòng Kinh doanh & Dịch vụ khách hàng: Tiếp nhận nhu cầu thuê, tư vấn cấu hình, kiểm tra số lượng tồn kho khả dụng, lập báo giá, duyệt hợp đồng, theo dõi lịch thanh toán phân kỳ và hỗ trợ đối soát công nợ.")
    add_bullet(doc, "Phòng Quản lý kho & Kỹ thuật: Tiếp nhận lệnh xuất kho, kiểm định phần cứng, dán tem serial, niêm phong thiết bị, giao nhận máy tận nơi, thực hiện bảo trì sự cố và nghiệm thu thu hồi máy khi kết thúc hợp đồng.")
    add_bullet(doc, "Khách hàng (Cá nhân & Doanh nghiệp): Đăng ký tài khoản, lựa chọn cấu hình máy, ký hợp đồng điện tử trực tuyến, thanh toán cọc qua mã VietQR và gửi yêu cầu hỗ trợ kỹ thuật.")

    add_figure_with_caption(doc, "1.2", 1, "Sơ đồ luồng quy trình nghiệp vụ tổng thể sau khi tin học hóa",
                            "figures/hinh_1_2_quy_trinh_tong_the_de_xuat.png", width_cm=14.0)

    doc.add_page_break()
    add_heading_2(doc, "1.3. QUY TRÌNH NGHIỆP VỤ TRUYỀN THỐNG VÀ PHÂN TÍCH ĐIỂM NGHẼN")"""

replacements = [
    (old_format_p, new_format_p, "widow_control in format_p"),
    (old_add_bullet, new_add_bullet, "widow_control in add_bullet"),
    (old_sec_1_2, new_sec_1_2, "clean page break around Section 1.2")
]

for old, new, desc in replacements:
    if old in text:
        text = text.replace(old, new, 1)
        print(f"[OK] Applied: {desc}")
    else:
        print(f"[FAIL] Target not found for: {desc}")

if has_crlf:
    text = text.replace('\n', '\r\n')

with open(script_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Optimization updates saved successfully to build_master_thesis.py")
