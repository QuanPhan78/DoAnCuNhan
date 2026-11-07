# -*- coding: utf-8 -*-
import sys, os, re

sys.stdout.reconfigure(encoding='utf-8')

script_path = os.path.join(os.path.dirname(__file__), 'build_master_thesis.py')
with open(script_path, 'r', encoding='utf-8') as f:
    code = f.read()

# Normalize to \n for robust string replacement
has_crlf = '\r\n' in code
code = code.replace('\r\n', '\n')

# 1. Add sanitize_mojibake and update add_p
mojibake_func = '''def sanitize_mojibake(text):
    """Strips any non-Vietnamese Latin-1 extended characters (mojibake) from text."""
    if not text:
        return ""
    # Strip garbage characters: ¡ ¢ £ ¤ ¥ ¦ § ¨ © ª « ¬ ® ¯ ° ± ² ³ ´ µ ¶ · ¸ ¹ º » ¼ ½ ¾ ¿ × ÷ Þ ß þ
    # Keep standard ASCII and Vietnamese Unicode NFC
    clean = re.sub(r'[\u00a1-\u00bf\u00d7\u00f7\u00de\u00df\u00fe]', '', text)
    return clean


def add_p('''

if 'def sanitize_mojibake' not in code:
    assert 'def add_p(' in code, "def add_p not found"
    code = code.replace('def add_p(', mojibake_func, 1)
    code = code.replace('if text:\n        p.add_run(text)', 'if text:\n        p.add_run(sanitize_mojibake(text))', 1)
    code = code.replace('run = p.add_run(f"{prefix}{text}")', 'run = p.add_run(f"{prefix}{sanitize_mojibake(text)}")', 1)
    print("Added sanitize_mojibake and updated add_p / add_bullet")

# 2. Add vAlign center in set_table_styling
old_tcpr_shd = '''        tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="0F2B5C"/>'))'''
new_tcpr_shd = '''        tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="0F2B5C"/>'))
        if not tcPr.xpath("./w:vAlign"):
            tcPr.append(parse_xml(f'<w:vAlign {nsdecls("w")} w:val="center"/>'))'''
if old_tcpr_shd in code and './w:vAlign' not in code:
    code = code.replace(old_tcpr_shd, new_tcpr_shd, 1)
    print("Added vAlign center to table headers")

old_data_shd = '''                tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_fill}"/>'))'''
new_data_shd = '''                tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{bg_fill}"/>'))
            if not tcPr.xpath("./w:vAlign"):
                tcPr.append(parse_xml(f'<w:vAlign {nsdecls("w")} w:val="center"/>'))'''
if old_data_shd in code:
    code = code.replace(old_data_shd, new_data_shd, 1)
    print("Added vAlign center to table data rows")

# Also sanitize table cells in add_table_with_caption
old_tbl_cells = '''    for c_idx, h_text in enumerate(headers):
        table.rows[0].cells[c_idx].text = h_text

    for r_idx, row_data in enumerate(data_rows):
        for c_idx, val in enumerate(row_data):
            table.rows[r_idx + 1].cells[c_idx].text = str(val)'''

new_tbl_cells = '''    for c_idx, h_text in enumerate(headers):
        table.rows[0].cells[c_idx].text = sanitize_mojibake(h_text)

    for r_idx, row_data in enumerate(data_rows):
        for c_idx, val in enumerate(row_data):
            table.rows[r_idx + 1].cells[c_idx].text = sanitize_mojibake(str(val))'''
if old_tbl_cells in code:
    code = code.replace(old_tbl_cells, new_tbl_cells, 1)
    print("Added sanitize_mojibake to table cells")

# 3. Fix Table 0.4.1 (remove CLO6, set col_widths=[1.8, 2.7, 7.0, 3.5])
if '("0.4", "1", "Bảng tiến độ kế hoạch thực hiện và phân công nhiệm vụ 12 tuần (CLO6)"),' in code:
    code = code.replace(
        '("0.4", "1", "Bảng tiến độ kế hoạch thực hiện và phân công nhiệm vụ 12 tuần (CLO6)"),',
        '("0.4", "1", "Bảng tiến độ kế hoạch thực hiện và phân công nhiệm vụ 12 tuần"),'
    )
    print("Updated Table 0.4.1 in master tables catalog")

