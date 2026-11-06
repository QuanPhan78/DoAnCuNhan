# Trạng thái bộ demo

Ngày kiểm chứng: **04/11/2026** (Asia/Bangkok).

## Đã thực hiện

- CSDL `RentalSystemDemoDB` riêng, 7 hợp đồng, 24 thiết bị, 13 kỳ thanh toán; đủ bốn vai trò. Ngày dữ liệu được làm mới khi reset.
- Hợp đồng chính HD-0001 đủ hồ sơ và chữ ký giả lập; phiếu SC-0001 sửa xong chưa đánh giá làm dự phòng.
- Bản sao lưu baseline và gói snapshot chứa JSON, ảnh/chữ ký và manifest.
- **35/35 kiểm tra HTTP tích hợp đạt** trên `RentalSystemDemoCheckDB`: đăng nhập, danh sách theo khách, thuê và đối chiếu Web, phân công, sửa chữa, đánh giá, phân quyền trang Web, Excel, biểu mẫu, sao lưu/khôi phục, dữ liệu giữ nguyên sau khởi động lại. Kết quả máy đọc được: `outputs/demo-check/verification.json`.
- Kiểm thử Flutter cấu hình mặc định: **10/10 đạt**. Kiểm thử riêng với `API_BASE_URL=http://127.0.0.1:5000/api`: **1/1 đạt**.
- `flutter analyze --no-pub`: không có vấn đề.
- APK Android debug đã build thành công với địa chỉ API qua USB, đặt tại `outputs/demo/android/RentalSystem-demo-debug.apk`. Đã kiểm tra manifest APK có quyền Internet, cho phép HTTP trong bản debug; metadata và SHA256 trong `outputs/demo/android/build.json`. Chạy `demo.ps1 -Action Install` để cài khi điện thoại kết nối.
- Build .NET thành công; mã ứng dụng hiện có vẫn phát cảnh báo nullable khi biên dịch đầy đủ. Không dùng kết quả kiểm tra tài liệu khóa luận để suy ra tình trạng chạy ứng dụng.
- scrcpy portable 5.0.1 tải từ bản phát hành chính thức, đối chiếu SHA256; lệnh kiểm tra phiên bản thành công. Metadata tại `outputs/demo/tools/scrcpy/installation.json`.
- Kịch bản tiếng Việt, bảng nhắc HTML và PDF **1 trang A4 ngang**, đã render và kiểm tra trực quan. PDF: `output/pdf/BANG_NHAC_DEMO.pdf`.
- Excel, hợp đồng, biên bản bàn giao và phiếu thu đã xuất thực tế từ CSDL kiểm chứng, tại `outputs/demo-check/evidence/`.

## Cần thực hiện trên thiết bị thật

- ☐ Cắm điện thoại Android qua USB, mở khóa và chấp nhận USB debugging. Lần kiểm tra gần nhất chưa có thiết bị kết nối.
- ☐ Chạy `demo.ps1 -Action Install` (hoặc `Mobile`) và `demo.ps1 -Action Mirror`; kiểm tra đăng nhập và tải dữ liệu từ điện thoại.
- ☐ Thao tác trọn luồng Mobile → Web → Mobile bằng giao diện thật; kiểm tra trình chiếu đọc rõ mã và số tiền.
- ☐ Quay và mở thử ba video dự phòng. Công cụ quay đã có; chưa có video điện thoại thật.
- ☐ Tập hai lượt liên tiếp, mỗi lượt ≤12 phút; điền thời gian thực tế trong README.

Kết quả HTTP không thay thế những bước trên. Chỉ đánh dấu sẵn sàng bảo vệ khi đã hoàn tất kiểm tra điện thoại, video và hai lượt tập.
