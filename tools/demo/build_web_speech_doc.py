"""Build the Vietnamese read-aloud Web demonstration script with python-docx."""
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "outputs/Kich_ban_trinh_bay_demo_Web_RentalSystem.docx"
doc = Document()
section = doc.sections[0]
section.page_width, section.page_height = Inches(8.5), Inches(11)
section.top_margin, section.bottom_margin = Inches(.70), Inches(.65)
section.left_margin, section.right_margin = Inches(.80), Inches(.80)
section.footer_distance = Inches(.30)


def font(style, size, bold=False, italic=False):
    style.font.name = "Arial"
    style.font.size = Pt(size)
    style.font.bold, style.font.italic = bold, italic
    style.font.color.rgb = RGBColor(0, 0, 0)
    rpr = style.element.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.insert(0, fonts)
    for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
        fonts.set(qn("w:" + attr), "Arial")
    for attr in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
        fonts.attrib.pop(qn("w:" + attr), None)
    ppr = style.element.find(qn("w:pPr"))
    if ppr is not None:
        for border in list(ppr.findall(qn("w:pBdr"))):
            ppr.remove(border)


font(doc.styles["Normal"], 14)
normal = doc.styles["Normal"].paragraph_format
normal.line_spacing = 1.16
normal.space_after = Pt(10)
normal.widow_control = True
font(doc.styles["Title"], 22, True)
doc.styles["Title"].paragraph_format.space_after = Pt(10)
font(doc.styles["Subtitle"], 12)
doc.styles["Subtitle"].paragraph_format.space_after = Pt(12)
font(doc.styles["Heading 1"], 17, True)
doc.styles["Heading 1"].paragraph_format.space_before = Pt(0)
doc.styles["Heading 1"].paragraph_format.space_after = Pt(8)
doc.styles["Heading 1"].paragraph_format.keep_with_next = True
font(doc.styles["Heading 2"], 13, True)
doc.styles["Heading 2"].paragraph_format.space_before = Pt(9)
doc.styles["Heading 2"].paragraph_format.space_after = Pt(5)
doc.styles["Heading 2"].paragraph_format.keep_with_next = True
for name, size, bold, italic in [("Cue", 11.5, False, True), ("Time", 12, True, False), ("Prep", 11.5, False, False)]:
    s = doc.styles.add_style(name, 1)
    s.base_style = doc.styles["Normal"]
    font(s, size, bold, italic)
    s.paragraph_format.space_after = Pt(8)
    s.paragraph_format.line_spacing = 1.10

doc.core_properties.title = "Kịch bản trình bày demo RentalSystem trên Web"
doc.core_properties.subject = "Lời đọc và thao tác cho phần demo bảo vệ khóa luận"
doc.core_properties.author = "Nhóm thực hiện RentalSystem"
doc.core_properties.keywords = "RentalSystem, demo Web, kịch bản thuyết trình"

footer = section.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
run = footer.add_run("Demo Web RentalSystem  |  ")
run.font.name, run.font.size = "Arial", Pt(10)
field = OxmlElement("w:fldSimple")
field.set(qn("w:instr"), "PAGE")
footer._p.append(field)


def p(text, style=None):
    return doc.add_paragraph(text, style)


def cue(text):
    p("Thao tác: " + text, "Cue")


def speech(*paragraphs):
    for text in paragraphs:
        p(text)


def stage(number, title, timing, new_page=True):
    if new_page:
        doc.add_page_break()
    doc.add_heading(f"Phần {number} {title}", level=1)
    p(timing, "Time")