old_tbl_call = '''    add_table_with_caption(doc, "0.4", 1, "Bảng tiến độ kế hoạch thực hiện và phân công nhiệm vụ 12 tuần (CLO6)",
                           ["Tuần", "Khung thời gian", "Nội dung công việc triển khai theo đề cương", "Phân công trách nhiệm"],
                           schedule_data, col_widths=[1.5, 3.2, 7.3, 3.0])'''

new_tbl_call = '''    add_table_with_caption(doc, "0.4", 1, "Bảng tiến độ kế hoạch thực hiện và phân công nhiệm vụ 12 tuần",
                           ["Tuần", "Khung thời gian", "Nội dung công việc triển khai theo đề cương", "Phân công trách nhiệm"],
                           schedule_data, col_widths=[1.8, 2.7, 7.0, 3.5])'''

if old_tbl_call in code:
    code = code.replace(old_tbl_call, new_tbl_call, 1)
    print("Updated Table 0.4.1 call with col_widths=[1.8, 2.7, 7.0, 3.5]")

# 4. Section 2.2.2: Add page break between 7 core processes
old_core_loop = '''    for code, name, desc, actors, pre, steps, alt, post in core_processes:
        add_heading_4(doc, f"{code}. {name}")'''

new_core_loop = '''    for idx, (code, name, desc, actors, pre, steps, alt, post) in enumerate(core_processes):
        if idx > 0:
            doc.add_page_break()
        add_heading_4(doc, f"{code}. {name}")'''

if old_core_loop in code:
    code = code.replace(old_core_loop, new_core_loop, 1)
    print("Added page breaks between 7 core processes in Section 2.2.2")

# 5. Section 3.4: Enhance 7 functions 3-layer design with structured text and page breaks
old_sec34_block = '''    functions_info = [
        ("3.4.1", "Chức năng Đăng ký & Xác thực người dùng",
         "Thiết kế 3 lớp xử lý nhận diện danh tính, phân quyền Cookie Claims và điều hướng phân hệ thông minh."),
        ("3.4.2", "Chức năng Đặt thuê máy & Kiểm tra tồn kho (SemaphoreSlim)",
         "Thiết kế 3 lớp xử lý khóa tương tranh đa luồng, kiểm tra giao thoa khoảng ngày và giữ chỗ thiết bị an toàn."),
        ("3.4.3", "Chức năng Thanh toán đặt cọc qua VietQR động NAPAS 247",
         "Thiết kế 3 lớp sinh chuỗi TLV EMVCo, bắt Webhook ngân hàng và đối soát phiếu thu tự động."),
        ("3.4.4", "Chức năng Bàn giao & Ký biên bản bàn giao máy",
         "Thiết kế 3 lớp thu nhận chữ ký số HTML5 Canvas, kiểm soát bộ nhớ Base64 và cập nhật trạng thái serial."),
        ("3.4.5", "Chức năng Báo cáo sự cố & Phân công bảo trì thiết bị",
         "Thiết kế 3 lớp tiếp nhận phiếu lỗi, điều phối kỹ thuật viên và kiểm soát cơ chế tạm dừng tính tiền thuê."),
        ("3.4.6", "Chức năng Gia hạn hợp đồng & Phân kỳ nợ",
         "Thiết kế 3 lớp kiểm tra lịch thuê tương lai, tính toán dồn dư kỳ cuối và cập nhật phân kỳ tài chính."),
        ("3.4.7", "Chức năng Trả máy, nghiệm thu & Hoàn trả tiền cọc",
         "Thiết kế 3 lớp kiểm định thu hồi máy, đối trừ công nợ hư hại và chi hoàn cọc qua phiếu chi tự động.")
    ]

    for code, name, desc in functions_info:
        add_heading_3(doc, f"{code}. {name}")
        add_p(doc, f"Mô tả kiến trúc thiết kế: {desc}")

        # Diagram 1: BCE
        bce_img = f"figures/hinh_{code.replace('.', '_')}_1_bce_{get_slug(code)}.png"
        add_figure_with_caption(doc, code, 1, f"Sơ đồ 3 lớp mức thiết kế {name} (BCE)", bce_img, width_cm=14.5)

        # Diagram 2: Sequence 3-layer
        seq_img = f"figures/hinh_{code.replace('.', '_')}_2_sequence_3lop_{get_slug(code)}.png"
        add_figure_with_caption(doc, code, 2, f"Sơ đồ tuần tự 3 lớp {name}", seq_img, width_cm=14.5)

        # Diagram 3: Collab 3-layer
        col_img = f"figures/hinh_{code.replace('.', '_')}_3_collab_3lop_{get_slug(code)}.png"
        add_figure_with_caption(doc, code, 3, f"Sơ đồ cộng tác 3 lớp {name}", col_img, width_cm=14.5)'''

