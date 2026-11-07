# -*- coding: utf-8 -*-
"""
Script to apply remaining 7 tone-down replacements in tools/build_master_thesis.py.
"""
import sys, os

sys.stdout.reconfigure(encoding='utf-8')

script_path = os.path.join(os.path.dirname(__file__), 'build_master_thesis.py')
with open(script_path, 'r', encoding='utf-8') as f:
    code = f.read()

has_crlf = '\r\n' in code
code = code.replace('\r\n', '\n')

replacements = [
    # 1. Line 1432
    (
        'add_p(doc, "Nhằm tạo nền tảng backend vững chắc và sẵn sàng tích hợp với các ứng dụng máy khách di động trong tương lai, hệ thống thiết lập bộ dịch vụ RESTful API tuân thủ khuyến nghị OpenAPI 3.0 (Swagger UI):")',
        'add_p(doc, "Để hỗ trợ trao đổi dữ liệu với các ứng dụng máy khách và mở rộng tích hợp trong tương lai, hệ thống thiết lập các dịch vụ RESTful API tuân thủ đặc tả OpenAPI 3.0 (Swagger UI):")'
    ),
    # 2. Line 1895
    (
        'add_p(doc, "Tại CartController.cs (hành động SignContract) và HopDongController.cs (hành động KyHopDong), khách hàng thực hiện ký hợp đồng điện tử trực tiếp trên phần tử HTML5 Canvas được điều khiển bởi thư viện signature_pad. Dữ liệu chữ ký dạng chuỗi Base64 được giới hạn kích thước tối đa 256KB, giải mã sang mảng byte và xác thực nghiêm ngặt Magic Bytes (bắt đầu bằng 0x89 0x50 0x4E 0x47 đối với PNG) trước khi ghi tệp vật lý vào thư mục /uploads/signatures/ và lưu đường dẫn vào trường ChuKyKhachHang. Đồng thời, tệp ảnh CCCD/CMND tải lên được giới hạn dung lượng tối đa 5MB, kiểm tra phần mở rộng (.jpg, .jpeg, .png, .webp) và xác thực Magic Bytes (PNG: 0x89 0x50 0x4E 0x47, JPG: 0xFF 0xD8 0xFF, RIFF/WEBP: 0x52 0x49 0x46 0x46), ngăn chặn hiệu quả mã độc tải lên hệ thống.")',
        'add_p(doc, "Tại CartController.cs (hành động SignContract) và HopDongController.cs (hành động KyHopDong), khách hàng thực hiện ký hợp đồng điện tử trực tiếp trên phần tử HTML5 Canvas được điều khiển bởi thư viện signature_pad. Dữ liệu chữ ký dạng chuỗi Base64 được giới hạn kích thước tối đa 256KB, giải mã sang mảng byte và kiểm tra định dạng Magic Bytes (bắt đầu bằng 0x89 0x50 0x4E 0x47 đối với PNG) trước khi ghi tệp vật lý vào thư mục /uploads/signatures/ và lưu đường dẫn vào trường ChuKyKhachHang. Đồng thời, tệp ảnh CCCD/CMND tải lên được giới hạn dung lượng tối đa 5MB, kiểm tra phần mở rộng (.jpg, .jpeg, .png, .webp) và kiểm tra Magic Bytes (PNG: 0x89 0x50 0x4E 0x47, JPG: 0xFF 0xD8 0xFF, RIFF/WEBP: 0x52 0x49 0x46 0x46), nhằm hạn chế nguy cơ tải tệp không hợp lệ lên máy chủ.")'
    ),
    # 3. Line 1901
    (
        'add_p(doc, "Tại ThongKeController.cs và CongNoController.cs, tính năng xuất báo cáo quản trị sử dụng thư viện ClosedXML (phiên bản 0.104.2). Trong đó, hành động CongNoController.ExportExcel kết xuất 17 cột dữ liệu chi tiết kèm công thức định dạng tiền tệ (#,##0), và ThongKeController.ExportExcel kết xuất 9 chỉ số KPI trọng yếu định dạng chuẩn nhận diện thương hiệu Cổ Điển Doanh Nghiệp (Executive Deep Navy #0F2B5C), tính toán doanh thu thuần, tiền cọc đang giữ và tỷ lệ khai thác kho máy tự động.")',
        'add_p(doc, "Tại ThongKeController.cs và CongNoController.cs, tính năng xuất báo cáo quản trị sử dụng thư viện ClosedXML (phiên bản 0.104.2). Trong đó, hành động CongNoController.ExportExcel kết xuất 17 cột dữ liệu chi tiết kèm công thức định dạng tiền tệ (#,##0), và ThongKeController.ExportExcel kết xuất 9 chỉ số KPI trọng yếu sử dụng tông màu xanh đen (#0F2B5C) làm màu tiêu đề bảng, tính toán doanh thu thuần, tiền cọc đang giữ và tỷ lệ khai thác kho máy tự động.")'
    ),
    # 4. Line 1904
    (
        'add_p(doc, "Để phục vụ trao đổi dữ liệu hai chiều với các ứng dụng máy khách và mở rộng hệ sinh thái di động, hệ thống cấu hình bộ điều khiển API Controller kế thừa ControllerBase kết hợp tài liệu hóa OpenAPI / Swagger. Cơ chế xác thực an toàn được thực hiện thông qua JSON Web Token (JWT) được cấp phát khi đăng nhập hợp lệ. Các Endpoint API trả về cấu trúc dữ liệu JSON chuẩn mực gồm mã trạng thái (statusCode), thông điệp (message) và tải dữ liệu (data), hỗ trợ xử lý bất đồng bộ (async/await) trên toàn bộ các tác vụ truy vấn Entity Framework Core.")',
        'add_p(doc, "Để phục vụ trao đổi dữ liệu với các ứng dụng máy khách và mở rộng tích hợp di động, hệ thống cấu hình các bộ điều khiển API Controller kế thừa ControllerBase kết hợp tài liệu hóa OpenAPI / Swagger. Cơ chế xác thực được thực hiện thông qua JSON Web Token (JWT) khi đăng nhập hợp lệ. Các Endpoint API trả về cấu trúc dữ liệu JSON gồm mã trạng thái (statusCode), thông điệp (message) và dữ liệu trả về (data), áp dụng xử lý bất đồng bộ (async/await) trên các tác vụ truy vấn Entity Framework Core.")'
    ),
    # 5. Line 1907
    (
        'add_p(doc, "Tại DatabaseController.cs (khu vực Admin, phân quyền nghiêm ngặt Authorize(Roles = \'Admin\')), hệ thống cài đặt giải pháp sao lưu và khôi phục toàn vẹn 18 bảng cơ sở dữ liệu quan hệ, đáp ứng chuẩn an toàn dữ liệu và phục hồi sự cố doanh nghiệp:")',
        'add_p(doc, "Tại DatabaseController.cs (khu vực Admin, áp dụng thuộc tính phân quyền Authorize(Roles = \'Admin\')), hệ thống cài đặt chức năng sao lưu và khôi phục dữ liệu cho 18 bảng của hệ thống:")'
    ),
    # 6. Line 1912
    (
        'add_p(doc, "Chương 4 đã trình bày chi tiết môi trường phát triển .NET 9, kiến trúc phân tầng ASP.NET Core MVC và quá trình cài đặt thực tế các cơ chế kỹ thuật cốt lõi của hệ thống RentalSystem. Việc kết hợp hài hòa giữa các công nghệ hiện đại (.NET 9, EF Core 9, SQL Server 2022, ClosedXML) và các chuẩn thiết kế nghiêm ngặt đã tạo nên một sản phẩm phần mềm hoàn thiện, vận hành ổn định và sẵn sàng cho công tác kiểm thử tại Chương 5.")',
        'add_p(doc, "Chương 4 đã trình bày môi trường phát triển .NET 9, kiến trúc phân tầng ASP.NET Core MVC và quá trình cài đặt các chức năng chính của hệ thống RentalSystem trên nền tảng .NET 9, EF Core 9, SQL Server 2022 và thư viện ClosedXML, làm cơ sở thực hiện đánh giá kiểm thử tại Chương 5.")'
    ),
    # 7. Line 1971
    (
        'add_p(doc, "Dựa trên kết quả triển khai thực tế và các kịch bản kiểm thử đã thực hiện, hệ thống phần mềm RentalSystem được đánh giá trên các tiêu chí: khả năng đáp ứng yêu cầu nghiệp vụ, độ ổn định và an toàn dữ liệu, cùng trải nghiệm người dùng trên giao diện Web Responsive Design (Executive Deep Navy).")',
        'add_p(doc, "Dựa trên kết quả triển khai thực tế và các kịch bản kiểm thử đã thực hiện, hệ thống phần mềm RentalSystem được đánh giá trên các tiêu chí: khả năng đáp ứng yêu cầu nghiệp vụ, độ ổn định, tính an toàn dữ liệu và khả năng tương thích của giao diện web trên các thiết bị.")'
    )
]

success = 0
for old, new in replacements:
    if old in code:
        code = code.replace(old, new, 1)
        success += 1
    else:
        print(f"[WARN] Target not found:\n  {old[:80]}...")

if has_crlf:
    code = code.replace('\n', '\r\n')

with open(script_path, 'w', encoding='utf-8') as f:
    f.write(code)

print(f"\nCompleted: {success}/{len(replacements)} additional passages rewritten cleanly!")
