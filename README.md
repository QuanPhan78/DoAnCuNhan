# RentalSystem - Hệ Thống Quản Lý & Cho Thuê Thiết Bị Điện Tử

> **Đồ Án Khóa Luận Tốt Nghiệp Cử Nhân CNTT**  
> Hệ thống kết hợp đa nền tảng gồm **Web Quản trị & Nghiệp vụ (ASP.NET Core 9)** và **Ứng dụng Di động (Flutter 3)** dành cho Khách hàng & Kỹ thuật viên hiện trường.

---

## 1. Kiến Trúc & Công Nghệ Cốt Lõi

- **Backend Web / Web API**: ASP.NET Core 9.0, Entity Framework Core 9, SQL Server, Kestrel.
- **Frontend Web**: Razor Pages, Bootstrap 5, semantic CSS chuẩn *Executive Deep Navy* (`classic-navy.css`).
- **Mobile App**: Flutter 3 (Dart 3.x), Provider State Management, `url_launcher` (In-App Browser & Deep Linking).
- **Cổng thanh toán & Ngân hàng**:
  - VNPay Sandbox trực tuyến (tích hợp Web và In-App Deep Link `rentalsystem://payment-result`).
  - Open Banking Webhook tự động đối soát và gạch nợ ngân hàng.
  - VietQR động sinh mã chuyển khoản kèm nội dung đối soát.

---

## 2. Hướng Dẫn Cài Đặt & Khởi Động Nhanh (Quickstart)

### Bước 1: Khởi tạo Cơ sở dữ liệu (SQL Server)
1. Mở **SQL Server Management Studio (SSMS)** hoặc **Azure Data Studio**.
2. Kết nối tới máy chủ SQL Server cục bộ (`localhost` hoặc `(localdb)\mssqllocaldb`).
3. Mở và thực thi toàn bộ script:
   ```text
   MobileApp/RentalSystemDB.sql
   ```
   *(Script đã bao gồm toàn bộ bảng cốt lõi, dữ liệu thiết bị, tài khoản mẫu và các bản cập nhật migration từ 001 đến 004).*

### Bước 2: Khởi động Backend Web & Web API
1. Kiểm tra chuỗi kết nối trong `RentalSystem/appsettings.json`:
   ```json
   "ConnectionStrings": {
     "DefaultConnection": "Server=localhost;Database=RentalSystemDB_V2;Trusted_Connection=True;TrustServerCertificate=True;"
   }
   ```
2. Khởi động Web API tại cổng `5000`:
   ```powershell
   dotnet run --project RentalSystem/RentalSystem.csproj --urls "http://0.0.0.0:5000"
   ```
3. Truy cập trình duyệt: [http://localhost:5000](http://localhost:5000)

### Bước 3: Khởi động Ứng dụng Di động (Flutter)
1. **Nếu chạy trên thiết bị thật cắm cáp USB (Khuyên dùng)**:
   - Bật **USB Debugging** trên điện thoại.
   - Chạy lệnh chuyển tiếp cổng:
     ```powershell
     adb reverse tcp:5000 tcp:5000
     ```
   - Khởi chạy ứng dụng:
     ```powershell
     cd MobileApp
     flutter run --dart-define=API_BASE_URL=http://127.0.0.1:5000/api
     ```
2. **Nếu chạy trên Android Emulator**:
   ```powershell
   cd MobileApp
   flutter run --dart-define=API_BASE_URL=http://10.0.2.2:5000/api
   ```

---

## 3. Danh Sách Tài Khoản Kiểm Thử Phân Quyền (Demo Accounts)

Hệ thống đã nạp sẵn dữ liệu mẫu để thuận tiện cho việc đánh giá và chấm điểm khóa luận:

| Vai trò | Tên đăng nhập | Mật khẩu | Chức năng chính |
| :--- | :--- | :--- | :--- |
| **Quản trị viên (Admin)** | `admin` | `admin@123` | Quản trị thiết bị, phê duyệt hợp đồng, báo cáo doanh thu & công nợ |
| **Nhân viên Kỹ thuật** | `kythuat01` | `123456` | Tiếp nhận lịch bàn giao máy, ký biên bản lắp đặt, xử lý sự cố & bảo trì trên Mobile |
| **Nhân viên Kinh doanh** | `kinhdoanh01` | `123456` | Lập hợp đồng, quản lý khách hàng, kiểm duyệt đề xuất thuê |
| **Kế toán** | `ketoan01` | `123456` | Quản lý phiếu thu chi, quyết toán hợp đồng, đối soát thanh toán ngân hàng |
| **Khách hàng** | `khachhang01` | `123456` | Xem giỏ hàng, ký hợp đồng điện tử, thanh toán kỳ hạn VNPay trên Mobile & Web |

---

## 4. Kiểm Thử Thanh Toán Trực Tuyến VNPay

- **Thông số Sandbox cấu hình sẵn**:
  - `TmnCode`: `DVMQNJYZ`
  - `HashSecret`: `FKBFZYKDCFNVHTECOAJCVNRTNCNLHNUI`
  - `BaseUrl`: `https://sandbox.vnpayment.vn/paymentv2/vpcpay.html`
- **Thẻ kiểm thử nội địa VNPay Sandbox**:
  - Ngân hàng: **NCB**
  - Số thẻ: `9704198526191432198`
  - Tên chủ thẻ: `NGUYEN VAN A`
  - Ngày phát hành: `07/15`
  - Mã OTP: `123456`
- **Cơ chế Deep Linking Mobile**: Sau khi hoàn tất trên cổng VNPay, hệ thống tự động gọi schema `rentalsystem://payment-result` để mở lại app di động, đối soát tự động và hiển thị màn hình kết quả gạch nợ tức thì.
