"""
HUIT 2025 Graduation Thesis Reference Fixture Builder
Generates a fully compliant HUIT 2025 graduation thesis Word document (.docx)
satisfying 100% of the faculty formatting rules and project requirements.
Used for test harness verification, baseline comparisons, and fixture testing.
"""

import os
import io
import docx
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
from PIL import Image


def create_300dpi_sample_image(text="UML Diagram", width=600, height=400, color=(15, 43, 92)):
    """Generate an in-memory 300 DPI PNG diagram matching Executive Deep Navy palette."""
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG", dpi=(300, 300))
    buf.seek(0)
    return buf


def set_section_margins_and_geometry(section, is_cover=False, is_prelim=False, is_body=False):
    """Set margins: Left 3.5cm (1985 dxa), Top/Bottom/Right 2.5cm (1418 dxa)."""
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(3.5)
    section.right_margin = Cm(2.5)
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    
    sectPr = section._sectPr
    
    # Clean up inherited elements from python-docx cloning
    for b in sectPr.xpath("./w:pgBorders"):
        sectPr.remove(b)
    for p in sectPr.xpath("./w:pgNumType"):
        sectPr.remove(p)

    if is_cover:
        # Section 0: cornerTriangles border on first page
        border_xml = f"""
            <w:pgBorders {nsdecls('w')} w:display="firstPage">
                <w:top w:val="cornerTriangles" w:sz="15" w:space="1" w:color="auto"/>
                <w:left w:val="cornerTriangles" w:sz="15" w:space="4" w:color="auto"/>
                <w:bottom w:val="cornerTriangles" w:sz="15" w:space="1" w:color="auto"/>
                <w:right w:val="cornerTriangles" w:sz="15" w:space="4" w:color="auto"/>
            </w:pgBorders>
        """
        sectPr.append(parse_xml(border_xml))
    elif is_prelim:
        # Section 1: lowerRoman numbering starting at 1 (i, ii, iii...)
        pgnum_xml = f'<w:pgNumType {nsdecls("w")} w:fmt="lowerRoman" w:start="1"/>'
        sectPr.append(parse_xml(pgnum_xml))
    elif is_body:
        # Section 2: decimal numbering starting at 1 (1, 2, 3...)
        pgnum_xml = f'<w:pgNumType {nsdecls("w")} w:fmt="decimal" w:start="1"/>'
        sectPr.append(parse_xml(pgnum_xml))


def format_paragraph(p, font_name="Times New Roman", font_size_pt=13, is_bold=False,
                     line_spacing=1.3, space_after_pt=6, align=WD_ALIGN_PARAGRAPH.LEFT):
    """Apply HUIT 2025 paragraph formatting: Times New Roman, line spacing Multiple 1.3, 6pt after."""
    p.alignment = align
    p.paragraph_format.line_spacing = line_spacing
    p.paragraph_format.space_after = Pt(space_after_pt)
    
    for run in p.runs:
        run.font.name = font_name
        run.font.size = Pt(font_size_pt)
        run.font.bold = is_bold
        # Set rFonts for XML compatibility
        rPr = run._r.get_or_add_rPr()
        rFonts = rPr.xpath("./w:rFonts")
        if not rFonts:
            rFonts_elem = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_name}" w:hAnsi="{font_name}"/>')
            rPr.append(rFonts_elem)
        else:
            rFonts[0].set(qn("w:ascii"), font_name)
            rFonts[0].set(qn("w:hAnsi"), font_name)


def add_formatted_p(doc, text, font_name="Times New Roman", font_size_pt=13, is_bold=False,
                    line_spacing=1.3, space_after_pt=6, align=WD_ALIGN_PARAGRAPH.LEFT):
    """Add a formatted paragraph to document."""
    p = doc.add_paragraph()
    run = p.add_run(text)
    format_paragraph(p, font_name, font_size_pt, is_bold, line_spacing, space_after_pt, align)
    return p


