# Bộ demo RentalSystem — Web và Android thật

Mở [kịch bản nói](KICH_BAN.md) để tập và [bảng nhắc một trang](BANG_NHAC.html) để in A4 ngang. Thời lượng mục tiêu 11 phút 30 giây, dự phòng 30 giây. Một người điều khiển Web và điện thoại chiếu lên laptop qua USB.

Bản PDF in sẵn: `output/pdf/BANG_NHAC_DEMO.pdf` (1 trang A4 ngang, đã render kiểm tra). Bảng HTML là nguồn để chỉnh lời nhắc; công cụ xuất lại tùy chọn: `node tools/demo/render_reminder.mjs` khi có Playwright.

## Chạy nhanh

Phần này áp dụng khi `RentalSystemDB_V2` còn được đánh dấu diễn tập. Web diễn tập chạy trên cổng 5001. Xem [quy trình cơ sở dữ liệu](../database-cutover.md) để chạy ứng dụng đã đưa vào sử dụng.

Chạy PowerShell tại `D:\DoAnCuNhan`. Mỗi dòng dưới đây là một lệnh riêng. Cần .NET 9, SQL Server `localhost` cho phép Windows Authentication, Flutter và Android SDK platform-tools. Không cần chuyển khoản thật.

```powershell
# Tạo CSDL giả lập hoặc cập nhật ảnh mẫu của demo hiện có
.\tools\demo\demo.ps1 -Action Prepare

# Lần đầu nếu chưa có scrcpy: tải bản portable chính thức và kiểm tra SHA256
.\tools\demo\setup-scrcpy.ps1

# Terminal 1: chạy Web, để terminal này mở; Ctrl+C để dừng
.\tools\demo\demo.ps1 -Action Web

# Terminal 2: mở ba hồ sơ trình duyệt riêng để đăng nhập các vai trò
.\tools\demo\demo.ps1 -Action Sessions

# Terminal 3: cắm và mở khóa điện thoại, chấp nhận USB debugging, cài/mở APK đã chuẩn bị
.\tools\demo\demo.ps1 -Action Install

# Terminal 4: chiếu điện thoại
.\tools\demo\demo.ps1 -Action Mirror
```

`Mobile` chuyển tiếp cổng 5000 trên điện thoại tới cổng 5001 trên máy tính, rồi chạy Flutter debug với `API_BASE_URL=http://127.0.0.1:5000/api`. Cấu hình HTTP chỉ mở cho bản Android debug. Địa chỉ runtime qua `ApiConfig.setBaseUrl` có ưu tiên cao hơn cấu hình biên dịch.

`Install` dùng APK đã đóng gói tại `outputs/demo/android/RentalSystem-demo-debug.apk`; chạy offline khi đã có ADB. Nếu cần chạy mã nguồn để debug, dùng `demo.ps1 -Action Mobile`. Khi đổi cấu hình API hoặc sửa mã, build lại bằng `flutter build apk --debug --no-pub --dart-define=API_BASE_URL=http://127.0.0.1:5000/api` tại `MobileApp`, rồi chép `build/app/outputs/flutter-apk/app-debug.apk` đến đường dẫn APK demo trên.