p("Kịch bản trình bày demo\nRentalSystem trên Web", "Title")
p("Lời đọc cho một người trình bày trong 10 đến 12 phút", "Subtitle")
p("Đọc các đoạn chữ thường bên dưới. Dòng in nghiêng là lời nhắc thao tác, không đọc thành tiếng. Mốc thời gian tính từ lúc bắt đầu demo; dành 30 giây cuối để dự phòng.", "Prep")
stage(1, "Giới thiệu và chọn thiết bị", "0:00 - 1:30", new_page=False)
cue("Mở sẵn Web ở danh mục sản phẩm, đăng nhập bằng other@demo.invalid. Mật khẩu demo: Demo@123. Chọn Laptop Demo Dell Latitude 5430.")
speech(
    "Kính thưa quý thầy cô, sau đây em xin trình bày chương trình quản lý cho thuê thiết bị RentalSystem trên giao diện Web.",
    "Em sẽ minh họa từ lúc khách hàng gửi yêu cầu thuê, nhân viên tiếp nhận hợp đồng, đến quá trình báo sự cố, xử lý kỹ thuật và đánh giá dịch vụ. Sau đó, em trình bày phần báo cáo và sao lưu dữ liệu.",
    "Trước tiên, em đang sử dụng tài khoản khách hàng Demo Bình. Tại danh mục sản phẩm, khách hàng có thể xem tên thiết bị, cấu hình và giá thuê trước khi quyết định đặt thuê.",
    "Trong tình huống này, khách hàng cần thuê một laptop để phục vụ công việc trong bảy ngày. Em chọn dòng Dell Latitude 5430 có giá một trăm bảy mươi nghìn đồng mỗi ngày, sau đó thêm một máy vào giỏ hàng."
)
p("Câu chuyển", "Heading 2")
speech("Sau khi chọn thiết bị, em chuyển sang bước nhập thời gian và địa chỉ nhận máy.")

stage(2, "Tạo yêu cầu thuê và tiếp nhận hợp đồng", "1:30 - 4:00")
cue("Giỏ hàng: chọn 1 máy. Nhập ngày nhận D và ngày trả D+7; ví dụ 04/11 đến 11/11. Địa chỉ: Phòng demo, 123 Đường Minh Họa, TP.HCM. Gửi yêu cầu và ghi lại mã đơn thực tế.")
speech(
    "Tại giỏ hàng, em kiểm tra lại số lượng là một máy. Tiếp theo, em chọn ngày nhận và ngày trả cách nhau bảy ngày, đồng thời nhập địa chỉ giao thiết bị.",
    "Với đơn giá một trăm bảy mươi nghìn đồng một ngày, tiền thuê dự kiến là một triệu một trăm chín mươi nghìn đồng. Em đối chiếu số tiền này trước khi gửi yêu cầu.",
    "Sau khi gửi thành công, hệ thống chuyển sang bước hoàn thiện hồ sơ và ký hợp đồng. Ở thời điểm này, yêu cầu đã được tạo nhưng chưa bàn giao máy."
)
cue("Chuyển sang hồ sơ trình duyệt Kinh doanh Demo, mở Đơn thuê máy, tải lại và mở đúng mã đơn vừa tạo. Nếu cần minh họa ràng buộc, thử Giao máy và đọc thông báo từ chối khi chưa đủ hồ sơ.")
speech(
    "Bây giờ, em chuyển sang tài khoản nhân viên kinh doanh để kiểm tra yêu cầu vừa được khách hàng gửi.",
    "Trong danh sách hợp đồng, nhân viên có thể xem đúng khách hàng Demo Bình, thời gian thuê bảy ngày và số tiền một triệu một trăm chín mươi nghìn đồng. Đơn đang ở trạng thái chờ duyệt và chưa ghi nhận khoản thu tiền.",
    "Trước khi giao máy, nhân viên cần kiểm tra hồ sơ và chữ ký của các bên. Hệ thống có ràng buộc để từ chối bàn giao khi những thông tin bắt buộc này chưa đầy đủ."
)

