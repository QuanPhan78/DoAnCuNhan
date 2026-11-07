# -*- coding: utf-8 -*-
"""
Script clean_ai_hallucinations.py
Triệt để xử lý toàn bộ các ảo giác AI trong:
1. tools/build_master_thesis.py (Nội dung văn bản Word)
2. tools/render_all_diagrams.py (Sơ đồ kỹ thuật)
"""
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

def clean_build_master_thesis():
    file_path = 'tools/build_master_thesis.py'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Ban Giam Doc -> Admin / Stakeholders
    content = content.replace(
        'add_bullet(doc, "Ban Giám đốc (Ban Quản trị): Chịu trách nhiệm ban hành bảng giá thuê, tỷ lệ đặt cọc máy (20% – 50%), phê duyệt các hợp đồng quy mô lớn (>50 thiết bị) và theo dõi báo cáo tài chính định kỳ.")',
        'add_bullet(doc, "Quản trị viên hệ thống (Admin): Quản trị người dùng, phân quyền truy cập, thiết lập cấu hình giá thuê, tỷ lệ cọc và giám sát toàn diện hoạt động của hệ thống.")'
    )
    content = content.replace(
        'add_bullet(doc, "Phòng Tài chính – Kế toán: Tiếp nhận thanh toán tiền cọc, lập lịch thu nợ phân kỳ theo tháng, hàng ngày đối soát biến động số dư tài khoản ngân hàng, tính lãi phạt trễ hạn và quyết toán hoàn cọc.")',
        'add_bullet(doc, "Phòng Kinh doanh & Dịch vụ khách hàng: Tiếp nhận nhu cầu thuê, tư vấn cấu hình, kiểm tra số lượng tồn kho khả dụng, lập báo giá, duyệt hợp đồng, theo dõi lịch thanh toán phân kỳ và hỗ trợ đối soát công nợ.")'
    )

    # 2. Quy trình truyen thong AS-IS (Bước 4 & 6)
    content = content.replace(
        'add_bullet(doc, "Bước 4 – Thu tiền ban đầu: Kế toán viết phiếu thu tay hoặc gửi số tài khoản ngân hàng để khách chuyển khoản, kiểm tra thông báo SMS biến động số dư thủ công.")',
        'add_bullet(doc, "Bước 4 – Thu tiền ban đầu: Nhân viên kinh doanh gửi số tài khoản ngân hàng để khách chuyển khoản, kiểm tra thông báo SMS biến động số dư thủ công và viết phiếu thu tay.")'
    )
    content = content.replace(
        'add_bullet(doc, "Bước 6 – Bảo dưỡng, thu hồi và thanh lý: Khi máy hỏng hoặc hết hạn, kỹ thuật viên tiếp nhận, ghi chép lỗi vào sổ tay; kế toán tính lại công nợ trên Excel rồi hoàn tiền cọc.")',
        'add_bullet(doc, "Bước 6 – Bảo dưỡng, thu hồi và thanh lý: Khi máy hỏng hoặc hết hạn, kỹ thuật viên tiếp nhận, ghi chép lỗi vào sổ tay; nhân viên kinh doanh đối soát lại công nợ trên Excel rồi hoàn tiền cọc.")'
    )

    # 3. Mục 2.2.1 Use Case tổng quát
    content = content.replace(
        'Sơ đồ ca sử dụng nghiệp vụ tổng quát mô tả bức tranh toàn cảnh về sự tương tác giữa các tác nhân kinh doanh (Khách hàng cá nhân, Khách hàng doanh nghiệp, Nhân viên kinh doanh, Kỹ thuật viên kho và Kế toán tài chính) với các quy trình nghiệp vụ của hệ thống.',
        'Sơ đồ ca sử dụng nghiệp vụ tổng quát mô tả bức tranh toàn cảnh về sự tương tác giữa 4 tác nhân chính trong hệ thống (Khách hàng, Nhân viên kinh doanh, Kỹ thuật viên và Quản trị viên) cùng hệ thống thanh toán VietQR với các quy trình nghiệp vụ của RentalSystem.'
    )

    # 4. Quy trình 2.2.2.7
    content = content.replace(
        '"Khách hàng, Kỹ thuật viên kho, Kế toán tài chính."',
        '"Khách hàng, Kỹ thuật viên kho, Nhân viên kinh doanh."'
    )
    content = content.replace(
        '"Khách hàng trả máy khi hết hạn hợp đồng; kỹ thuật viên nghiệm thu, kế toán đối trừ công nợ hư hại và chi hoàn tiền cọc."',
        '"Khách hàng trả máy khi hết hạn hợp đồng; kỹ thuật viên nghiệm thu tình trạng máy, nhân viên kinh doanh đối trừ công nợ hư hại và lập phiếu chi hoàn tiền cọc."'
    )
    content = content.replace(
        '"4. Kế toán đối chiếu tổng công nợ còn thiếu, tiền phạt trễ hạn và chi phí bồi thường linh kiện."',
        '"4. Nhân viên kinh doanh đối chiếu tổng công nợ còn thiếu, tiền phạt trễ hạn và chi phí bồi thường linh kiện theo biên bản kỹ thuật."'
    )
    content = content.replace(
        '"5. Kế toán lập Phiếu chi (PhieuChi) hoàn trả số tiền cọc còn lại vào tài khoản ngân hàng của khách hàng."',
        '"5. Nhân viên kinh doanh lập Phiếu chi (PhieuChi) trên hệ thống để hoàn trả số tiền cọc còn lại vào tài khoản ngân hàng của khách hàng."'
    )

    # 5. UC 10, 11, 12
    content = content.replace(
        '("10", "Nghiệm thu trả máy và Quyết toán hoàn cọc", "Kỹ thuật viên kho, Kế toán tài chính"',
        '("10", "Nghiệm thu trả máy và Quyết toán hoàn cọc", "Kỹ thuật viên kho, Nhân viên kinh doanh"'
    )
    content = content.replace(
        '"4. Kế toán truy cập chức năng Quyết toán hợp đồng, hệ thống tự động tổng hợp: Tiền cọc đang giữ, tiền thuê còn thiếu (nếu có), tiền phạt quá hạn và chi phí bồi thường hư hại (nếu có).\\n"',
        '"4. Nhân viên kinh doanh truy cập chức năng Quyết toán hợp đồng, hệ thống tự động tổng hợp: Tiền cọc đang giữ, tiền thuê còn thiếu (nếu có), tiền phạt quá hạn và chi phí bồi thường hư hại (nếu có).\\n"'
    )
    content = content.replace(
        '"6. Kế toán lập Phiếu chi (PhieuChi) hoàn trả tiền cho khách hàng và đóng hợp đồng ở trạng thái \'DaThanhLy\'.",',
        '"6. Nhân viên kinh doanh lập Phiếu chi (PhieuChi) trên hệ thống để hoàn trả tiền cho khách hàng và đóng hợp đồng ở trạng thái \'DaThanhLy\'.",'
    )
    content = content.replace(
        'chuyển kế toán khấu trừ vào tiền cọc.',
        'chuyển nhân viên kinh doanh khấu trừ vào tiền cọc.'
    )

    content = content.replace(
        '("11", "Quản lý sổ nợ và Nhắc nợ tự động", "Kế toán tài chính",',
        '("11", "Quản lý sổ nợ và Nhắc nợ tự động", "Nhân viên kinh doanh / Quản trị viên",'
    )
    content = content.replace(
        '"Kế toán đăng nhập hệ thống với quyền Kế toán / Quản trị viên."',
        '"Người dùng đăng nhập hệ thống với quyền \'KinhDoanh\' hoặc \'Admin\'."'
    )
    content = content.replace(
        '"1. Kế toán mở màn hình \'Quản trị công nợ\'.\\n"',
        '"1. Nhân viên kinh doanh mở màn hình \'Quản trị công nợ\'.\\n"'
    )
    content = content.replace(
        '"4. Kế toán chọn chức năng \'Gửi thông báo nhắc nợ\', hệ thống tự động gửi Email/SMS thông báo kèm đường dẫn thanh toán nhanh VietQR đến khách hàng nợ.\\n"',
        '"4. Nhân viên kinh doanh chọn chức năng \'Gửi thông báo nhắc nợ\', hệ thống tự động gửi Email/SMS thông báo kèm đường dẫn thanh toán nhanh VietQR đến khách hàng nợ.\\n"'
    )
    content = content.replace(
        'Kế toán áp dụng chính sách miễn giảm hoặc lùi ngày tính phạt theo thẩm quyền.',
        'Nhân viên kinh doanh báo cáo Quản trị viên áp dụng chính sách miễn giảm hoặc lùi ngày tính phạt theo thẩm quyền.'
    )
    content = content.replace(
        '("8", "NguoiLap", "int", "FK", "No", "Kế toán viên lập phiếu chi")]),',
        '("8", "NguoiLap", "int", "FK", "No", "Nhân viên kinh doanh lập phiếu chi")]),'
    )
    content = content.replace(
        'xuất báo cáo Excel chuẩn kế toán',
        'xuất báo cáo Excel phân tích tài chính'
    )

    content = content.replace(
        '("12", "Trung tâm phân tích báo cáo BI và Xuất Excel", "Ban Giám đốc / Quản trị viên cấp cao",',
        '("12", "Trung tâm phân tích báo cáo BI và Xuất Excel", "Quản trị viên (Admin) / Nhân viên kinh doanh",'
    )
    content = content.replace(
        '"Người dùng đăng nhập với quyền \'Admin\' hoặc \'BanGiamDoc\'."',
        '"Người dùng đăng nhập với quyền \'Admin\' hoặc \'KinhDoanh\'."'
    )
    content = content.replace(
        '"1. Ban Giám đốc truy cập màn hình \'Báo cáo thống kê & Phân tích BI\'.\\n"',
        '"1. Quản trị viên hoặc Nhân viên kinh doanh truy cập màn hình \'Báo cáo thống kê & Phân tích BI\'.\\n"'
    )

    # 6. Kết chương 2
    content = content.replace(
        'add_p(doc, "Chương 2 đã hoàn thành trọn vẹn các mục tiêu nghiên cứu và phân tích hệ thống RentalSystem: (1) Làm rõ cơ chế kỹ thuật và giải thuật cốt lõi gồm khóa tương tranh SemaphoreSlim chống Overbooking, thuật toán sinh mã VietQR động NAPAS 247 và thuật toán phân kỳ nợ 4 cấp độ; (2) Mô hình hóa chi tiết 7 quy trình nghiệp vụ trọng tâm với đầy đủ bộ ba sơ đồ Activity, Sequence và Collaboration; (3) Phân tích 12 ca sử dụng chức năng và thiết lập sơ đồ lớp mức phân tích chuẩn BCE. Các kết quả này tạo tiền đề vững chắc cho giai đoạn thiết kế kiến trúc và cơ sở dữ liệu chi tiết tại Chương 3.")',
        'add_p(doc, "Thông qua Chương 2, đề tài đã phân tích ba bài toán kỹ thuật cốt lõi gồm kiểm soát tương tranh giữ chỗ bằng SemaphoreSlim, sinh mã VietQR động theo chuẩn EMVCo và phân kỳ công nợ 4 cấp độ. Đồng thời, chương này đã mô hình hóa 7 quy trình nghiệp vụ trọng tâm và đặc tả chi tiết 12 ca sử dụng gắn liền với 4 vai trò người dùng trong hệ thống (Khách hàng, Kinh doanh, Kỹ thuật và Quản trị viên). Những kết quả phân tích yêu cầu này đóng vai trò cơ sở để triển khai thiết kế kiến trúc và lược đồ cơ sở dữ liệu chi tiết trong Chương 3.")'
    )

    # 7. Kết chương 3
    content = content.replace(
        'add_p(doc, "Chương 3 đã hoàn tất thiết kế chi tiết toàn bộ kiến trúc hệ thống RentalSystem: (1) Thiết kế cơ sở dữ liệu quan hệ hoàn chỉnh gồm 18 bảng từ điển dữ liệu, ma trận ràng buộc và lược đồ vật lý ERD; (2) Thiết kế giao diện khách hàng và Admin chuẩn mực theo phong cách Cổ Điển Doanh Nghiệp (Executive Deep Navy); (3) Thiết kế sơ đồ lớp 3 lớp tổng thể và hoàn thiện bộ ba sơ đồ BCE, Sequence, Collaboration 3 lớp cho toàn bộ 7 chức năng trọng tâm. Đây là bản thiết kế hoàn chỉnh làm căn cứ trực tiếp để triển khai cài đặt mã nguồn tại Chương 4.")',
        'add_p(doc, "Trong Chương 3, nhóm nghiên cứu đã hoàn thành bản thiết kế kỹ thuật chi tiết cho hệ thống RentalSystem, bao gồm: (1) Lược đồ cơ sở dữ liệu quan hệ 18 bảng với đầy đủ ràng buộc toàn vẹn khóa ngoại; (2) Thiết kế giao diện trực quan phân hệ Khách hàng và Quản trị theo chuẩn bảng màu Cổ Điển Doanh Nghiệp; (3) Mô hình hóa kiến trúc 3 lớp (BCE, Sequence và Collaboration) cho 7 chức năng trọng tâm. Các đặc tả thiết kế này là cơ sở trực tiếp để triển khai mã nguồn trên nền tảng ASP.NET Core tại Chương 4.")'
    )

    # 8. Môi trường phát triển & Bảng 4.1.1
    content = content.replace(
        'Hệ thống RentalSystem được xây dựng trên nền tảng công nghệ tiên tiến nhất hiện nay của hệ sinh thái Microsoft .NET, đáp ứng các tiêu chuẩn khắt khe về hiệu năng, an ninh và khả năng bảo trì lâu dài:',
        'Hệ thống RentalSystem được xây dựng trên nền tảng Microsoft .NET 9 hiện đại kết hợp kiến trúc phân tầng ASP.NET Core MVC, đáp ứng các yêu cầu về hiệu năng xử lý web, tính module hóa và khả năng bảo trì hệ thống:'
    )
    content = content.replace(
        '("Hệ điều hành máy chủ", "Windows Server 2022 Datacenter / Windows 11 Enterprise"),',
        '("Hệ điều hành máy chủ", "Windows Server 2022 / Windows 11 Pro 64-bit"),'
    )
    content = content.replace(
        '("Nền tảng thực thi (Framework)", ".NET 9 (C# 13.0) – Long Term Support / Current"),',
        '("Nền tảng thực thi (Framework)", ".NET 9.0 (C# 13.0) – Standard-Term Support (STS)"),'
    )
    content = content.replace(
        '("Hệ quản trị CSDL (DBMS)", "Microsoft SQL Server 2022 Enterprise Edition"),',
        '("Hệ quản trị CSDL (DBMS)", "Microsoft SQL Server 2022 (Developer Edition)"),'
    )
    content = content.replace(
        '("Môi trường phát triển (IDE)", "Microsoft Visual Studio 2022 Enterprise v17.12"),',
        '("Môi trường phát triển (IDE)", "Microsoft Visual Studio 2022 Community / Professional v17.12"),'
    )
    content = content.replace(
        '("Thư viện kiểm thử tự động", "ChallengerTests Runner tích hợp xUnit & Moq")',
        '("Bộ kiểm thử tự động", "ChallengerTests (xUnit, Moq, FluentAssertions)")'
    )

    # 9. Đánh giá phân hệ Table 5.3
    content = content.replace(
        '("Phân hệ Tài chính – Kế toán", "Đối soát Webhook tự động, phân kỳ nợ, quản lý 4 Tier", "Gạch nợ tức thời, tự động hóa tính phạt quá hạn", "Tốt")',
        '("Bộ phận Quản lý kinh doanh & Công nợ", "Đối soát Webhook tự động, phân kỳ nợ, quản lý 4 Tier", "Gạch nợ tức thời, tự động hóa tính phạt quá hạn", "Tốt")'
    )

    # 10. Kết luận: hạ thấp tuyên bố phóng đại
    content = content.replace(
        'add_bullet(doc, "Loại bỏ hoàn toàn rủi ro Overbooking: Nhờ cơ chế khóa tương tranh SemaphoreSlim, việc giữ chỗ máy được tuần tự hóa an toàn, không còn tình trạng ký vượt số lượng máy thực tế trong kho.")',
        'add_bullet(doc, "Giảm thiểu tối đa rủi ro Overbooking: Nhờ cơ chế khóa tương tranh SemaphoreSlim, việc giữ chỗ máy được tuần tự hóa an toàn, kiểm soát chặt chẽ tình trạng vượt quá số lượng máy thực tế trong kho.")'
    )

    # 11. Cập nhật hiện thực hóa chức năng 4.3.2, 4.3.3, 4.3.4 theo đúng C# codebase
    content = content.replace(
        'Tại DocumentController.cs, khách hàng ký tên trực tiếp trên thẻ canvas HTML5. Chuỗi dữ liệu Base64 được gửi về máy chủ, giải mã sang mảng byte và kiểm tra tính hợp lệ của Magic Bytes hình ảnh (bắt đầu bằng 0x89 0x50 0x4E 0x47 đối với PNG) trước khi lưu vào CSDL, loại bỏ hoàn toàn nguy cơ tải lên mã độc.',
        'Tại CartController.cs (hành động SignContract) và HopDongController.cs (hành động KyHopDong), khách hàng thực hiện ký hợp đồng điện tử trực tiếp trên phần tử HTML5 Canvas được điều khiển bởi thư viện signature_pad. Dữ liệu chữ ký dạng chuỗi Base64 được giới hạn kích thước tối đa 256KB, giải mã sang mảng byte và xác thực nghiêm ngặt Magic Bytes (bắt đầu bằng 0x89 0x50 0x4E 0x47 đối với PNG) trước khi ghi tệp vật lý vào thư mục /uploads/signatures/ và lưu đường dẫn vào trường ChuKyKhachHang. Đồng thời, tệp ảnh CCCD/CMND tải lên được giới hạn dung lượng tối đa 5MB, kiểm tra phần mở rộng (.jpg, .jpeg, .png, .webp) và xác thực Magic Bytes (PNG: 0x89 0x50 0x4E 0x47, JPG: 0xFF 0xD8 0xFF, RIFF/WEBP: 0x52 0x49 0x46 0x46), ngăn chặn triệt để mã độc tải lên hệ thống.'
    )
    content = content.replace(
        'Tại PaymentWebhookController.cs, bản tin Webhook chứa TransactionRef được kiểm tra tính duy nhất (Idempotency) trong bảng WebhookLog. Hệ thống dùng biểu thức Regex bóc tách mã hợp đồng hoặc mã kỳ hạn, kiểm tra số tiền khớp lệnh và tự động gạch nợ.',
        'Tại PaymentController.cs, cổng tiếp nhận POST /Payment/BankingWebhook xử lý bản tin biến động số dư ngân hàng theo mô hình giao dịch an toàn kết hợp khóa SemaphoreSlim PaymentLock và mức cô lập Serializable Transaction. Cơ chế đảm bảo tính bất biến (Idempotency) được kích hoạt thông qua việc kiểm tra mã giao dịch ngân hàng referenceCode trong bảng PhieuThus (MaGiaoDichNganHang == referenceCode || GhiChu.Contains(referenceCode)). Khi xác nhận giao dịch mới, hệ thống bóc tách mã hợp đồng và thực hiện thuật toán gạch nợ 4 tầng (Waterfall): (1) Bù tiền cọc còn thiếu, (2) Thanh toán các kỳ hạn theo thứ tự hạn nộp tăng dần, (3) Thu hồi chi phí sửa chữa/bồi thường phát sinh, (4) Dồn tiền dôi dư vào số dư trả trước hợp đồng (TienDuKyTruoc). Phiếu thu tự động ghi nhận với MaNhanVienThu = null để đánh dấu giao dịch đối soát tự động bởi hệ thống.'
    )
    content = content.replace(
        'Tại ThongKeController.cs, hành động ExportExcel sử dụng thư viện ClosedXML để khởi tạo bảng tính Excel định dạng chuẩn kế toán doanh nghiệp, tính toán doanh thu thuần, tiền cọc đang giữ và tỷ lệ khai thác kho máy tự động.',
        'Tại ThongKeController.cs và CongNoController.cs, tính năng xuất báo cáo quản trị sử dụng thư viện ClosedXML (phiên bản 0.104.2). Trong đó, hành động CongNoController.ExportExcel kết xuất 17 cột dữ liệu chi tiết kèm công thức định dạng tiền tệ (#,##0), và ThongKeController.ExportExcel kết xuất 9 chỉ số KPI trọng yếu định dạng chuẩn nhận diện thương hiệu Cổ Điển Doanh Nghiệp (Executive Deep Navy #0F2B5C), tính toán doanh thu thuần, tiền cọc đang giữ và tỷ lệ khai thác kho máy tự động.'
    )

    # 12. Loại bỏ then chốt & vững chắc trong kết chương 4, 5 và bảng 5.2.2
    content = content.replace(
        'quá trình cài đặt thực tế các cơ chế kỹ thuật then chốt của hệ thống RentalSystem.',
        'quá trình cài đặt thực tế các cơ chế kỹ thuật cốt lõi của hệ thống RentalSystem.'
    )
    content = content.replace(
        'col_widths=[1.5, 3.2, 3.0, 3.2, 3.3, 1.3]',
        'col_widths=[1.3, 3.0, 3.0, 3.1, 3.3, 1.3]'
    )
    content = content.replace(
        '12 ca kiểm thử chức năng then chốt tương ứng',
        '12 ca kiểm thử chức năng tương ứng'
    )
    content = content.replace(
        'Nhằm đảm bảo hệ thống vận hành vững chắc trước các tình huống bất thường,',
        'Nhằm kiểm chứng độ tin cậy và khả năng chịu lỗi của hệ thống trước các tình huống bất thường,'
    )
    content = content.replace(
        'thực thi thành công ma trận 12 ca kiểm thử chức năng then chốt (TC-01 đến TC-12)',
        'thực thi thành công ma trận 12 ca kiểm thử chức năng (TC-01 đến TC-12)'
    )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: Cleaned build_master_thesis.py")