new_sec34_block = '''    functions_info = [
        ("3.4.1", "Chức năng Đăng ký & Xác thực người dùng",
         "Thiết kế 3 lớp xử lý nhận diện danh tính, phân quyền Cookie Claims và điều hướng phân hệ thông minh.",
         "Giao diện Đăng ký / Đăng nhập (RegisterView, LoginView) tiếp nhận biểu mẫu và xác thực đầu vào.",
         "AccountController và CookieAuthenticationHandler kiểm tra băm mật khẩu, thiết lập phiên bảo mật.",
         "Bảng NguoiDung và VaiTro lưu trữ hồ sơ tài khoản và vai trò phân quyền."),

        ("3.4.2", "Chức năng Đặt thuê máy & Kiểm tra tồn kho (SemaphoreSlim)",
         "Thiết kế 3 lớp xử lý khóa tương tranh đa luồng, kiểm tra giao thoa khoảng ngày và giữ chỗ thiết bị an toàn.",
         "Giao diện Giỏ hàng / Đặt thuê (CheckoutView) tiếp nhận thông số gói thuê và lịch nhận máy.",
         "CartController phối hợp static SemaphoreSlim(1,1) ngăn chặn Race Condition và cấp phát serial tạm.",
         "Bảng SanPham, ThietBi và HopDong lưu trữ chi tiết đơn thuê và đổi trạng thái máy sang Giữ chỗ."),

        ("3.4.3", "Chức năng Thanh toán đặt cọc qua VietQR động NAPAS 247",
         "Thiết kế 3 lớp sinh chuỗi TLV EMVCo, bắt Webhook ngân hàng và đối soát phiếu thu tự động.",
         "Giao diện Thanh toán (PaymentView) hiển thị mã QR động chứa số tiền cọc và bộ đếm ngược.",
         "PaymentController và OpenBankingWebhookService tiếp nhận IPN, xác thực chữ ký và gạch nợ tự động.",
         "Bảng PhieuThu và KyHanThanhToan ghi nhận phiếu thu và cập nhật trạng thái hợp đồng đã cọc."),

        ("3.4.4", "Chức năng Bàn giao & Ký biên bản bàn giao máy",
         "Thiết kế 3 lớp thu nhận chữ ký số HTML5 Canvas, kiểm soát bộ nhớ Base64 và cập nhật trạng thái serial.",
         "Giao diện Bàn giao (HandoverView) cung cấp vùng ký Canvas và tiếp nhận hồ sơ CCCD/ảnh máy.",
         "HopDongController kiểm tra magic bytes tệp tải lên, giải mã chữ ký ảnh PNG và sinh biên bản bàn giao.",
         "Bảng BienBanBanGiao và ThietBi lưu biên bản pháp lý và đổi trạng thái máy sang Đang thuê."),

        ("3.4.5", "Chức năng Báo cáo sự cố & Phân công bảo trì thiết bị",
         "Thiết kế 3 lớp tiếp nhận phiếu lỗi, điều phối kỹ thuật viên và kiểm soát cơ chế tạm dừng tính tiền thuê.",
         "Giao diện Báo lỗi sự cố (IncidentTicketView) cho phép khách hàng gửi mô tả kèm ảnh lỗi.",
         "BaoTriController phân công kỹ thuật viên, kích hoạt cờ TamDungTinhTien nếu bảo trì vượt quá 24h.",
         "Bảng PhieuBaoTri và PhanCongCongViec lưu lịch sử khắc phục sự cố và điều phối nhân sự."),

        ("3.4.6", "Chức năng Gia hạn hợp đồng & Phân kỳ nợ",
         "Thiết kế 3 lớp kiểm tra lịch thuê tương lai, tính toán dồn dư kỳ cuối và cập nhật phân kỳ tài chính.",
         "Giao diện Gia hạn (ExtensionRequestView) và Quản trị công nợ (CongNoAdminView) phục vụ lập và duyệt gia hạn.",
         "HopDongController và DebtCalculationHelper kiểm tra xung đột lịch thuê, tính toán phân kỳ trả góp bổ sung.",
         "Bảng YeuCauGiaHan, HopDong và KyHanThanhToan lưu trữ kỳ hạn mới và cập nhật ngày kết thúc hợp đồng."),

        ("3.4.7", "Chức năng Trả máy, nghiệm thu & Hoàn trả tiền cọc",
         "Thiết kế 3 lớp kiểm định thu hồi máy, đối trừ công nợ hư hại và chi hoàn cọc qua phiếu chi tự động.",
         "Giao diện Nghiệm thu (ReturnMachineView) và Chi tiết hợp đồng (HopDongDetailsView) phục vụ nghiệm thu và hoàn cọc.",
         "HopDongController thực hiện đối trừ công nợ tồn đọng, bồi thường linh kiện và duyệt chi hoàn cọc.",
         "Bảng BienBanBanGiao, PhieuChi, HopDong và ThietBi ghi nhận tất toán hợp đồng và đưa máy về kho sẵn sàng.")
    ]

    for idx, (code, name, desc, bnd, ctrl, ent) in enumerate(functions_info):
        if idx > 0:
            doc.add_page_break()
        add_heading_3(doc, f"{code}. {name}")
        add_p(doc, f"Mô tả kiến trúc thiết kế: {desc}")
        add_p(doc, "Kiến trúc 3 lớp (Boundary - Control - Entity) của chức năng được phân rã như sau:")
        add_bullet(doc, f"Tầng Biên (Boundary): {bnd}")
        add_bullet(doc, f"Tầng Điều khiển (Control): {ctrl}")
        add_bullet(doc, f"Tầng Thực thể (Entity): {ent}")

        # Diagram 1: BCE
        bce_img = f"figures/hinh_{code.replace('.', '_')}_1_bce_{get_slug(code)}.png"
        add_figure_with_caption(doc, code, 1, f"Sơ đồ 3 lớp mức thiết kế {name} (BCE)", bce_img, width_cm=14.5)

        # Diagram 2: Sequence 3-layer
        seq_img = f"figures/hinh_{code.replace('.', '_')}_2_sequence_3lop_{get_slug(code)}.png"
        add_figure_with_caption(doc, code, 2, f"Sơ đồ tuần tự 3 lớp {name}", seq_img, width_cm=14.5)

        # Diagram 3: Collab 3-layer
        col_img = f"figures/hinh_{code.replace('.', '_')}_3_collab_3lop_{get_slug(code)}.png"
        add_figure_with_caption(doc, code, 3, f"Sơ đồ cộng tác 3 lớp {name}", col_img, width_cm=14.5)'''

if old_sec34_block in code:
    code = code.replace(old_sec34_block, new_sec34_block, 1)
    print("Enhanced Section 3.4 with 3-layer architecture details and page breaks")

# Restore original CRLF
if has_crlf:
    code = code.replace('\n', '\r\n')

with open(script_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("ALL CHANGES SUCCESSFULLY SAVED TO tools/build_master_thesis.py!")