stage(3, "Xem hợp đồng đang thuê và báo sự cố", "4:00 - 6:00")
cue("Ở Web nhân viên, mở hợp đồng số 1, chỉ serial DEMO-LAP-001, chữ ký hai bên và biên bản bàn giao số 1. Sau đó chuyển sang tài khoản customer@demo.invalid của khách hàng Demo An.")
speech(
    "Để minh họa giai đoạn sau bàn giao, em chuyển sang hợp đồng số một của khách hàng Demo An. Đây là một hợp đồng khác, đã được chuẩn bị sẵn hồ sơ và đang trong thời gian cho thuê.",
    "Thiết bị trong hợp đồng được quản lý bằng số serial cụ thể. Nhờ đó, nhân viên có thể đối chiếu đúng máy đã bàn giao, thay vì chỉ theo dõi chung theo tên dòng sản phẩm.",
    "Tại đây, hệ thống lưu thông tin chữ ký của khách hàng, chữ ký đối chiếu của nhân viên và biên bản bàn giao. Toàn bộ hồ sơ trong buổi trình bày này là dữ liệu giả lập."
)
cue("Tài khoản khách hàng Demo An: Hợp đồng của tôi, chọn Báo Lỗi ở hợp đồng số 1. Chọn DEMO-LAP-001; nhập Máy không kết nối Wi-Fi; mức độ Tiêu chuẩn; gửi yêu cầu. Ghi lại mã phiếu mới.")
speech(
    "Giả sử trong quá trình sử dụng, khách hàng gặp tình trạng máy không kết nối được Wi-Fi. Em mở hợp đồng đang thuê và gửi yêu cầu hỗ trợ cho đúng thiết bị này.",
    "Khách hàng mô tả tình trạng lỗi, chọn mức độ cần hỗ trợ và gửi phiếu. Sau khi gửi thành công, phiếu xuất hiện trong lịch sử báo cáo sự cố để khách hàng tiếp tục theo dõi."
)
p("Câu chuyển", "Heading 2")
speech("Tiếp theo, em chuyển sang Web quản trị để tiếp nhận và phân công xử lý phiếu vừa tạo.")

stage(4, "Phân công và xử lý bảo trì", "6:00 - 8:30")
cue("Quản trị Demo: Bảo trì và Sự cố, mở đúng phiếu mới. Chọn Kỹ thuật Demo, giữ trạng thái 1 Mới tiếp nhận, ghi chú Đã phân công kỹ thuật Demo và lưu.")
speech(
    "Tại danh sách bảo trì và sự cố, quản trị thấy phiếu mới với mã hợp đồng, số serial thiết bị, thời gian báo lỗi và nội dung khách hàng đã nhập.",
    "Em kiểm tra lại các thông tin này để xác nhận phiếu thuộc đúng hợp đồng số một. Sau đó, em phân công cho kỹ thuật viên phụ trách và lưu thông tin tiếp nhận."
)
cue("Chuyển sang hồ sơ Kỹ thuật Demo. Mở đúng mã phiếu ở danh sách Bảo trì và Sự cố. Chọn trạng thái 2 Đang sửa chữa, nhập Đang kiểm tra kết nối Wi-Fi và lưu.")
speech(
    "Khi bắt đầu xử lý, kỹ thuật viên cập nhật trạng thái đang sửa chữa. Phần ghi chú dùng để lưu nội dung kiểm tra và hướng xử lý thiết bị.",
    "Trong tình huống minh họa, nguyên nhân là cấu hình kết nối mạng. Kỹ thuật viên cấu hình lại kết nối, sau đó kiểm tra khả năng truy cập và hoạt động của máy."
)
cue("Chọn trạng thái 3 Đã sửa xong. Nguyên nhân: Cấu hình mạng. Linh kiện: Không thay linh kiện. Kết quả: Đã cấu hình lại kết nối, kiểm tra hoạt động ổn định. Giữ chi phí và bồi thường bằng 0; không chọn thu phí hoặc giảm trừ tiền thuê. Lưu.")
speech(
    "Sau khi xử lý, em cập nhật kết quả là đã cấu hình lại kết nối và kiểm tra máy hoạt động ổn định. Tình huống này không thay linh kiện và không phát sinh phí sửa chữa hoặc bồi thường cho khách hàng.",
    "Phiếu được chuyển sang trạng thái đã sửa xong, chờ khách hàng kiểm tra và nghiệm thu. Lịch sử trên Web giúp tra cứu quá trình tiếp nhận và xử lý của phiếu."
)

