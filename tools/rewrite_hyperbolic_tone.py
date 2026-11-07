# -*- coding: utf-8 -*-
"""
Script to tone down hyperbolic AI buzzwords in tools/build_master_thesis.py.
"""
import sys, os, re

sys.stdout.reconfigure(encoding='utf-8')

script_path = os.path.join(os.path.dirname(__file__), 'build_master_thesis.py')
with open(script_path, 'r', encoding='utf-8') as f:
    code = f.read()

has_crlf = '\r\n' in code
code = code.replace('\r\n', '\n')

replacements = [
    # 1. Section 3.2.2 Admin UI (Call out specifically by user)
    (
        'add_heading_3(doc, "3.2.2. Thiết kế giao diện quản trị Admin theo chuẩn Executive Deep Navy")',
        'add_heading_3(doc, "3.2.2. Thiết kế giao diện phân hệ quản trị (Admin)")'
    ),
    (
        'add_p(doc, "Giao diện quản trị Admin tuân thủ tuyệt đối chuẩn thiết kế Cổ Điển Doanh Nghiệp (Executive Navy & Pure White):")',
        'add_p(doc, "Giao diện quản trị Admin được thiết kế theo phong cách tối giản, sử dụng tông màu chủ đạo là xanh đen (Deep Navy) kết hợp nền trắng để đảm bảo độ tương phản rõ ràng, giúp người dùng dễ dàng quan sát và thao tác dữ liệu:")'
    ),
    (
        'add_bullet(doc, "Bảng màu chủ đạo: Deep Navy #0f2b5c sang trọng, thanh lịch; Pure White #ffffff làm nền thẻ dữ liệu; viền mảnh Slate #e2e8f0.")',
        'add_bullet(doc, "Bảng màu sử dụng: Tông xanh đen (#0f2b5c) được dùng cho thanh điều hướng (Sidebar) và tiêu đề bảng; nền trắng (#ffffff) và viền xám nhạt (#e2e8f0) được áp dụng cho các khung chứa dữ liệu để tạo sự ngăn nắp.")'
    ),
    (
        'add_bullet(doc, "Sử dụng các class ngữ nghĩa đóng gói trong classic-navy.css: .stat-card, .admin-card, .admin-table, .action-btn, .btn-navy.")',
        'add_bullet(doc, "Bố cục bảng biểu: Sử dụng các lớp CSS ngữ nghĩa trong file classic-navy.css (.admin-card, .admin-table, .stat-card) nhằm chuẩn hóa cấu trúc hiển thị bảng và nút bấm chức năng đồng bộ.")'
    ),
    (
        'add_bullet(doc, "Hệ thống huy hiệu trạng thái Executive Dot Pill (.status-pill) với chấm chỉ thị màu trầm tinh tế, loại bỏ hoàn toàn các khối màu neon chói lọi của Bootstrap.")',
        'add_bullet(doc, "Huy hiệu trạng thái: Sử dụng các huy hiệu dạng nhãn nhỏ (.status-pill) với màu sắc nhẹ dịu để phân biệt trạng thái của đơn thuê và thiết bị, hạn chế sử dụng các gam màu quá chói.")'
    ),

    # 2. Introduction & Objectives
    (
        'add_bullet(doc, "Khảo sát và mô hình hóa toàn diện các quy trình nghiệp vụ cốt lõi bằng bộ công cụ chuẩn UML (Activity, Sequence, Collaboration) và kiến trúc thiết kế 3 lớp (Boundary – Control – Entity).")',
        'add_bullet(doc, "Khảo sát và mô hình hóa các quy trình nghiệp vụ cốt lõi bằng bộ công cụ UML (Activity, Sequence, Collaboration) và kiến trúc thiết kế 3 lớp (Boundary – Control – Entity).")'
    ),
    (
        'add_bullet(doc, "Xây dựng hệ thống hoàn chỉnh trên nền tảng Web (ASP.NET Core 9 MVC) tối ưu Responsive Design (RWD) hiển thị mượt mà trên cả trình duyệt máy tính và điện thoại thông minh, hỗ trợ toàn bộ 4 phân hệ người dùng (Khách hàng, Kinh doanh, Kỹ thuật, Quản trị).")',
        'add_bullet(doc, "Xây dựng hệ thống trên nền tảng Web (ASP.NET Core 9 MVC) hỗ trợ Responsive Web Design (RWD) tương thích trên máy tính và thiết bị di động, phục vụ 4 phân hệ người dùng (Khách hàng, Kinh doanh, Kỹ thuật, Quản trị).")'
    ),
    (
        'add_bullet(doc, "Thiết kế cơ sở dữ liệu quan hệ chuẩn mực gồm 18 bảng thực thể, tối ưu hóa các chỉ mục và ràng buộc toàn vẹn dữ liệu.")',
        'add_bullet(doc, "Thiết kế cơ sở dữ liệu quan hệ gồm 18 bảng thực thể, thiết lập các chỉ mục và ràng buộc toàn vẹn dữ liệu.")'
    ),
    (
        'add_bullet(doc, "Phát triển giao diện người dùng theo chuẩn phong cách Cổ Điển Doanh Nghiệp (Executive Deep Navy #0f2b5c và Pure White #ffffff).")',
        'add_bullet(doc, "Xây dựng giao diện web với tông màu xanh đen (#0f2b5c) và nền trắng, bố cục rõ ràng, thuận tiện cho người dùng thao tác.")'
    ),
    (
        'add_bullet(doc, "Thực hiện kiểm thử chức năng toàn diện cho các ca sử dụng cốt lõi, kiểm tra tích hợp luồng tương tranh, đối soát thanh toán và gọi API di động, đảm bảo tính đúng đắn và độ ổn định của hệ thống.")',
        'add_bullet(doc, "Thực hiện kiểm thử chức năng cho các ca sử dụng cốt lõi, kiểm tra luồng tương tranh, đối soát thanh toán và gọi API, đánh giá tính đúng đắn và độ ổn định của hệ thống.")'
    ),

    # 3. Chapter 2 Architecture & Debt
    (
        'add_p(doc, "Nhằm tạo nền tảng backend vững chắc và sẵn sàng tích hợp với các ứng dụng máy khách di động trong tương lai, hệ thống xây dựng bộ RESTful API chuẩn mực tuân thủ khuyến nghị OpenAPI 3.0 (Swagger UI):")',
        'add_p(doc, "Để hỗ trợ trao đổi dữ liệu với các ứng dụng máy khách và mở rộng tích hợp trong tương lai, hệ thống xây dựng các dịch vụ RESTful API tuân thủ đặc tả OpenAPI 3.0 (Swagger UI):")'
    ),
    (
        'add_p(doc, "Song song với việc sinh lịch trả góp, hệ thống vận hành cơ chế phân loại tuổi nợ tự động (Debt Aging Management) theo chuẩn quản trị tài chính doanh nghiệp, phân chia các khoản nợ thành 4 cấp độ (Tier 0 – 4) dựa trên số ngày quá hạn:")',
        'add_p(doc, "Song song với việc sinh lịch trả góp, hệ thống vận hành cơ chế phân loại tuổi nợ tự động (Debt Aging Management), phân chia các khoản nợ thành các nhóm tuổi nợ (Tier 0 – 4) dựa trên số ngày quá hạn để theo dõi thu hồi nợ:")'
    ),

    # 4. Chapter 3 DB & Constraints & Conclusion
    (
        'add_p(doc, "Cơ sở dữ liệu của RentalSystem được thiết kế chuẩn hóa mức 3NF trên hệ quản trị Microsoft SQL Server 2022, bao gồm 18 bảng thực thể đáp ứng toàn bộ các yêu cầu nghiệp vụ khắt khe:")',
        'add_p(doc, "Cơ sở dữ liệu của RentalSystem được thiết kế chuẩn hóa mức 3NF trên hệ quản trị Microsoft SQL Server 2022, bao gồm 18 bảng thực thể đáp ứng các yêu cầu lưu trữ dữ liệu của hệ thống:")'
    ),
    (
        'add_p(doc, "Để đảm bảo tính toàn vẹn tham chiếu (Referential Integrity) và ngăn chặn việc xóa nhầm dữ liệu lịch sử tài chính, RentalSystem áp dụng chiến lược cấu hình hành vi xóa khóa ngoại (DeleteBehavior) nghiêm ngặt trong DbContext:")',
        'add_p(doc, "Để đảm bảo tính toàn vẹn tham chiếu (Referential Integrity) và ngăn chặn việc xóa nhầm dữ liệu lịch sử tài chính, RentalSystem cấu hình hành vi xóa khóa ngoại (DeleteBehavior) trong DbContext:")'
    ),
    (
        'add_bullet(doc, "Quan hệ HopDong -> PhieuThu & PhieuChi: Cấu hình DeleteBehavior.Restrict. Tuyệt đối không cho phép xóa hợp đồng nếu đã phát sinh chứng từ tài chính thu/chi nhằm phục vụ công tác thanh tra tài chính và kiểm toán dữ liệu.")',
        'add_bullet(doc, "Quan hệ HopDong -> PhieuThu & PhieuChi: Cấu hình DeleteBehavior.Restrict. Không cho phép xóa trực tiếp hợp đồng nếu đã phát sinh chứng từ tài chính thu/chi nhằm bảo lưu chứng từ kế toán.")'
    ),
    (
        'add_p(doc, "Trong Chương 3, nhóm nghiên cứu đã hoàn thành bản thiết kế kỹ thuật chi tiết cho hệ thống RentalSystem, bao gồm: (1) Lược đồ cơ sở dữ liệu quan hệ 18 bảng với đầy đủ ràng buộc toàn vẹn khóa ngoại; (2) Thiết kế giao diện trực quan phân hệ Khách hàng và Quản trị theo chuẩn bảng màu Cổ Điển Doanh Nghiệp; (3) Mô hình hóa kiến trúc 3 lớp (BCE, Sequence và Collaboration) cho 7 chức năng trọng tâm. Các đặc tả thiết kế này là cơ sở trực tiếp để triển khai mã nguồn trên nền tảng ASP.NET Core tại Chương 4.")',
        'add_p(doc, "Trong Chương 3, nhóm nghiên cứu đã hoàn thành bản thiết kế kỹ thuật chi tiết cho hệ thống RentalSystem, bao gồm: (1) Lược đồ cơ sở dữ liệu quan hệ 18 bảng với đầy đủ ràng buộc toàn vẹn khóa ngoại; (2) Bố cục giao diện phân hệ Khách hàng và Quản trị trực quan, rõ ràng; (3) Mô hình hóa kiến trúc 3 lớp (BCE, Sequence và Collaboration) cho 7 chức năng trọng tâm. Các đặc tả thiết kế này là cơ sở kỹ thuật để triển khai mã nguồn trên nền tảng ASP.NET Core tại Chương 4.")'
    ),

    # 5. Chapter 4 Implementation
    (
        'add_p(doc, "Ứng dụng tuân thủ nghiêm ngặt mô hình kiến trúc phân tầng ASP.NET Core MVC kết hợp nguyên lý SOLID:")',
        'add_p(doc, "Ứng dụng được tổ chức theo mô hình kiến trúc phân tầng ASP.NET Core MVC kết hợp các nguyên lý hướng đối tượng SOLID:")'
    ),
    (
        'add_p(doc, "Để bảo vệ hệ thống trước các cuộc tấn công tải tệp độc hại (Web Shell) và tấn công từ chối dịch vụ bộ nhớ (Base64 Memory DoS), hệ thống áp dụng cơ chế phòng vệ chuyên sâu nhiều lớp nghiêm ngặt:")',
        'add_p(doc, "Để hạn chế nguy cơ tải tệp không hợp lệ và tấn công từ chối dịch vụ bộ nhớ (Base64 Memory DoS), hệ thống áp dụng các bước kiểm tra tệp tin chặt chẽ:")'
    ),
    (
        'add_p(doc, "Để phục vụ trao đổi dữ liệu hai chiều với các ứng dụng máy khách và mở rộng hệ sinh thái di động, hệ thống cài đặt hệ thống API chuẩn mực theo kiến trúc RESTful (OpenAPI 3.0 / Swagger UI) gồm 6 cụm Controller độc lập:")',
        'add_p(doc, "Để phục vụ trao đổi dữ liệu với các ứng dụng máy khách và mở rộng hệ sinh thái di động, hệ thống cài đặt các endpoint API theo kiến trúc RESTful (OpenAPI 3.0 / Swagger UI) gồm 6 cụm Controller:")'
    ),
    (
        'add_p(doc, "Tại DatabaseController.cs (khu vực Admin, phân quyền nghiêm ngặt Authorize(Roles = \'Admin\')), hệ thống cài đặt hai quy trình sao lưu và phục hồi:")',
        'add_p(doc, "Tại DatabaseController.cs (khu vực Admin, áp dụng thuộc tính phân quyền Authorize(Roles = \'Admin\')), hệ thống cài đặt hai quy trình sao lưu và phục hồi:")'
    ),

    # 6. Conclusion
    (
        'add_p(doc, "Sau thời gian tập trung nghiên cứu lý thuyết, khảo sát thực tế và triển khai mã nguồn, đề tài \'Xây dựng hệ thống quản lý cho thuê thiết bị (RentalSystem)\' đã hoàn thành các mục tiêu đặt ra theo đúng chuẩn mực của Khoa Công nghệ Thông tin - Trường Đại học Công Thương TP. Hồ Chí Minh (HUIT). Những kết quả chính đạt được bao gồm:")',
        'add_p(doc, "Sau thời gian tập trung nghiên cứu lý thuyết, khảo sát thực tế và triển khai mã nguồn, đề tài \'Xây dựng hệ thống quản lý cho thuê thiết bị (RentalSystem)\' đã hoàn thành các mục tiêu đặt ra theo đề cương chi tiết của Khoa Công nghệ Thông tin - Trường Đại học Công Thương TP. Hồ Chí Minh (HUIT). Những kết quả chính đạt được bao gồm:")'
    ),
    (
        'add_bullet(doc, "Về mặt học thuật và phương pháp luận: Khảo sát thực tế mô hình vận hành và các điểm nghẽn nghiệp vụ của lĩnh vực cho thuê thiết bị công nghệ; mô hình hóa chuẩn mực 7 quy trình nghiệp vụ trọng tâm bằng hệ thống sơ đồ UML (Activity, Sequence, Collaboration) và kiến trúc thiết kế 3 lớp (Boundary – Control – Entity).")',
        'add_bullet(doc, "Về mặt học thuật và phương pháp luận: Khảo sát mô hình vận hành và các điểm nghẽn nghiệp vụ của lĩnh vực cho thuê thiết bị công nghệ; mô hình hóa 7 quy trình nghiệp vụ trọng tâm bằng hệ thống sơ đồ UML (Activity, Sequence, Collaboration) và kiến trúc thiết kế 3 lớp (Boundary – Control – Entity).")'
    ),
    (
        'add_bullet(doc, "Về mặt xây dựng sản phẩm: Phát triển hoàn chỉnh ứng dụng web trên nền tảng .NET 9, kiến trúc phân tầng ASP.NET Core MVC, cơ sở dữ liệu Microsoft SQL Server 2022 gồm 18 bảng chuẩn hóa 3NF, và giao diện chuẩn Cổ Điển Doanh Nghiệp (Executive Deep Navy #0f2b5c).")',
        'add_bullet(doc, "Về mặt xây dựng sản phẩm: Xây dựng ứng dụng web trên nền tảng .NET 9, kiến trúc phân tầng ASP.NET Core MVC, cơ sở dữ liệu Microsoft SQL Server 2022 gồm 18 bảng chuẩn hóa 3NF, và giao diện web với tông màu xanh đen (#0f2b5c) bố trí gọn gàng, thuận tiện thao tác.")'
    ),
    (
        'add_bullet(doc, "Về mặt kiểm thử và đánh giá: Hệ thống được kiểm thử chức năng toàn diện với 12 ca kiểm thử trọng tâm (TC-01 đến TC-12), kiểm chứng an toàn luồng tương tranh SemaphoreSlim và xử lý an toàn bản tin Webhook đối soát thanh toán, bảo đảm hệ thống vận hành tin cậy và chính xác.")',
        'add_bullet(doc, "Về mặt kiểm thử và đánh giá: Hệ thống được kiểm thử chức năng với 14 ca kiểm thử trọng tâm (TC-01 đến TC-14), kiểm tra luồng tương tranh SemaphoreSlim và xử lý bản tin Webhook đối soát thanh toán, đánh giá hệ thống vận hành ổn định và chính xác.")'
    ),
    (
        'add_p(doc, "Hệ thống RentalSystem đã giải quyết được các điểm nghẽn nghiêm trọng nhất của phương thức quản lý truyền thống:")',
        'add_p(doc, "Hệ thống RentalSystem giúp khắc phục các bất cập của phương thức quản lý thủ công truyền thống:")'
    ),
    (
        'add_bullet(doc, "Về nền tảng người dùng: Hệ thống đã thiết lập kiến trúc RESTful API chuẩn mực phục vụ kết nối di động; hướng nghiên cứu tiếp theo sẽ nâng cấp ứng dụng di động lên mô hình Offline-First đồng bộ nền ngầm và tối ưu hóa thư viện quét mã vạch Barcode/QR tốc độ cao cho nhân viên giao nhận tại kho bãi.")',
        'add_bullet(doc, "Về nền tảng người dùng: Hệ thống đã thiết lập kiến trúc RESTful API phục vụ kết nối di động; hướng nghiên cứu tiếp theo sẽ nâng cấp ứng dụng di động lên mô hình Offline-First đồng bộ nền ngầm và tích hợp thư viện quét mã vạch Barcode/QR tốc độ cao cho nhân viên giao nhận tại kho bãi.")'
    ),
]

successful_replacements = 0
for old, new in replacements:
    if old in code:
        code = code.replace(old, new, 1)
        successful_replacements += 1
    else:
        print(f"[WARN] Target not found:\n  {old[:80]}...")

if has_crlf:
    code = code.replace('\n', '\r\n')

with open(script_path, 'w', encoding='utf-8') as f:
    f.write(code)

print(f"\nCompleted: {successful_replacements}/{len(replacements)} hyperbolic passages rewritten cleanly!")