Bộ build Android đã được căn theo mẫu của Flutter 3.38.7 đang cài: Gradle 8.14, Android Gradle Plugin 8.11.1, Kotlin Gradle Plugin 2.2.20, Java 17. Cấu hình AGP 9 trước đó không phù hợp SDK này; [tài liệu Flutter](https://docs.flutter.dev/release/breaking-changes/migrate-to-built-in-kotlin/for-app-developers) nêu hỗ trợ AGP 9 với Kotlin tích hợp tắt bắt đầu từ Flutter 3.44. Không cần nâng Flutter để sử dụng bộ demo.

Kotlin incremental được tắt cho dự án để tránh lỗi đường dẫn khác ổ đĩa giữa Pub cache trên C: và mã nguồn trên D:. Cấu hình này chỉ ảnh hưởng cách build, không đổi chức năng ứng dụng.

Nếu có nhiều điện thoại: thêm `-Serial MA_THIET_BI` vào `Install`, `Mobile`, `Mirror`, `Record`. Nếu scrcpy chưa có trong PATH, giải nén bản Windows chính thức rồi truyền `-ScrcpyPath 'D:\duong-dan\scrcpy.exe'`. Chạy `scrcpy --version` để kiểm tra. Nguồn: [scrcpy chính thức](https://github.com/Genymobile/scrcpy), [hướng dẫn Windows](https://github.com/Genymobile/scrcpy/blob/master/doc/windows.md), [quay video](https://github.com/Genymobile/scrcpy/blob/master/doc/recording.md). Cấu hình Flutter dùng [compilation environment declarations](https://dart.dev/libraries/core/environment-declarations).

## Tài khoản và mã chuẩn

Tất cả tài khoản dưới đây chỉ có trong CSDL demo, mật khẩu **`Demo@123`**.

| Vai trò | Tài khoản | Nơi dùng |
|---|---|---|
| Khách hàng | `customer@demo.invalid` | Điện thoại; tên “Khách hàng Demo An”, mã người dùng 4 |
| Kinh doanh | `sale@demo.invalid` | Hồ sơ trình duyệt `browser-sale` |
| Kỹ thuật | `tech@demo.invalid` | Hồ sơ trình duyệt `browser-tech`; mã kỹ thuật viên 3 |
| Quản trị | `admin@demo.invalid` | Hồ sơ trình duyệt `browser-admin` |

| Dữ liệu | Mã/giá trị |
|---|---|
| Sản phẩm đặt mới | `SP-0001` — Laptop Demo Dell Latitude 5430 |
| Đơn giá | 170.000đ/ngày; cọc tham khảo của sản phẩm 8.000.000đ |
| Ngày chọn trên Mobile | Chọn ngày bắt đầu D và kết thúc D+6: 7 ngày lịch theo cách tính hiện tại của Mobile |
| Tiền dự kiến | 1.190.000đ; phần “đã thu cọc” của yêu cầu mới là **0đ** |
| Địa chỉ | Phòng demo, 123 Đường Minh Họa, TP.HCM |
| Hợp đồng báo lỗi chính | `HD-0001` — serial `DEMO-LAP-001` |
| Biên bản của hợp đồng chính | Mã 1 |
| Hợp đồng dự phòng đã thuê | `HD-0002` — serial `DEMO-LAP-002` |
| Phiếu dự phòng sửa xong, chưa đánh giá | `SC-0001`, thuộc `HD-0002` |
| Đơn chờ duyệt dự phòng | `HD-0003`; chưa thu cọc |
| Công nợ quá hạn minh họa | `HD-0004` |

Ngày kết thúc D+6 là lựa chọn có chủ ý: Mobile hiện tính cả ngày đầu và ngày cuối, đồng thời gửi tiền dự kiến sang API. Không chọn D+7 rồi đọc là 7 ngày. Bộ demo giữ nguyên quy tắc hiện tại. Giá cọc tham khảo không đồng nghĩa đã thu cọc; chưa demo bước thu tiền thì đọc là 0đ. Sau khi đặt, ghi **mã đơn thật trả về**, không giả định luôn là HD-0008. Tương tự, ghi mã sự cố mới ngay khi Web hiển thị.

## Các cửa sổ cần mở trước

- Kinh doanh: `http://localhost:5001/Admin/HopDong` và `/Admin/HopDong/Details/1`.
- Kỹ thuật: `http://localhost:5001/Admin/BaoTri`; sẵn sàng mở đúng phiếu mới được phân công.
- Quản trị: `/Admin/BaoTri`, `/Admin/ThongKe`, `/Admin/Database`.
- Điện thoại: đăng nhập khách hàng; mở danh mục thiết bị. Trước khi báo sự cố, vào “Hợp đồng” và tải danh sách để ứng dụng có dữ liệu hợp đồng cho ô chọn.
- Kỳ báo cáo: từ **ngày chuẩn bị trừ 60 ngày đến ngày chuẩn bị**, xem chính xác trong `outputs/demo-check/manifest.json`. Chọn khoảng tùy chỉnh, vì một số khoản thu nằm ở tháng trước.

Đổi tên hoặc đặt màu từng hồ sơ trình duyệt theo vai trò trong lần tập đầu. Ba cửa sổ ẩn danh cùng một trình duyệt có thể dùng chung cookie; dùng ba hồ sơ do lệnh `Sessions` tạo.

## Sao lưu, đặt lại và diễn tập

```powershell
# Kiểm tra dữ liệu: có thể chạy trước khi mở Web
.\tools\demo\demo.ps1 -Action Check

# Sau khi dừng Web bằng Ctrl+C: sao lưu dữ liệu + toàn bộ ảnh/chữ ký demo
.\tools\demo\demo.ps1 -Action Snapshot

# Sau khi dừng Web: tự sao lưu trạng thái trước reset rồi tạo lại bộ giả lập
.\tools\demo\demo.ps1 -Action Reset

# Kiểm thử HTTP đầy đủ trên V2 đang được đánh dấu diễn tập
.\tools\demo\demo.ps1 -Action Verify
```

`Reset` yêu cầu `RentalSystemDB_V2` có dấu diễn tập và cổng 5001 đã dừng. Công cụ sao lưu fixture trước khi xóa và nạp lại dữ liệu mẫu. Ngày và kỳ thanh toán được tính theo ngày chạy. `Prepare` nạp mẫu trên cơ sở dữ liệu trống hoặc cập nhật ảnh mẫu của fixture hiện có.

Mỗi lần reset có dữ liệu sẽ tạo thư mục `outputs/demo-check/snapshots/<thời-gian>-pre-reset/` gồm `database.json`, `uploads/` và `manifest.json`. `Snapshot` tạo gói tương tự. `baseline.json` chứa dữ liệu ban đầu để thử khôi phục. JSON không chứa nội dung ảnh, phải giữ thư mục `uploads` cùng bản sao lưu. Bản baseline và snapshot có mật khẩu **giả lập** để đăng nhập phục vụ diễn tập.

Phần mềm có thể tự nạp lại dữ liệu khi thiếu 7 hợp đồng, 20 thiết bị hoặc 10 kỳ thanh toán. Bộ demo có 7/24/13 để vượt điều kiện này. Không xóa bớt dữ liệu nền. `Verify` thực hiện đặt thuê qua API với payload giống Mobile, kiểm tra lại trên Web kinh doanh, phân công và sửa qua Web, đánh giá qua API, xuất Excel/biểu mẫu, sao lưu, khôi phục và khởi động lại. Đây là kiểm thử HTTP; không thay cho thao tác Android và tập có bấm giờ.

## Tệp minh chứng

- `outputs/demo-check/manifest.json`: mã dữ liệu, tài khoản và kỳ báo cáo.
- `outputs/demo-check/baseline.json`: sao lưu bộ dữ liệu gốc.
- `outputs/demo-check/wwwroot/uploads/demo/`: chữ ký giả lập và hai ảnh giấy tờ PNG đã che thông tin, có nhãn DEMO.
- `outputs/demo-check/snapshots/`: gói sao lưu dữ liệu kèm tệp ảnh.
- `outputs/demo-check/evidence/`: Excel, hợp đồng HTML, biên bản HTML, phiếu thu HTML và sao lưu sau diễn tập được lấy từ CSDL kiểm chứng cùng bộ giả lập. Các tệp HTML dùng ảnh tại `../wwwroot/`; giữ nguyên cấu trúc thư mục khi sao chép.
- `outputs/demo-check/verification.json`: kết quả kiểm chứng HTTP và các hạng mục điện thoại còn cần thực hiện.
- `outputs/demo-check/videos/`: video do bạn quay trên điện thoại thật.

Biểu mẫu HTML có thể mở trực tiếp bằng trình duyệt và in/lưu PDF bằng Ctrl+P. Các liên kết thao tác trong bản xuất chỉ là ảnh chụp nội dung HTML; dùng Web đang chạy để thực hiện nghiệp vụ.

## Quay video dự phòng và tập hai lượt

```powershell
# Thực hiện khi Web và Mobile đang chạy; đóng cửa sổ scrcpy để chốt tệp MP4
.\tools\demo\demo.ps1 -Action Record -Clip 01-dat-thue
.\tools\demo\demo.ps1 -Action Record -Clip 02-bao-su-co
.\tools\demo\demo.ps1 -Action Record -Clip 03-xem-ket-qua-danh-gia
```

Lệnh ghi video màn hình điện thoại, không thu giọng nói và không ghi màn hình Web. Quay phần Web bằng công cụ ghi màn hình có sẵn trên laptop khi tập. Sau khi quay phải mở thử từng MP4, xác nhận đúng dữ liệu, đủ đầu/cuối và dễ đọc mã. Không ghi nhận video hoàn thành khi chưa có tệp thật.

| Lượt tập | Tổng thời gian | Đơn mới Mobile→Web | Sự cố→xử lý→đánh giá | Video mở được | Đạt ≤12 phút |
|---|---|---|---|---|---|
| 1 | Chưa thực hiện | ☐ | ☐ | ☐ | ☐ |
| 2 | Chưa thực hiện | ☐ | ☐ | ☐ | ☐ |

Sau mỗi lượt: dừng backend, Snapshot nếu muốn giữ kết quả, Reset, mở Web lại và làm mới dữ liệu trên Mobile. Trước 30 phút: kiểm tra SQL, USB, pin, chiếu màn hình, kỳ báo cáo, tệp dự phòng. Trước 5 phút: kiểm tra đăng nhập, tắt thông báo, mở bảng nhắc. Sau buổi tập: có thể gỡ chuyển tiếp bằng `adb reverse --remove tcp:5000`.

## Phạm vi cần nói đúng khi trả lời hội đồng

- Web và Mobile dùng chung backend/dữ liệu cho các luồng đã kiểm chứng. Tải lại danh sách để thấy cập nhật; không gọi là đồng bộ tức thời nếu chưa tải lại.
- Minh họa chữ ký viết tay trên giao diện bằng dữ liệu giả lập; không gọi đây là chữ ký số có chứng thư.
- Không dùng luồng lắp đặt cục bộ và ảnh đính kèm mô phỏng làm bằng chứng dữ liệu đã được gửi lên máy chủ.
- Quyền truy cập nêu trong demo được minh họa bằng phiên Web. Không khẳng định API dùng JWT: mã hiện tại chưa có cơ chế xác thực JWT tương ứng.
- Khi hỏi chống trùng thuê hoặc bảo mật API, phân biệt rõ luồng MVC và Mobile API. Bộ demo này không sửa cơ chế nghiệp vụ hay bổ sung bảo mật API.
- Thanh toán: giới thiệu trạng thái và phiếu thu giả lập đã chuẩn bị; không nói đang kết nối ngân hàng thật khi không có giao dịch thật.

Nếu sự cố kết nối kéo dài quá 20 giây, chuyển bản quay và nói rõ “Em xin sử dụng bản quay trước của bước này”. Kịch bản chi tiết có lời chuyển sang dữ liệu dự phòng.