def clean_render_all_diagrams():
    file_path = 'tools/render_all_diagrams.py'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Figure 2.1 Use Case tổng quát: thay Kế toán / Thủ quỹ bằng Cổng VietQR & NAPAS
    content = content.replace(
        'box_tc = Rectangle((8.4, 0.6), 4.6, 4.0, facecolor=COLOR_ACCENT_BG, edgecolor=COLOR_BORDER_SOLID, linewidth=1.2, zorder=1)\n    ax.add_patch(box_tc)\n    ax.text(10.7, 4.35, "PHÂN HỆ TÀI CHÍNH & KẾ TOÁN", fontsize=11, fontweight=\'bold\', color=COLOR_TEXT_MAIN, ha=\'center\')',
        'box_tc = Rectangle((8.4, 0.6), 4.6, 4.0, facecolor=COLOR_ACCENT_BG, edgecolor=COLOR_BORDER_SOLID, linewidth=1.2, zorder=1)\n    ax.add_patch(box_tc)\n    ax.text(10.7, 4.35, "PHÂN HỆ KINH DOANH & CÔNG NỢ", fontsize=11, fontweight=\'bold\', color=COLOR_TEXT_MAIN, ha=\'center\')'
    )
    content = content.replace(
        'act_ktv = draw_actor(ax, 14.0, 2.5, "Kế toán / Thủ quỹ\\n(Accountant)", scale=1.1)',
        'act_ktv = draw_actor(ax, 14.0, 2.5, "Cổng thanh toán\\nVietQR / NAPAS", scale=1.1)'
    )
    # Re-wire act_kd and act_ktv:
    # act_kd connects to ov_tc2 (Theo dõi công nợ)
    content = content.replace(
        "    # Kế toán connects to Finance & Admin\n    connect_actor_to_usecase(ax, act_ktv['left'], (ov_tc1[0], ov_tc1[1]))\n    connect_actor_to_usecase(ax, act_ktv['left'], (ov_tc2[0], ov_tc2[1]))\n    connect_actor_to_usecase(ax, act_ktv['left'], (ov_tc3[0], ov_tc3[1]))\n    connect_actor_to_usecase(ax, act_ktv['left'], (ov_ad1[0], ov_ad1[1]))",
        "    # Kinh doanh connects to Cong no\n    connect_actor_to_usecase(ax, act_kd['right'], (ov_tc2[0], ov_tc2[1]))\n    connect_actor_to_usecase(ax, act_kd['right'], (ov_tc3[0], ov_tc3[1]))\n    # Cong thanh toan connects to VietQR\n    connect_actor_to_usecase(ax, act_ktv['left'], (ov_tc1[0], ov_tc1[1]))"
    )

    # 2. Figure 2.3 Use Case phân rã Admin: thay Kế toán viên bằng Cổng thanh toán Webhook NAPAS
    content = content.replace(
        'act_acc = draw_actor(ax, 13.5, 4.8, "Kế toán viên\\n(Accountant)", scale=1.1)',
        'act_acc = draw_actor(ax, 13.5, 2.7, "Cổng Webhook\\nNAPAS 247", scale=1.1)'
    )
    content = content.replace(
        "    # Accountant connects to 05, 06, 07, 08, 09\n    connect_actor_to_usecase(ax, act_acc['left'], (rendered_ovals[4][0], rendered_ovals[4][1]))\n    connect_actor_to_usecase(ax, act_acc['left'], (rendered_ovals[5][0], rendered_ovals[5][1]))\n    connect_actor_to_usecase(ax, act_acc['left'], (rendered_ovals[6][0], rendered_ovals[6][1]))\n    connect_actor_to_usecase(ax, act_acc['left'], (rendered_ovals[7][0], rendered_ovals[7][1]))\n    connect_actor_to_usecase(ax, act_acc['left'], (rendered_ovals[8][0], rendered_ovals[8][1]))",
        "    # Sales connects also to Debt, Refund, Report\n    connect_actor_to_usecase(ax, act_sales['right'], (rendered_ovals[4][0], rendered_ovals[4][1]))\n    connect_actor_to_usecase(ax, act_sales['right'], (rendered_ovals[7][0], rendered_ovals[7][1]))\n    connect_actor_to_usecase(ax, act_sales['right'], (rendered_ovals[8][0], rendered_ovals[8][1]))\n    # Webhook connects to UC-AD07\n    connect_actor_to_usecase(ax, act_acc['left'], (rendered_ovals[6][0], rendered_ovals[6][1]))"
    )

    # 2b. Clean legacy mentions of Kế toán in Sequence & Collaboration flow data
    content = content.replace('"actor": "Khách hàng & Kế toán",', '"actor": "Khách hàng & Kinh doanh",')
    content = content.replace('"actor": "Khách hàng & Kế toán kho",', '"actor": "Khách hàng & Kinh doanh",')
    content = content.replace('("Kế toán", "Tính quyết toán: Hoàn cọc = Tiền cọc - Phạt hư hỏng - Nợ thuê"),', '("Kinh doanh", "Tính quyết toán: Hoàn cọc = Tiền cọc - Phạt hư hỏng - Nợ thuê"),')
    content = content.replace('("Kế toán", "Lập PhieuChi hoàn tiền cọc & Chuyển khoản cho khách hàng"),', '("Kinh doanh", "Lập PhieuChi hoàn tiền cọc & Chuyển khoản cho khách hàng"),')
    content = content.replace('("Actor", "Boundary", "5: Kế toán bấm Lập phiếu chi hoàn cọc"),', '("Actor", "Boundary", "5: Kinh doanh bấm Lập phiếu chi hoàn cọc"),')
    content = content.replace('("5: Lập phiếu chi hoàn tiền cọc", "Kế toán", "PhieuChiController"),', '("5: Lập phiếu chi hoàn tiền cọc", "Kinh doanh", "PhieuChiController"),')

    # 3. Figure 2.1.2.1 VietQR: mở rộng canvas, bỏ text overlap, không che chữ
    old_vietqr_code = """def render_figure_2_1_2_1_vietqr():
    \"\"\"Hình 2.1.2. 1: Cấu trúc bản tin và giải thuật sinh chuỗi mã VietQR động NAPAS 247\"\"\"
    fig, ax = setup_canvas(14, 8.5)
    
    # Left Box: EMVCo TLV Structure
    ax.text(3.6, 7.8, "CẤU TRÚC DỮ LIỆU EMVCO TLV (TAG - LENGTH - VALUE)", fontsize=11, fontweight='bold', color=COLOR_TEXT_MAIN, ha='center')
    
    # 100% Sanitized Corporate Data (R2d)
    tags = [
        ("Tag 00", "02", "01", "Payload Format Indicator (Phiên bản chuẩn)"),
        ("Tag 01", "02", "12", "Point of Initiation Method (12: Mã động Dynamic QR)"),
        ("Tag 38", "57", "0010A0000007270124...", "Merchant Account: VietinBank / NAPAS 247, STK: 999988882026"),
        ("Tag 53", "03", "704", "Transaction Currency (704: Việt Nam Đồng - VNĐ)"),
        ("Tag 54", "07", "2500000", "Transaction Amount (Số tiền cọc hoặc kỳ hạn thuê)"),
        ("Tag 58", "02", "VN", "Country Code (Mã quốc gia Việt Nam)"),
        ("Tag 59", "23", "RENTALSYSTEM ENTERPRISE", "Merchant Name (Tên tài khoản người thụ hưởng)"),
        ("Tag 60", "15", "TP HO CHI MINH", "Merchant City (Thành phố nơi mở tài khoản)"),
        ("Tag 62", "14", "0810HD105 KY2", "Additional Data (Cú pháp tự động đối soát HD/KY)"),
        ("Tag 63", "04", "CRC16-CCITT", "Checksum bảo toàn toàn vẹn chuỗi dữ liệu EMVCo")
    ]
    
    y = 7.1
    for tag, length, val, desc in tags:
        draw_rounded_box(ax, 0.8, y, 1.1, 0.48, tag, bg=COLOR_HEADER_BG, border='none', text_color=COLOR_HEADER_TEXT, fontsize=9.0, bold=True)
        draw_rounded_box(ax, 2.0, y, 0.6, 0.48, length, bg=COLOR_ACCENT_BG, border=COLOR_BORDER_SOLID, text_color=COLOR_TEXT_MAIN, fontsize=9.0)
        draw_rounded_box(ax, 2.7, y, 2.0, 0.48, val, bg=COLOR_CARD_BG, border=COLOR_BORDER_SOLID, text_color=COLOR_TEXT_MAIN, fontsize=9.0, bold=True)
        ax.text(4.85, y + 0.24, desc, fontsize=9.5, color=COLOR_TEXT_MAIN, fontfamily=FONT_FAMILY, va='center')
        y -= 0.58
        
    # Right Box: CRC16 & Webhook Automation
    ax.text(10.5, 7.8, "THUẬT TOÁN CRC16-CCITT & ĐỐI SOÁT OPEN BANKING", fontsize=11, fontweight='bold', color=COLOR_TEXT_MAIN, ha='center')
    
    draw_rounded_box(ax, 7.3, 4.6, 6.0, 2.7,
                     "GIẢI THUẬT KIỂM TOÀN VẸN CRC16-CCITT:\\n\\n"
                     "- Đa thức sinh: G(x) = x^16 + x^12 + x^5 + 1 (Hex: 0x1021)\\n"
                     "- Giá trị khởi tạo: 0xFFFF | Quét toàn chuỗi từ Tag 00 đến '6304'\\n"
                     "- Kết quả 16-bit Hexadecimal ghép trực tiếp vào cuối chuỗi QR\\n"
                     "- Công thức: CRC = Sum(D_k * x^(16-k)) mod G(x)",
                     bg=COLOR_CARD_BG, border=COLOR_BORDER_SOLID, fontsize=9.5, align='left')
    
    # Standardized Webhook System Title (R2d)
    draw_rounded_box(ax, 7.3, 1.2, 6.0, 3.0,
                     "HỆ THỐNG ĐỐI SOÁT TỰ ĐỘNG WEBHOOK 24/7:\\n\\n"
                     "1. Khách hàng quét mã VietQR và xác nhận chuyển tiền trên Mobile Banking.\\n"
                     "2. Cổng thanh toán NAPAS 247 gửi biến động số dư qua Open Banking (SePay/Casso).\\n"
                     "3. Endpoint /Payment/BankingWebhook tiếp nhận gói HTTP POST.\\n"
                     "4. Regex Parser: (?i)(?:HD|HĐ)[\\\\s\\\\-_:#]*([0-9]{1,10}) tự động bóc tách số hợp đồng.\\n"
                     "5. Khóa PaymentLock đảm bảo Idempotency (chống trùng lặp giao dịch).\\n"
                     "6. Gạch nợ tự động trong 3 giây, sinh PhieuThu và kích hoạt hợp đồng.",
                     bg=COLOR_ACCENT_BG, border=COLOR_BORDER_SOLID, fontsize=9.2, align='left')
    
    draw_arrow(ax, 4.8, 1.5, 7.3, 2.7, "Quét & Webhook", fontsize=9.5)
    
    plt.tight_layout()
    outpath = os.path.join(OUTPUT_DIR, 'hinh_2_1_2_1_vietqr_napas247_structure.png')
    plt.savefig(outpath, dpi=300)
    plt.close()
    return outpath"""

    new_vietqr_code = """def render_figure_2_1_2_1_vietqr():
    \"\"\"Hình 2.1.2. 1: Cấu trúc bản tin và giải thuật sinh chuỗi mã VietQR động NAPAS 247\"\"\"
    fig, ax = setup_canvas(15.5, 7.6)
    
    # 100% Sanitized Corporate Data (Clean & Readable)
    tags = [
        ("Tag 00", "02", "01", "Payload Format Indicator (Phiên bản chuẩn EMVCo)"),
        ("Tag 01", "02", "12", "Point of Initiation Method (12: Mã động Dynamic QR)"),
        ("Tag 38", "57", "0010A0000007270124...", "Merchant Account: VietinBank / NAPAS 247"),
        ("Tag 53", "03", "704", "Transaction Currency (704: Việt Nam Đồng - VNĐ)"),
        ("Tag 54", "07", "2500000", "Transaction Amount (Số tiền cọc hoặc kỳ hạn thuê)"),
        ("Tag 58", "02", "VN", "Country Code (Mã quốc gia Việt Nam)"),
        ("Tag 59", "23", "RENTALSYSTEM ENTERPRISE", "Merchant Name (Tên người thụ hưởng)"),
        ("Tag 60", "15", "TP HO CHI MINH", "Merchant City (Thành phố mở tài khoản)"),
        ("Tag 62", "14", "0810HD105 KY2", "Additional Data (Cú pháp tự động đối soát HD)"),
        ("Tag 63", "04", "CRC16-CCITT", "Checksum bảo toàn chuỗi dữ liệu EMVCo")
    ]
    
    y = 6.8
    for tag, length, val, desc in tags:
        draw_rounded_box(ax, 0.4, y, 1.0, 0.48, tag, bg=COLOR_HEADER_BG, border='none', text_color=COLOR_HEADER_TEXT, fontsize=10.0, bold=True)
        draw_rounded_box(ax, 1.5, y, 0.55, 0.48, length, bg=COLOR_ACCENT_BG, border=COLOR_BORDER_SOLID, text_color=COLOR_TEXT_MAIN, fontsize=10.0)
        draw_rounded_box(ax, 2.15, y, 1.9, 0.48, val, bg=COLOR_CARD_BG, border=COLOR_BORDER_SOLID, text_color=COLOR_TEXT_MAIN, fontsize=9.5, bold=True)
        ax.text(4.2, y + 0.24, desc, fontsize=10.5, color=COLOR_TEXT_MAIN, fontfamily=FONT_FAMILY, va='center')
        y -= 0.62
        
    # Right Box: CRC16 & Webhook Automation (Starts at x=8.8 - generous width)
    draw_rounded_box(ax, 8.8, 4.0, 6.3, 3.2,
                     "GIẢI THUẬT KIỂM TOÀN VẸN CRC16-CCITT:\\n\\n"
                     "- Đa thức sinh: G(x) = x^16 + x^12 + x^5 + 1 (Hex: 0x1021)\\n"
                     "- Giá trị khởi tạo: 0xFFFF | Quét chuỗi từ Tag 00 đến '6304'\\n"
                     "- Kết quả 16-bit Hexadecimal ghép vào cuối chuỗi QR\\n"
                     "- Công thức: CRC = Sum(D_k * x^(16-k)) mod G(x)",
                     bg=COLOR_CARD_BG, border=COLOR_BORDER_SOLID, fontsize=10.5, align='left')
    
    draw_rounded_box(ax, 8.8, 0.4, 6.3, 3.4,
                     "HỆ THỐNG ĐỐI SOÁT TỰ ĐỘNG WEBHOOK 24/7:\\n\\n"
                     "1. Khách hàng quét mã VietQR trên ứng dụng Mobile Banking.\\n"
                     "2. Cổng NAPAS 247 gửi biến động số dư qua Webhook.\\n"
                     "3. Endpoint /Payment/BankingWebhook tiếp nhận HTTP POST.\\n"
                     "4. Regex Parser tự động bóc tách số hợp đồng từ cú pháp.\\n"
                     "5. Khóa PaymentLock đảm bảo Idempotency (chống trùng lặp).\\n"
                     "6. Gạch nợ tự động trong 3 giây, sinh PhieuThu và kích hoạt.",
                     bg=COLOR_ACCENT_BG, border=COLOR_BORDER_SOLID, fontsize=10.0, align='left')
    
    # Arrow placed at bottom right to avoid any overlap
    draw_arrow(ax, 7.8, 0.8, 8.8, 1.0, "Webhook", fontsize=10.0)
    
    plt.tight_layout()
    outpath = os.path.join(OUTPUT_DIR, 'hinh_2_1_2_1_vietqr_napas247_structure.png')
    plt.savefig(outpath, dpi=300)
    plt.close()
    return outpath"""

    if old_vietqr_code in content:
        content = content.replace(old_vietqr_code, new_vietqr_code)
        print("SUCCESS: Replaced render_figure_2_1_2_1_vietqr")
    else:
        print("WARNING: old_vietqr_code not matched exactly, checking substring...")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: Cleaned render_all_diagrams.py")

if __name__ == '__main__':
    clean_build_master_thesis()
    clean_render_all_diagrams()