stage(5, "Khách hàng đánh giá và nghiệm thu", "8:30 - 10:00")
cue("Quay lại tài khoản Demo An trên Web. Mở Lịch sử sự cố, tải lại và chọn đúng mã phiếu vừa xử lý; xem Chi tiết. Không dùng phiếu số 3 để gửi đánh giá mới vì phiếu đó đã có kết quả thử.")
speech(
    "Em quay lại tài khoản khách hàng để kiểm tra kết quả xử lý. Sau khi tải lại trang, khách hàng có thể xem phiếu đã sửa xong và nội dung kỹ thuật viên ghi nhận.",
    "Qua phần này, khách hàng theo dõi được yêu cầu đã được xử lý đến đâu và kết quả xử lý là gì. Chức năng đánh giá chỉ được sử dụng sau khi kỹ thuật viên hoàn thành sửa chữa."
)
cue("Trong Chi tiết phiếu, chọn 5 sao; nhập Hỗ trợ nhanh, máy hoạt động ổn định; bấm Gửi Đánh Giá Dịch Vụ. Tải lại trang để kiểm tra kết quả đã lưu.")
speech(
    "Giả sử khách hàng đã kiểm tra và hài lòng với kết quả, em chọn mức đánh giá năm sao và nhập nhận xét hỗ trợ nhanh, máy hoạt động ổn định. Sau khi gửi, đánh giá được lưu vào phiếu bảo trì.",
    "Em tải lại trang để đối chiếu kết quả. Điểm đánh giá và nhận xét vẫn được hiển thị, cho thấy phản hồi đã được lưu cùng hồ sơ xử lý."
)
cue("Bấm xác nhận nghiệm thu trên trang Chi tiết phiếu. Ghi ý kiến Đã kiểm tra máy hoạt động ổn định nếu biểu mẫu yêu cầu. Kiểm tra trạng thái 5 Đã nghiệm thu và Đóng phiếu.")
speech(
    "Tiếp theo, khách hàng xác nhận nghiệm thu thiết bị. Phiếu được chuyển sang trạng thái đã nghiệm thu và đóng, hoàn tất tình huống hỗ trợ trong phần trình bày này."
)
p("Câu chuyển", "Heading 2")
speech("Sau cùng, em chuyển sang tài khoản quản trị để xem dữ liệu được tổng hợp thành báo cáo như thế nào.")

stage(6, "Báo cáo sao lưu và kết thúc", "10:00 - 11:30")
cue("Quản trị Demo: mở Thống kê báo cáo. Chọn kỳ có dữ liệu; bộ demo chuẩn bị ngày 04/11/2026 dùng từ 05/09/2026 đến 04/11/2026. Bấm Lọc, chỉ các chỉ tiêu đang hiển thị và xuất Excel.")
speech(
    "Tại phần thống kê, quản trị có thể chọn khoảng thời gian cần xem báo cáo. Em chọn khoảng thời gian có dữ liệu để minh họa các chỉ tiêu đang hiển thị, gồm doanh thu, tình trạng thiết bị và kết quả xử lý kỹ thuật.",
    "Ngoài việc xem trực tiếp trên Web, quản trị có thể xuất báo cáo Excel để lưu trữ và tiếp tục tổng hợp. Em thực hiện xuất báo cáo và kiểm tra tệp được tải xuống."
)
cue("Nếu còn thời gian, mở Công nợ và chỉ hợp đồng số 4 có kỳ quá hạn. Sau đó mở Sao lưu CSDL, kiểm tra tên RentalSystemDemoDB và tải bản sao lưu JSON. Không thực hiện khôi phục trong lượt demo chính.")
speech(
    "Ở phần công nợ, nhân viên có thể tra cứu các kỳ thanh toán và những khoản đến hạn hoặc quá hạn để theo dõi việc thu hồi công nợ.",
    "Quản trị cũng có chức năng sao lưu dữ liệu. Em tải bản sao lưu JSON của cơ sở dữ liệu demo. Khi chuẩn bị bản dự phòng, các tệp ảnh và chữ ký được giữ kèm với dữ liệu để có thể sử dụng đầy đủ khi cần khôi phục.",
    "Qua phần trình diễn, em đã minh họa việc gửi và tiếp nhận yêu cầu thuê, quản lý thiết bị theo hợp đồng, xử lý sự cố và ghi nhận đánh giá của khách hàng. Các thông tin này tiếp tục được sử dụng trong báo cáo quản lý.",
    "Em xin kết thúc phần demo chương trình và sẵn sàng trả lời câu hỏi của quý thầy cô."
)
p("Nếu thời gian sắp hết", "Heading 2")
p("Rút phần xem công nợ và mở tệp Excel. Giữ thao tác gửi đánh giá, nghiệm thu và câu kết; giới thiệu sao lưu bằng một câu.", "Cue")

