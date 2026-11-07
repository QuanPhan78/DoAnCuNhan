# Quyết toán hợp đồng và kiểm thử điện thoại

Luồng hoàn cọc dùng chung `ContractSettlementService` cho quyết toán sau trả máy, trả trước hạn và hủy đơn chờ giao. Cọc thực thu lấy từ phiếu thu loại 1 chưa hủy; cọc yêu cầu không phải số dư có thể hoàn. Phiếu chi loại 0 chỉ chứa phần hoàn cọc; hoàn thuê và tiền chuyển thừa được tách riêng.

SQL 004 bổ sung `ContractSettlements`, khóa chính là mã hợp đồng. Khóa giao dịch SQL và bản ghi duy nhất chặn chi lặp giữa các tiến trình. Bản xem trước có dấu vân tay của dữ liệu tài chính; nhân viên phải xác nhận lại khi dữ liệu đổi. Hợp đồng lịch sử đã kết thúc được giữ nguyên, không tự tạo bản ghi quyết toán hồi tố. Cọc lưu không khớp chứng từ phải được đối chiếu trước khi chi.

Trước nâng cấp: sao lưu SQL bằng `COPY_ONLY, CHECKSUM`, chạy `RESTORE VERIFYONLY ... WITH CHECKSUM`, áp dụng `004_ContractSettlements.sql`, kiểm tra dữ liệu cũ rồi khởi động bản Web cùng phiên bản. Tạo mới dùng `MobileApp/RentalSystemDB.sql`, bao gồm 001–004. JSON backup/restore chứa sổ quyết toán; SQL backup giữ toàn bộ lược đồ và dữ liệu.

Kiểm thử HTTP dùng các công cụ `tools/database/verify_*.py`; fixture tạo cơ sở dữ liệu có tên ngẫu nhiên `RentalSystemDebtCheck_*`, chạy server riêng và xóa đúng cơ sở dữ liệu đó khi kết thúc. Không chạy lệnh Prepare/Reset trên `RentalSystemDB_V2` đang sử dụng.

Mobile giới hạn yêu cầu thông thường 30 giây và multipart 60 giây. Lỗi mạng không xóa phiên và không tự gửi lại lệnh tạo. Khi kết quả chưa rõ, khách hàng kiểm tra danh sách sau khi kết nối lại trước khi gửi tiếp. KT-30 được chạy bằng proxy API thử để tạo lỗi trước khi gửi, treo phản hồi và mất phản hồi sau khi đã lưu.

## Giữ ứng dụng trên điện thoại

Không dùng `flutter test ... -d <serial>` cho bài integration nếu cần giữ ứng dụng: Flutter SDK tự gỡ bản test khi dọn tiến trình. Dùng:

```powershell
flutter drive --driver=test_driver/integration_test.dart --target=integration_test/physical_connection_test.dart --keep-app-running --no-pub -d <serial> --android-project-arg=rentalTestApplicationId=com.example.quan_ly_cho_thue_thiet_bi.testing --dart-define=API_BASE_URL=http://127.0.0.1:5108/api
```

`rentalTestApplicationId` là tham số Gradle tùy chọn. Không truyền tham số thì ID bản chính giữ nguyên; truyền `.testing` tạo bản cài và dữ liệu riêng, tên hiển thị “RentalSystem kiểm thử”. API 5108/điều khiển 5109 chỉ thuộc fixture thử. Dùng `adb install -r` để cập nhật, không dùng uninstall hoặc clear data. Sau kiểm thử, cài cập nhật bản `lib/main.dart` chạy bình thường, giữ ứng dụng trên máy và mở lại bản chính.

APK cục bộ dùng `API_BASE_URL=http://127.0.0.1:5000/api` kết nối qua `adb reverse tcp:5000 tcp:5000`. Backend tương ứng cần chạy trên máy tính tại cổng 5000.