def build_huit_compliant_thesis(output_path):
    """Build a complete HUIT 2025 compliant fixture thesis document."""
    doc = docx.Document()
    
    # 1. Update settings: w:updateFields = true
    update_fields = parse_xml(f'<w:updateFields {nsdecls("w")} w:val="true"/>')
    doc.settings.element.append(update_fields)
    
    # Set default style to Times New Roman
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(13)
    
    # ==========================================
    # SECTION 0: BÌA CHÍNH VÀ BÌA PHỤ
    # ==========================================
    sec0 = doc.sections[0]
    set_section_margins_and_geometry(sec0, is_cover=True)
    
    add_formatted_p(doc, "BỘ CÔNG THƯƠNG", font_size_pt=14, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "TRƯỜNG ĐẠI HỌC CÔNG THƯƠNG TP. HỒ CHÍ MINH", font_size_pt=14, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "KHOA CÔNG NGHỆ THÔNG TIN", font_size_pt=14, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "---------------------------------", font_size_pt=12, align=WD_ALIGN_PARAGRAPH.CENTER)
    
    add_formatted_p(doc, "\n\nKHÓA LUẬN TỐT NGHIỆP", font_size_pt=18, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "XÂY DỰNG HỆ THỐNG QUẢN LÝ CHO THUÊ THIẾT BỊ (RENTALSYSTEM)", font_size_pt=16, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    
    add_formatted_p(doc, "\nNgành: CÔNG NGHỆ THÔNG TIN", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "Chuyên ngành: KỸ THUẬT PHẦN MỀM", font_size_pt=13, align=WD_ALIGN_PARAGRAPH.CENTER)
    
    add_formatted_p(doc, "\nSinh viên thực hiện: PHAN MINH QUÂN - MSSV: 2001210779", font_size_pt=13, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "Giảng viên hướng dẫn: ThS. NGUYỄN VĂN A", font_size_pt=13, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "\nTP. HỒ CHÍ MINH, 2026", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    
    # ==========================================
    # SECTION 1: TRANG SƠ BỘ (lowerRoman i, ii, iii...)
    # ==========================================
    sec1 = doc.add_section()
    set_section_margins_and_geometry(sec1, is_prelim=True)
    
    # 1.1 Lời cảm ơn (Page i)
    add_formatted_p(doc, "LỜI CẢM ƠN", font_size_pt=16, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "Em xin bày tỏ lòng biết ơn sâu sắc đến quý Thầy Cô Khoa Công nghệ Thông tin - Trường Đại học Công Thương TP. Hồ Chí Minh đã tận tình giảng dạy và truyền đạt kiến thức quý báu trong suốt thời gian học tập tại trường...")
    doc.add_page_break()
    
    # 1.2 LỜI CAM ĐOAN (Page ii) - MUST BE AFTER Lời cảm ơn and BEFORE Nhận xét GVHD
    add_formatted_p(doc, "LỜI CAM ĐOAN", font_size_pt=16, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "Tôi xin cam đoan đây là công trình nghiên cứu của riêng tôi dưới sự hướng dẫn của Giảng viên hướng dẫn. Các số liệu, kết quả nghiên cứu trong khóa luận là hoàn toàn trung thực, khách quan và chưa từng được công bố trong bất kỳ công trình nào khác. Mọi thông tin trích dẫn đều đã được ghi rõ nguồn gốc xuất xứ theo chuẩn quy định.")
    add_formatted_p(doc, "Sinh viên cam đoan: Phan Minh Quân", font_size_pt=13, is_bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT)
    doc.add_page_break()
    
    # 1.3 Nhận xét của Giảng viên Hướng dẫn (Page iii)
    add_formatted_p(doc, "NHẬN XÉT CỦA GIẢNG VIÊN HƯỚNG DẪN", font_size_pt=16, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "Nhận xét về tinh thần, thái độ làm việc và nội dung khóa luận tốt nghiệp của sinh viên Phan Minh Quân...")
    doc.add_page_break()
    
    # 1.4 Mục lục tự động
    add_formatted_p(doc, "MỤC LỤC", font_size_pt=16, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "MỤC LỤC TỰ ĐỘNG CỦA KHÓA LUẬN...")
    doc.add_page_break()
    
    # 1.5 Danh mục từ viết tắt
    add_formatted_p(doc, "DANH MỤC TỪ VIẾT TẮT", font_size_pt=16, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "ICT: Information and Communications Technology\nEF: Entity Framework\nMVC: Model - View - Controller\nBCE: Boundary - Control - Entity\nNAPAS: National Payment Corporation of Vietnam")
    doc.add_page_break()
    
    # 1.6 Danh mục hình
    add_formatted_p(doc, "DANH MỤC HÌNH", font_size_pt=16, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "Hình 2.2.2.1. 1: Sơ đồ hoạt động quy trình đặt thuê thiết bị\nHình 2.2.2.1. 2: Sơ đồ tuần tự quy trình đặt thuê thiết bị\nHình 2.2.2.1. 3: Sơ đồ cộng tác quy trình đặt thuê thiết bị")
    doc.add_page_break()
    
    # 1.7 Danh mục bảng
    add_formatted_p(doc, "DANH MỤC BẢNG", font_size_pt=16, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "Bảng 2.2.2.1. 1: Bảng đặc tả nghiệp vụ đặt thuê thiết bị\nBảng 3.1.1. 1: Bảng từ điển dữ liệu NguoiDung")
    
    # ==========================================
    # SECTION 2: PHẦN THÂN BÀI (Arabic 1, 2, 3...)
    # ==========================================
    sec2 = doc.add_section()
    set_section_margins_and_geometry(sec2, is_body=True)
    
    # MỞ ĐẦU
    add_formatted_p(doc, "MỞ ĐẦU", font_size_pt=18, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "1. Giới thiệu đề tài: Trong bối cảnh chuyển đổi số của các doanh nghiệp cho thuê thiết bị công nghệ...")
    add_formatted_p(doc, "2. Mục tiêu đề tài: Nghiên cứu, phân tích và xây dựng hệ thống quản lý cho thuê thiết bị RentalSystem...")
    add_formatted_p(doc, "3. Đối tượng và Phạm vi: Đối tượng là quy trình quản lý cho thuê thiết bị công nghệ; phạm vi ứng dụng tại doanh nghiệp ICT Saigon...")
    doc.add_page_break()
    
    # CHƯƠNG 1
    add_formatted_p(doc, "CHƯƠNG 1: KHẢO SÁT HỆ THỐNG", font_size_pt=18, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "1.1. Giới thiệu về nơi khảo sát: Công ty TNHH TM DV ICT Sài Gòn (ICT Saigon)", font_size_pt=14, is_bold=True)
    add_formatted_p(doc, "Khảo sát thực tế tại Công ty TNHH TM DV ICT Sài Gòn (ICT Saigon), địa chỉ tại 64 Nguyễn Đình Chiểu, Phường Đa Kao, Quận 1, TP. Hồ Chí Minh. Doanh nghiệp hoạt động chuyên sâu trong lĩnh vực cho thuê máy tính, laptop và thiết bị văn phòng...")
    
    add_formatted_p(doc, "1.2. Cơ cấu tổ chức và các phân hệ", font_size_pt=14, is_bold=True)
    add_formatted_p(doc, "Hệ thống bao gồm 4 phòng ban chức năng chính: Ban Giám đốc, Phòng Kinh doanh & CSKH, Phòng Quản lý kho & Kỹ thuật, và Phòng Tài chính - Kế toán...")
    
    add_formatted_p(doc, "1.3. Quy trình nghiệp vụ truyền thống và bất cập", font_size_pt=14, is_bold=True)
    add_formatted_p(doc, "Quy trình truyền thống trải qua 6 bước thủ công dựa trên giấy tờ và bảng tính Excel. 4 điểm nghẽn chính được ghi nhận: xung đột giữ chỗ, quản lý công nợ chậm trễ, khó theo dõi sự cố máy, và sai lệch hoàn cọc...")
    
    add_formatted_p(doc, "1.4. KẾT CHƯƠNG", font_size_pt=14, is_bold=True)
    add_formatted_p(doc, "Chương 1 đã hoàn thành việc khảo sát toàn diện hiện trạng hoạt động thực tế tại Công ty TNHH TM DV ICT Sài Gòn (ICT Saigon), phân tích rõ cơ cấu tổ chức 4 phòng ban và chỉ ra 4 bất cập cốt lõi của quy trình truyền thống. Đây là cơ sở tiền đề vững chắc để tiến hành phân tích và xây dựng hệ thống mới tại Chương 2.")
    doc.add_page_break()
    
    # CHƯƠNG 2
    add_formatted_p(doc, "CHƯƠNG 2: PHÂN TÍCH HỆ THỐNG", font_size_pt=18, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "2.1. Các thuật toán và cơ chế kỹ thuật cốt lõi", font_size_pt=14, is_bold=True)
    
    add_formatted_p(doc, "2.1.1. Cơ chế kiểm soát tương tranh SemaphoreSlim", font_size_pt=13, is_bold=True)
    add_formatted_p(doc, "Hệ thống sử dụng SemaphoreSlim(1, 1) để kiểm soát tương tranh giữ chỗ kho thiết bị và đối soát thanh toán webhook, ngăn ngừa tình trạng race condition và bảo đảm tính toàn vẹn dữ liệu...")
    
    add_formatted_p(doc, "2.1.2. Thuật toán sinh mã VietQR động NAPAS 247", font_size_pt=13, is_bold=True)
    add_formatted_p(doc, "Thuật toán tạo mã QR chuẩn EMVCo Merchant-Presented Mode và NAPAS 247 Open Banking, tính toán CRC16-CCITT với đa thức 0x1021 và giá trị khởi tạo 0xFFFF...")
    
    add_formatted_p(doc, "2.1.3. Thuật toán phân kỳ trả góp và quản lý tuổi nợ tự động", font_size_pt=13, is_bold=True)
    add_formatted_p(doc, "Thuật toán phân kỳ nợ chia đều các kỳ hạn, xử lý số dư làm tròn ở kỳ cuối cùng, phân loại 4 nhóm tuổi nợ và áp dụng mức phạt trễ hạn sau 3 ngày ân hạn...")
    
    add_formatted_p(doc, "2.2. Mô hình hóa 7 quy trình nghiệp vụ", font_size_pt=14, is_bold=True)
    
    core_processes = [
        ("2.2.2.1", "Quy trình Đặt thuê thiết bị và Đặt cọc giữ chỗ"),
        ("2.2.2.2", "Quy trình Giao nhận máy và Lập biên bản bàn giao"),
        ("2.2.2.3", "Quy trình Thu hồi máy và Nghiệm thu thiết bị"),
        ("2.2.2.4", "Quy trình Gia hạn hợp đồng thuê máy"),
        ("2.2.2.5", "Quy trình Báo hỏng, Sự cố và Bảo trì tạm dừng tính tiền"),
        ("2.2.2.6", "Quy trình Thanh toán kỳ hạn và Đối soát VietQR Webhook"),
        ("2.2.2.7", "Quy trình Thanh lý hợp đồng và Quyết toán hoàn tiền cọc")
    ]
    
    for code, name in core_processes:
        add_formatted_p(doc, f"{code}. {name}", font_size_pt=13, is_bold=True)
        # Bảng đặc tả văn bản
        t = doc.add_table(rows=2, cols=2)
        t.rows[0].cells[0].text = "Thuộc tính"
        t.rows[0].cells[1].text = "Nội dung đặc tả"
        t.rows[1].cells[0].text = "Tác nhân chính"
        t.rows[1].cells[1].text = "Khách hàng, Nhân viên kinh doanh, Kỹ thuật viên"
        add_formatted_p(doc, f"Bảng {code}. 1: Bảng đặc tả nghiệp vụ {name.lower()}", font_size_pt=11, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        
        # Sơ đồ Activity
        doc.add_picture(create_300dpi_sample_image(f"Activity {code}"), width=Inches(5.0))
        add_formatted_p(doc, f"Hình {code}. 1: Sơ đồ hoạt động {name.lower()}", font_size_pt=11, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        
        # Sơ đồ Sequence
        doc.add_picture(create_300dpi_sample_image(f"Sequence {code}"), width=Inches(5.0))
        add_formatted_p(doc, f"Hình {code}. 2: Sơ đồ tuần tự {name.lower()}", font_size_pt=11, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        
        # Sơ đồ Collaboration
        doc.add_picture(create_300dpi_sample_image(f"Collaboration {code}"), width=Inches(5.0))
        add_formatted_p(doc, f"Hình {code}. 3: Sơ đồ cộng tác {name.lower()}", font_size_pt=11, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    
    add_formatted_p(doc, "2.3. Mô hình hóa chức năng", font_size_pt=14, is_bold=True)
    add_formatted_p(doc, "Hệ thống bao gồm các ca sử dụng tổng quát cho 4 nhóm vai trò: Admin, Kinh Doanh, Kỹ Thuật và Khách Hàng...")
    
    add_formatted_p(doc, "2.4. Sơ đồ lớp mức phân tích (Analysis Class Diagram)", font_size_pt=14, is_bold=True)
    add_formatted_p(doc, "Sơ đồ lớp mức phân tích xác định các thực thể và quan hệ khái niệm...")
    
    add_formatted_p(doc, "2.5. KẾT CHƯƠNG", font_size_pt=14, is_bold=True)
    add_formatted_p(doc, "Chương 2 đã hoàn thành việc nghiên cứu 3 cơ chế kỹ thuật cốt lõi (SemaphoreSlim, VietQR NAPAS 247, Thuật toán phân kỳ nợ) và mô hình hóa trọn vẹn 7 quy trình nghiệp vụ với đầy đủ bộ ba sơ đồ Activity, Sequence và Collaboration...")
    doc.add_page_break()
    
    # CHƯƠNG 3
    add_formatted_p(doc, "CHƯƠNG 3: THIẾT KẾ HỆ THỐNG", font_size_pt=18, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "3.1. Thiết kế cơ sở dữ liệu", font_size_pt=14, is_bold=True)
    add_formatted_p(doc, "3.1.1. Từ điển dữ liệu 18 bảng cơ sở dữ liệu", font_size_pt=13, is_bold=True)
    
    db_tables = [
        "NguoiDung", "VaiTro", "SanPham", "DanhMuc", "ThietBi", "HopDong",
        "ChiTietHopDong", "KyHanThanhToan", "PhieuThu", "PhieuChi", "BaoTri",
        "ChiTietBaoTri", "KhuyenMai", "LichSuSuDung", "ThongBao", "PhanCong",
        "CauHinh", "WebhookLog"
    ]
    for idx, table_name in enumerate(db_tables, 1):
        tbl = doc.add_table(rows=2, cols=3)
        tbl.rows[0].cells[0].text = "Tên cột"
        tbl.rows[0].cells[1].text = "Kiểu dữ liệu"
        tbl.rows[0].cells[2].text = "Diễn giải"
        tbl.rows[1].cells[0].text = "Id"
        tbl.rows[1].cells[1].text = "int / PK"
        tbl.rows[1].cells[2].text = f"Khóa chính bảng {table_name}"
        add_formatted_p(doc, f"Bảng 3.1.1. {idx}: Cấu trúc từ điển dữ liệu bảng {table_name}", font_size_pt=11, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    
    add_formatted_p(doc, "3.1.2. Sơ đồ cơ sở dữ liệu vật lý ERD", font_size_pt=13, is_bold=True)
    doc.add_picture(create_300dpi_sample_image("ERD Vat Ly"), width=Inches(5.5))
    add_formatted_p(doc, "Hình 3.1.2. 1: Sơ đồ cơ sở dữ liệu vật lý ERD chi tiết 18 bảng", font_size_pt=11, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    
    add_formatted_p(doc, "3.2. Thiết kế giao diện hệ thống", font_size_pt=14, is_bold=True)
    add_formatted_p(doc, "Giao diện được thiết kế theo chuẩn Cổ Điển Doanh Nghiệp (Executive Deep Navy #0f2b5c và Pure White #ffffff)...")
    
    add_formatted_p(doc, "3.3. Sơ đồ lớp mức thiết kế 3 lớp (Design Class Diagram)", font_size_pt=14, is_bold=True)
    add_formatted_p(doc, "Sơ đồ kiến trúc phân tầng 3 lớp Boundary - Control - Entity...")
    
    add_formatted_p(doc, "3.4. Thiết kế chức năng chi tiết cho 7 chức năng cốt lõi", font_size_pt=14, is_bold=True)
    core_functions = [
        ("3.4.1", "Chức năng Đặt thuê thiết bị"),
        ("3.4.2", "Chức năng Giao nhận máy"),
        ("3.4.3", "Chức năng Thu hồi máy"),
        ("3.4.4", "Chức năng Gia hạn hợp đồng"),
        ("3.4.5", "Chức năng Báo hỏng và Bảo trì"),
        ("3.4.6", "Chức năng Thanh toán kỳ hạn"),
        ("3.4.7", "Chức năng Quyết toán thanh lý")
    ]
    for code, name in core_functions:
        add_formatted_p(doc, f"{code}. {name}", font_size_pt=13, is_bold=True)
        # Sơ đồ 3 lớp BCE
        doc.add_picture(create_300dpi_sample_image(f"BCE {code}"), width=Inches(5.0))
        add_formatted_p(doc, f"Hình {code}. 1: Sơ đồ 3 lớp mức thiết kế {name.lower()}", font_size_pt=11, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        
        # Sơ đồ tuần tự 3 lớp
        doc.add_picture(create_300dpi_sample_image(f"Sequence 3L {code}"), width=Inches(5.0))
        add_formatted_p(doc, f"Hình {code}. 2: Sơ đồ tuần tự 3 lớp {name.lower()}", font_size_pt=11, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        
        # Sơ đồ cộng tác 3 lớp
        doc.add_picture(create_300dpi_sample_image(f"Collab 3L {code}"), width=Inches(5.0))
        add_formatted_p(doc, f"Hình {code}. 3: Sơ đồ cộng tác 3 lớp {name.lower()}", font_size_pt=11, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    
    add_formatted_p(doc, "3.5. KẾT CHƯƠNG", font_size_pt=14, is_bold=True)
    add_formatted_p(doc, "Chương 3 đã hoàn tất thiết kế chi tiết cơ sở dữ liệu với 18 bảng thực thể, sơ đồ vật lý ERD, chuẩn thiết kế giao diện doanh nghiệp và bộ ba sơ đồ thiết kế 3 lớp (BCE, Sequence, Collaboration) cho toàn bộ 7 chức năng trọng tâm...")
    doc.add_page_break()
    
    # CHƯƠNG 4
    add_formatted_p(doc, "CHƯƠNG 4: CÀI ĐẶT HỆ THỐNG", font_size_pt=18, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "4.1. Môi trường phát triển và cài đặt", font_size_pt=14, is_bold=True)
    add_formatted_p(doc, "Hệ thống RentalSystem được xây dựng trên nền tảng .NET 9 (C# 13), hệ quản trị cơ sở dữ liệu Microsoft SQL Server 2022, và môi trường phát triển tích hợp Visual Studio 2022...")
    
    add_formatted_p(doc, "4.2. Kiến trúc hệ thống phân tầng ASP.NET Core MVC", font_size_pt=14, is_bold=True)
    add_formatted_p(doc, "Ứng dụng tuân thủ kiến trúc phân tầng ASP.NET Core MVC tách biệt Controller, ViewModel, Service và DbContext...")
    
    add_formatted_p(doc, "4.3. Xây dựng các chức năng chính của hệ thống", font_size_pt=14, is_bold=True)
    add_formatted_p(doc, "Hình ảnh giao diện thực tế và mã nguồn xử lý logic kinh doanh của hệ thống...")
    
    add_formatted_p(doc, "4.4. KẾT CHƯƠNG", font_size_pt=14, is_bold=True)
    add_formatted_p(doc, "Chương 4 đã trình bày chi tiết môi trường phát triển .NET 9, kiến trúc phân tầng MVC và quá trình cài đặt thực tế các chức năng cốt lõi của RentalSystem...")
    doc.add_page_break()
    
    # CHƯƠNG 5
    add_formatted_p(doc, "CHƯƠNG 5: THỬ NGHIỆM VÀ TRIỂN KHAI", font_size_pt=18, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "5.1. Triển khai hệ thống", font_size_pt=14, is_bold=True)
    add_formatted_p(doc, "Triển khai hệ thống trên máy chủ Internet Information Services (IIS), cấu hình cơ sở dữ liệu SQL Server và thiết lập webhook tiếp nhận thông báo ngân hàng SePay/Casso...")
    
    add_formatted_p(doc, "5.2. Đánh giá kiểm thử và thuật toán", font_size_pt=14, is_bold=True)
    add_formatted_p(doc, "Hệ thống đã trải qua quy trình kiểm thử tự động nghiêm ngặt với bộ kiểm thử ChallengerTests gồm 540 ca kiểm thử cốt lõi (tổng 595 ca kiểm thử thực thi), đạt tỷ lệ thành công 100% (595 PASSED, 0 FAILED). Kiểm thử chịu tải với 100 tác vụ song song trên SemaphoreSlim chứng minh 0 deadlock, thời gian phản hồi dưới 2 giây...")
    
    add_formatted_p(doc, "5.3. Thử nghiệm và khảo sát người dùng", font_size_pt=14, is_bold=True)
    add_formatted_p(doc, "Khảo sát thực tế theo thang đo Likert 5 mức độ với cỡ mẫu N = 50 người dùng thuộc 4 nhóm vai trò (15 Khách hàng cá nhân, 15 Doanh nghiệp, 10 Quản lý kho, 10 Kỹ thuật viên). Kết quả đánh giá trên 6 tiêu chí đạt điểm trung bình 4.57/5.0 với tỷ lệ hài lòng chung 94.6%...")
    
    doc.add_picture(create_300dpi_sample_image("Likert Survey Chart"), width=Inches(5.0))
    add_formatted_p(doc, "Hình 5.3. 1: Biểu đồ kết quả khảo sát mức độ hài lòng người dùng Likert N=50", font_size_pt=11, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    
    add_formatted_p(doc, "5.4. KẾT CHƯƠNG", font_size_pt=14, is_bold=True)
    add_formatted_p(doc, "Chương 5 đã chứng minh tính tin cậy và khả năng ứng dụng thực tiễn của RentalSystem thông qua kết quả kiểm thử tự động 540+ ca test đạt 100% PASS, kiểm thử chịu tải SemaphoreSlim an toàn và khảo sát người dùng Likert N=50 với mức độ hài lòng vượt trội 94.6%...")
    doc.add_page_break()
    
    # KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN
    add_formatted_p(doc, "KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", font_size_pt=18, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "1. Kết luận: Đề tài đã hoàn thành xuất sắc các mục tiêu nghiên cứu và phát triển hệ thống RentalSystem theo chuẩn HUIT 2025...")
    add_formatted_p(doc, "2. Hướng phát triển: Tích hợp trí tuệ nhân tạo (AI) dự báo nhu cầu thuê và quản lý lịch bảo trì chủ động...")
    doc.add_page_break()
    
    # DANH MỤC TÀI LIỆU THAM KHẢO
    add_formatted_p(doc, "DANH MỤC TÀI LIỆU THAM KHẢO", font_size_pt=16, is_bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    add_formatted_p(doc, "[1] Microsoft Corporation, 'ASP.NET Core Documentation & Architecture Guide', 2024.\n[2] NAPAS, 'VietQR Technical Specification & Standards', 2023.\n[3] Khoa CNTT - HUIT, 'Quy định trình bày Khóa luận tốt nghiệp Đại học', 2025.")
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc.save(output_path)
    return output_path


if __name__ == "__main__":
    out = "d:/DoAnCuNhan/tests/fixtures/huit_thesis_fixture.docx"
    build_huit_compliant_thesis(out)
    print(f"Fixture generated successfully at {out}")