doc.add_page_break()
doc.add_heading("Tài khoản và câu trả lời dự phòng", level=1)
p("Phần này dùng để chuẩn bị trước khi trình bày và tham khảo khi được hỏi.", "Prep")
p("Ngày nhận máy phải là ngày tập hoặc ngày trình bày thực tế, hoặc một ngày sau đó. Chọn ngày trả cách ngày nhận đúng 7 ngày; các ngày 04/11 và 11/11 trong kịch bản chỉ là ví dụ.", "Prep")
doc.add_heading("Tài khoản cần mở sẵn", level=2)
p("Mật khẩu chung của bộ dữ liệu demo là Demo@123. Mở từng vai trò bằng hồ sơ trình duyệt riêng để tránh dùng chung phiên đăng nhập.", "Prep")
table = doc.add_table(rows=1, cols=2)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
table.autofit = False
table.columns[0].width, table.columns[1].width = Inches(2.30), Inches(4.60)
table.rows[0].cells[0].text, table.rows[0].cells[1].text = "Vai trò sử dụng", "Tài khoản"
for role, email in [
    ("Khách đặt thuê Demo Bình", "other@demo.invalid"),
    ("Khách bảo trì Demo An", "customer@demo.invalid"),
    ("Nhân viên kinh doanh", "sale@demo.invalid"),
    ("Kỹ thuật viên", "tech@demo.invalid"),
    ("Quản trị viên", "admin@demo.invalid"),
]:
    cells = table.add_row().cells
    cells[0].text, cells[1].text = role, email
for ri, row in enumerate(table.rows):
    trpr = row._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    trpr.append(cant_split)
    if ri == 0:
        trpr.append(OxmlElement("w:tblHeader"))
    for ci, cell in enumerate(row.cells):
        cell.width = Inches((2.30, 4.60)[ci])
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        tcpr = cell._tc.get_or_add_tcPr()
        borders = OxmlElement("w:tcBorders")
        for edge in ("top", "left", "bottom", "right"):
            node = OxmlElement("w:" + edge)
            for attr, value in [("val", "single"), ("sz", "5"), ("color", "D9D9D9")]:
                node.set(qn("w:" + attr), value)
            borders.append(node)
        tcpr.append(borders)
        margins = OxmlElement("w:tcMar")
        for edge in ("top", "bottom", "left", "right"):
            node = OxmlElement("w:" + edge)
            node.set(qn("w:w"), "90")
            node.set(qn("w:type"), "dxa")
            margins.append(node)
        tcpr.append(margins)
        if ri == 0:
            shade = OxmlElement("w:shd")
            shade.set(qn("w:fill"), "E7EEF5")
            tcpr.append(shade)
        for para in cell.paragraphs:
            para.paragraph_format.space_after = Pt(0)
            para.paragraph_format.line_spacing = 1.05
            for run in para.runs:
                run.font.name, run.font.size = "Arial", Pt(11)
                run.bold = ri == 0

doc.add_heading("Khi được hỏi về dữ liệu chuẩn bị sẵn", level=2)
speech("Em sử dụng dữ liệu giả lập để trình bày các giai đoạn nghiệp vụ. Yêu cầu thuê mới được tạo trực tiếp, còn hợp đồng số một đã có hồ sơ bàn giao để minh họa quá trình sử dụng và bảo trì.")
doc.add_heading("Khi khách Demo An không đặt thuê mới được", level=2)
speech("Tài khoản Demo An có công nợ quá hạn nên Web chặn đặt thuê mới theo ràng buộc nghiệp vụ. Em dùng tài khoản Demo Bình cho tình huống đặt thuê, còn Demo An dùng để minh họa bảo trì hợp đồng đang thuê.")
doc.add_heading("Khi thao tác bị gián đoạn", level=2)
speech("Em xin chuyển sang kết quả đã lưu để tiếp tục minh họa bước này. Sau phần trình bày, em sẽ kiểm tra lại thao tác vừa bị gián đoạn.")
p("Nhắc trước buổi trình bày: HD-0009 và phiếu số 3 là kết quả đã có từ lượt kiểm tra Web; khi tạo lại phải đọc mã mới trên màn hình. Phiếu số 3 đã được đánh giá 5 sao và nghiệm thu. Không đọc cố định các mã này như thể vừa tạo mới.", "Prep")

TARGET.parent.mkdir(parents=True, exist_ok=True)
doc.save(TARGET)
print(TARGET)
