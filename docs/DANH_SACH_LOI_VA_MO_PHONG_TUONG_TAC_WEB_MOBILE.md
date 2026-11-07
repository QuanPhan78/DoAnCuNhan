# BÁO CÁO TOÀN DIỆN DANH MỤC LỖI KỸ THUẬT & MA TRẬN MÔ PHỎNG TƯƠNG TÁC HỆ THỐNG RENTALSYSTEM (WEB & MOBILE)

**Dự án**: Hệ thống Quản trị & Vận hành Cho thuê Thiết bị Công nghệ (RentalSystem)  
**Phân hệ khảo sát**: Web ASP.NET Core MVC 9.0 (C# 12) & Mobile App Flutter 3.38.7 (Dart 3.10.7)  
**Cơ sở dữ liệu**: Microsoft SQL Server 2022 (EF Core 9.0)  
**Tài liệu đối chiếu căn bản**: `CNTT_KLCN058.docx` (Khóa luận tốt nghiệp cử nhân CNTT)  
**Tác giả thẩm định**: `worker_sim_m2_1` (Role: Defect & Simulation Author)  
**Ngày phát hành**: 07/11/2026  
**Trạng thái**: Hoàn tất khảo sát, phân loại lỗi và xây dựng ma trận mô phỏng  

---

## MỤC LỤC TỔNG QUAN

1. [PHẦN I: QUY TRÌNH & MÔI TRƯỜNG KHỞI CHẠY, MÔ PHỎNG TƯƠNG TÁC CỤC BỘ](#phần-i-quy-trình--môi-trường-khởi-chạy-mô-phỏng-tương-tác-cục-bộ)
   - 1.1. Yêu cầu môi trường & Ngăn xếp công nghệ
   - 1.2. Quy trình khởi chạy phân hệ Web Backend (ASP.NET Core MVC 9.0)
   - 1.3. Quy trình khởi chạy phân hệ Mobile Client (Flutter Desktop & Web)
   - 1.4. Quy trình điều phối công cụ tự động hóa (DemoHarness, Python CDP, Reverse Proxy)
   - 1.5. Danh mục tài khoản kiểm thử chuẩn & Dữ liệu diễn tập
2. [PHẦN II: DANH MỤC TỔNG THỂ CÁC LỖI VÀ BẤT CẬP PHÁT HIỆN ĐƯỢC (DEFECT CATALOG)](#phần-ii-danh-mục-tổng-thể-các-lỗi-và-bất-cập-phát-hiện-được-defect-catalog)
   - 2.1. Tiêu chí phân cấp mức độ nghiêm trọng (Severity Taxonomy)
   - 2.2. Bảng tổng hợp Danh mục Lỗi DEF-01 đến DEF-14
   - 2.3. Ma trận phân bố lỗi theo phân hệ và mức độ ảnh hưởng
3. [PHẦN III: PHÂN TÍCH CHI TIẾT TỪNG NHÓM LỖI VÀ BẤT CẬP KỸ THUẬT](#phần-iii-phân-tích-chi-tiết-từng-nhóm-lỗi-và-bất-cập-kỹ-thuật)
   - 3.1. Nhóm 1: Các lỗi ngớ ngẩn (Silly Bugs), rò rỉ dữ liệu cá nhân & điểm nghẽn UX
   - 3.2. Nhóm 2: Sai lệch trạng thái hiển thị & Vi phạm chuẩn giao diện doanh nghiệp Classic Navy
   - 3.3. Nhóm 3: Bất đối xứng nghiêm trọng luồng nghiệp vụ Web vs Mobile (Parity Breaks)
   - 3.4. Nhóm 4: Lỗi biên dịch bộ kiểm thử tự động `ChallengerTests`
4. [PHẦN IV: MA TRẬN KỊCH BẢN MÔ PHỎNG TƯƠNG TÁC THỰC TẾ TỪNG MÀN HÌNH](#phần-iv-ma-trận-kịch-bản-mô-phỏng-tương-tác-thực-tế-từng-màn-hình)
   - 4.1. Ma trận mô phỏng 4 vai trò trên phân hệ Web (Admin, Kinh Doanh, Kỹ Thuật, Khách Hàng)
   - 4.2. Ma trận mô phỏng 3 vai trò trên phân hệ Mobile (Khách Hàng, Nhân Viên, Quản Lý)
   - 4.3. Kịch bản mô phỏng tích hợp liên nền tảng xuyên suốt vòng đời thuê máy
5. [PHẦN V: KẾT LUẬN & ĐỀ XUẤT NỀN TẢNG CHO KẾ HOẠCH SỬA ĐỔI](#phần-v-kết-luận--đề-xuất-nền-tảng-cho-kế-hoạch-sửa-đổi)

---

## PHẦN I: QUY TRÌNH & MÔI TRƯỜNG KHỞI CHẠY, MÔ PHỎNG TƯƠNG TÁC CỤC BỘ

### 1.1. Yêu cầu môi trường & Ngăn xếp công nghệ

Hệ thống RentalSystem được thiết kế vận hành hoàn toàn trên môi trường máy trạm cục bộ độc lập (Offline-ready/Localhost), không phụ thuộc vào các dịch vụ đám mây công cộng bên ngoài. Cấu hình môi trường yêu cầu gồm:

- **Hệ điều hành**: Microsoft Windows 10/11 x64 hoặc Windows Server 2022.
- **Hạ tầng Backend**: .NET SDK 9.0.305, C# 12, ASP.NET Core MVC 9.0 chạy trên máy chủ nội tại Kestrel.
- **Hệ quản trị CSDL**: Microsoft SQL Server 2022 (v17.0.1000.7) với Entity Framework Core 9.0.0. Chuỗi kết nối cục bộ:
  `Server=localhost;Database=RentalSystemDB_V2;Trusted_Connection=True;TrustServerCertificate=True;MultipleActiveResultSets=true`.
- **Hạ tầng Mobile**: Flutter SDK 3.38.7, Dart SDK 3.10.7, BLoC / Provider Pattern, Dio 5.x HTTP Client, Syncfusion PDF / Printing, Flutter Secure Storage.
- **Hạ tầng Tự động hóa**: Python 3.12/3.14 (với các thư viện `websockets`, `pillow`, `urllib`), Chrome Browser v156 (hỗ trợ Remote Debugging qua cổng 9222).

---

### 1.2. Quy trình khởi chạy phân hệ Web Backend (ASP.NET Core MVC 9.0)

Phân hệ Web cung cấp toàn bộ giao diện quản trị (Admin/Kinh Doanh/Kỹ Thuật), cổng thông tin khách hàng cá nhân và hệ thống RESTful API cho ứng dụng di động:

```powershell
# Bước 1: Điều hướng đến thư mục giải pháp
cd d:\DoAnCuNhan

# Bước 2: Kiểm tra biên dịch mã nguồn Web
dotnet build RentalSystem\RentalSystem.csproj --configuration Debug

# Bước 3: Áp dụng các bản cập nhật lược đồ CSDL (Migrations 001 đến 004)
# (CSDL RentalSystemDB_V2 đã được tích hợp sẵn 18 bảng chuẩn + 2 bảng kiểm toán)

# Bước 4: Khởi chạy máy chủ Web Kestrel trên cổng 5000 (HTTP) và 5001 (HTTPS nếu có)
dotnet run --project RentalSystem\RentalSystem.csproj --urls "http://localhost:5000"
```

*Dấu hiệu kiểm chứng sẵn sàng*: Console hiển thị `Now listening on: http://localhost:5000`. Truy cập `http://localhost:5000` trên trình duyệt trả về mã HTTP 200 trang chủ RentalSystem trong vòng dưới 2.0 giây.

---

### 1.3. Quy trình khởi chạy phân hệ Mobile Client (Flutter Desktop & Web)

Ứng dụng di động Flutter hỗ trợ biên dịch đa nền tảng. Trong môi trường phát triển máy trạm Windows, có thể khởi chạy ứng dụng trực tiếp dưới dạng Windows Desktop App hoặc Chrome Web App mà không cần cắm thiết bị Android vật lý:

```powershell
# Bước 1: Điều hướng đến thư mục mã nguồn Mobile
cd d:\DoAnCuNhan\MobileApp

# Bước 2: Kiểm tra phân tích tĩnh và bộ kiểm thử đơn vị
flutter analyze
flutter test
# Kết quả kỳ vọng: 0 issues found, 13/13 test files passed 100%

# Bước 3.1: Khởi chạy ứng dụng trực tiếp trên Windows Desktop (Khuyến nghị cho trải nghiệm mượt mà)
flutter run -d windows

# Bước 3.2: Hoặc khởi chạy trên Trình duyệt Google Chrome
flutter run -d chrome --web-port 8080
```

*Lưu ý cấu hình Endpoint API*: Trong tệp `MobileApp\lib\services\api_config.dart`, địa chỉ máy chủ mặc định trỏ tới `http://localhost:5000/api` đối với phiên bản Windows Desktop/Chrome Web, hoặc `http://10.0.2.2:5000/api` đối với máy ảo Android Emulator.

---

### 1.4. Quy trình điều phối công cụ tự động hóa (DemoHarness, Python CDP, Reverse Proxy)

Dự án trang bị sẵn hệ thống công cụ hỗ trợ mô phỏng, chụp ảnh minh chứng và kiểm thử tự động:

1. **Công cụ điều phối kịch bản diễn tập `DemoHarness` (`tools/demo/`)**:
   ```powershell
   # Biên dịch và kiểm tra trạng thái dữ liệu diễn tập
   dotnet run --project tools\demo\DemoHarness.csproj -- Check
   # Thiết lập lại dữ liệu sạch theo kịch bản mẫu 11 phút 30 giây
   dotnet run --project tools\demo\DemoHarness.csproj -- Reset
   ```
2. **Kịch bản tự động hóa chụp ảnh giao diện chất lượng cao (`tools/capture_ui_screenshots.py`)**:
   - Sử dụng giao thức Chrome DevTools Protocol (CDP) kết nối tới Chrome headless/headed tại cổng 9222.
   - Thiết lập khung nhìn chuẩn 1920x1080, tự động đăng nhập 4 vai trò, điều hướng qua các trang nghiệp vụ và chụp ảnh độ nét cao lưu vào thư mục `figures/`.
3. **Kịch bản kiểm thử tải đối kháng và API di động (`tools/mobile_e2e_test.py`)**:
   - Thực thi 42 ca kiểm thử tích hợp xuyên suốt vòng đời API di động (100% PASS).
4. **Bộ kịch bản kiểm tra toàn vẹn CSDL SQL Server (`tools/database/`)**:
   - Gồm 8 kịch bản Python kiểm tra tự động: `verify_api_access.py`, `verify_rental_booking.py`, `verify_debt_status.py`, `verify_contract_lifecycle.py`, `verify_contract_settlements.py`, `verify_customer_maintenance.py`, `verify_maintenance_assignments.py`, `verify_operations_reports.py`.

---

### 1.5. Danh mục tài khoản kiểm thử chuẩn & Dữ liệu diễn tập

Hệ thống cấu hình sẵn 4 tài khoản định danh tương ứng với 4 vai trò nghiệp vụ được chỉ định trong `CNTT_KLCN058.docx`:

| Vai trò Nghiệp vụ | Mã Vai Trò | Email Đăng Nhập | Mật Khẩu Chuẩn | Quyền Hạn & Phạm Vi Truy Cập |
|:---|:---:|:---|:---:|:---|
| **Quản trị viên (Admin)** | 1 | `admin@rentalsystem.com` | `Admin@123` | Toàn quyền cấu hình hệ thống, duyệt hợp đồng, quyết toán hoàn cọc, phân công kỹ thuật, xuất báo cáo BI và sao lưu CSDL |
| **Nhân viên Kinh doanh (Sales)** | 4 | `sale.linh@rentalsystem.com` | `Linh@123` | Tiếp nhận yêu cầu thuê, duyệt đơn, ký số nhân viên, theo dõi công nợ, duyệt gia hạn hợp đồng |
| **Kỹ thuật viên (Technician)** | 3 | `kt.tuan@rentalsystem.com` | `Tuan@123` | Lập biên bản bàn giao máy, lập biên bản thu hồi, tiếp nhận phiếu bảo trì sự cố, cập nhật tiến độ sửa chữa |
| **Khách hàng (Customer)** | 2 | `khach@gmail.com` | `123456` | Xem danh mục máy, đặt thuê, ký Canvas, tải CCCD, thanh toán VietQR, báo sự cố, nghiệm thu & đánh giá bảo trì |

*Tài khoản diễn tập bổ sung (Demo Data)*: `customer@demo.invalid`, `sales@demo.invalid`, `tech-a@demo.invalid`, `admin@demo.invalid` (Mật khẩu chung: `Demo@123`).

---

## PHẦN II: DANH MỤC TỔNG THỂ CÁC LỖI VÀ BẤT CẬP PHÁT HIỆN ĐƯỢC (DEFECT CATALOG)

### 2.1. Tiêu chí phân cấp mức độ nghiêm trọng (Severity Taxonomy)

- **Blocker (Chặn hệ thống)**: Gây lỗi biên dịch mã nguồn, làm hỏng quy trình CI/CD hoặc làm ứng dụng sập (crash) hoàn toàn không thể khởi chạy.
- **Critical (Nghiêm trọng)**: Gây sai lệch dòng tiền, đứt gãy luồng quy trình nghiệp vụ cốt lõi, rò rỉ dữ liệu nhạy cảm hoặc vi phạm an toàn thông tin nghiêm trọng.
- **Major (Lớn)**: Khiếm khuyết chức năng lớn, mất tính tương đương tính năng giữa Web và Mobile (Parity Break), vi phạm tiêu chuẩn thiết kế giao diện doanh nghiệp hoặc hỏng luồng thao tác người dùng.
- **Minor (Nhỏ)**: Các khiếm khuyết hiển thị nhỏ, lỗi chính tả/class HTML lặp, trải nghiệm người dùng (UX Quirk) chưa tối ưu nhưng không chặn thao tác nghiệp vụ.

---

### 2.2. Bảng tổng hợp Danh mục Lỗi DEF-01 đến DEF-14

<p align="center"><b>Bảng 2.1: Danh mục 14 lỗi kỹ thuật và bất cập trải nghiệm Web - Mobile (DEF-01 đến DEF-14)</b></p>

| Mã Lỗi | Phân Hệ | Mức Độ | Vị Trí Tệp Mã Nguồn / Dòng | Tên Lỗi / Bất Cập | Tóm Tắt Hiện Tượng & Hậu Quả |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **DEF-01** | API / Backend | **Critical** | `RentalSystem/Controllers/ApiContractsController.cs:278-298` | Lỗi logic nghiệp vụ API Gia hạn hợp đồng | API `POST /api/contracts/{id}/renew` chỉ nối chuỗi văn bản vào `HopDong.GhiChu`. Không tạo bản ghi `YeuCauGiaHan`, không bật cờ `HopDong.YeuCauGiaHan = true`, làm yêu cầu từ Mobile bị biến mất hoàn toàn khỏi màn hình duyệt của Admin. |
| **DEF-02** | Test / Build | **Blocker** | `ChallengerTests/Program.cs:1971-1975` & `RentalSystem/Common/DebtCalculationHelper.cs:48-56` | Lỗi biên dịch CS0117 & Phân kỳ tên nhóm tuổi nợ | `ChallengerTests` gọi `DebtCalculationHelper.GetAgingBadgeClass` nhưng hàm này không tồn tại trong `DebtCalculationHelper.cs`. Tên nhóm tuổi nợ `GetAgingTierName` trả về chuỗi lệch với kỳ vọng assertion của bộ test. |
| **DEF-03** | Web UI / Security | **Critical** | `RentalSystem/Views/Cart/ContractDetail.cshtml:380,396,400` & `Views/Account/MyDebt.cshtml:519` | Rò rỉ thông tin tài khoản ngân hàng cá nhân | Hardcode số tài khoản cá nhân `0783406516`, tên chủ tài khoản `PHAN MINH QUAN` (MBBank) trên giao diện thanh toán VietQR, buộc kịch bản chụp ảnh phải tiêm script khử khuẩn DOM để che giấu. |
| **DEF-04** | Web UI / UX | **Major** | `RentalSystem/Views/Cart/ContractDetail.cshtml:76` & dòng 361-367 | Nút bấm chuyển khoản đợt đầu lệch chuẩn & Rủi ro phạm vi Razor | Nút bấm "Chuyển khoản ... đ" dùng class Bootstrap cũ `.btn-primary` thiếu icon; cần chuẩn hóa sang `.btn-navy` và bảo đảm an toàn biên dịch (không tham chiếu biến `shouldShowVietQr` hạ nguồn để tránh lỗi CS0103). |
| **DEF-05** | Mobile Feature | **Major** | `MobileApp/lib/screens/requests/rental_confirm_screen.dart:55` | Mobile thiếu hoàn toàn Ký số Canvas và Tải ảnh CCCD | Ứng dụng di động không có màn hình ký điện tử và tải ảnh định danh. Dialog thông báo yêu cầu người dùng: *"Bạn có thể ký hợp đồng trên Web."*, phá vỡ quy trình nghiệp vụ khép kín trên di động. |
| **DEF-06** | Mobile Feature | **Major** | `MobileApp/lib/screens/contracts/` & `MobileApp/lib/datasources/` | Mobile thiếu Sổ công nợ và chức năng quét VietQR | Khách hàng trên Mobile không có màn hình xem danh sách kỳ hạn nợ, không xem được tuổi nợ, không có trình tạo mã QR VietQR động và không thể gửi minh chứng thanh toán đối soát. |
| **DEF-07** | Mobile Feature | **Major** | `MobileApp/lib/screens/requests/rental_form_screen.dart` | Giỏ hàng đơn máy trên Mobile vs Đa máy trên Web | Phân hệ Web hỗ trợ giỏ hàng đa sản phẩm (`/Cart`), trong khi Mobile chỉ cho phép đặt thuê duy nhất 1 thiết bị đơn lẻ mỗi lượt giao dịch, gây bất đối xứng tính năng lớn. |
| **DEF-08** | Mobile RBAC | **Major** | `MobileApp/lib/models/role_enum.dart:22-24` | Gộp chung vai trò Kinh doanh và Kỹ thuật (`Role.staff`) | Mobile gộp chung `kinhdoanh` và `kythuat` thành `Role.staff`, khiến nhân viên kinh doanh cũng nhìn thấy màn hình điều phối kỹ thuật và ngược lại, vi phạm phân định trách nhiệm nghiệp vụ. |
| **DEF-09** | Mobile UX | **Minor** | `MobileApp/lib/screens/requests/rental_detail_screen.dart` | Bất đồng bộ tiến trình (Timeline Mismatch) | Backend quản lý 5 trạng thái vòng đời hợp đồng (`HopDong.TrangThai` từ 0 đến 4), trong khi Mobile tự vẽ Timeline 7 bước giả lập cục bộ ("Đang chuẩn bị", "Đang giao", "Đã lắp đặt"...), không khớp với CSDL. |
| **DEF-10** | Web UI / Design | **Major** | `RentalSystem/Areas/Admin/Views/CongNo/Index.cshtml:43,59,75,212,226` & `CongNoController.cs` | Vi phạm chuẩn thiết kế Classic Navy & Thiếu các chỉ số Milestone 4 | Giao diện dùng class utility dài, màu neon chói lọi; thiếu thẻ KPI Khoản nợ xấu (`ViewBag.SoKhoanNoXau`), thiếu khối phân kỳ 4 nhóm tuổi nợ và class `.bg-orange` kiểm thử bởi `ChallengerTests`. |
| **DEF-11** | Web UI / Design | **Major** | `RentalSystem/Areas/Admin/Views/Database/Index.cshtml:41,57,73,89` | Vi phạm chuẩn thẻ trạng thái và viền màu neon | Dùng thẻ card tiện ích Bootstrap viền neon (`border-info`, `border-success`, `border-warning`) thay vì đóng gói chuẩn `.stat-card` và `.admin-card` theo quy định tại `classic-navy.css`. |
| **DEF-12** | Web UI / HTML | **Minor** | `Views/Cart/Checkout.cshtml:15`, `SignContract.cshtml:19,99`, `PhanCong/Create.cshtml:97` | Trùng lặp class, xung đột màu & Xung đột tiện ích `bg-white` vs `admin-card` | Thẻ HTML chứa class mâu thuẫn (`text-warning` và `text-dark`, lặp `fw-bold`), đồng thời pha trộn chuỗi class Bootstrap dài (`card border-0 shadow-sm rounded-3 bg-white`) với semantic class `.admin-card` làm vỡ tính đóng gói CSS. |
| **DEF-13** | Web UI / Form | **Major** | `Views/Account/Register.cshtml`, `Views/Cart/Checkout.cshtml`, `Views/BaoTri/TaoPhieu.cshtml`... | Thiếu `_ValidationScriptsPartial` trên các form quan trọng | Chỉ 4 view Thiết bị & Sản phẩm có script validate. Các form đăng ký, checkout, tạo phiếu bảo trì thiếu validate phía client, gây reload toàn trang khi submit lỗi, làm mất dữ liệu người dùng đã gõ. |
| **DEF-14** | Web UI / Design | **Minor** | `RentalSystem/Views/Home/Index.cshtml:19,28,37` & `Views/Cart/Checkout.cshtml:44` | Sử dụng nút bấm lệch chuẩn phong cách doanh nghiệp | Sử dụng nút `btn-dark rounded-pill` kiểu bo tròn thể thao và `btn-outline-primary` thay vì các class semantic quy chuẩn `.btn-navy` và `.btn-outline-navy`. |

---

### 2.3. Ma trận phân bố lỗi theo phân hệ và mức độ ảnh hưởng

```
               +-----------+------------+----------+----------+
               |  Blocker  |  Critical  |  Major   |  Minor   |  Tổng cộng
+--------------+-----------+------------+----------+----------+
| Backend / API|     0     |     1      |    0     |    0     |     1
| Test Suite   |     1     |     0      |    0     |    0     |     1
| Web UI / UX  |     0     |     1      |    3     |    2     |     6
| Mobile App   |     0     |     0      |    5     |    1     |     6
+--------------+-----------+------------+----------+----------+
| Tổng cộng    |     1     |     2      |    8     |    3     |    14
```

---

## PHẦN III: PHÂN TÍCH CHI TIẾT TỪNG NHÓM LỖI VÀ BẤT CẬP KỸ THUẬT

### 3.1. Nhóm 1: Các lỗi ngớ ngẩn (Silly Bugs), rò rỉ dữ liệu cá nhân & điểm nghẽn UX

#### 3.1.1. DEF-03: Hardcoded thông tin STK cá nhân (0783406516 - PHAN MINH QUAN) & Cơ chế DOM Sanitizer bắt buộc
- **Vị trí tệp và dòng mã**:
  - `RentalSystem/Views/Cart/ContractDetail.cshtml` dòng 380, dòng 396 và dòng 400.
  - `RentalSystem/Views/Account/MyDebt.cshtml` dòng 519 và dòng 523.
- **Trích xuất mã nguồn thực tế**:
  ```html
  <!-- Views/Cart/ContractDetail.cshtml:380-400 -->
  <img src="https://img.vietqr.io/image/MB-0783406516-compact.png?amount=@(vietQrAmountLong)&addInfo=@(vietQrMessage)&accountName=PHAN%20MINH%20QUAN" 
       alt="QR Code Chuyển khoản VietQR" ... />
  ...
  <td class="text-muted">Số tài khoản / Account Number:</td>
  <td class="fw-bold text-brand fs-5">0783406516</td>
  ...
  <td class="text-muted">Chủ tài khoản / Account Name:</td>
  <td class="fw-bold text-dark text-uppercase">PHAN MINH QUAN</td>
  ```
- **Hiện tượng & Bằng chứng kiểm toán**:
  - Thông tin tài khoản ngân hàng cá nhân thực tế bị gắn chết trong mã nguồn HTML Razor.
  - Khi triển khai kịch bản tự động chụp ảnh báo cáo khoa học `tools/capture_ui_screenshots.py`, tác giả đã buộc phải viết một đoạn script Javascript tiêm vào trình duyệt (`DOM_SANITIZER_JS`, dòng 36-45) để tìm kiếm và thay thế cưỡng bức các chuỗi này thành tài khoản doanh nghiệp hư cấu (`VietinBank - 101889998888 - NGUYEN VAN AN`):
    ```javascript
    // Trích từ tools/capture_ui_screenshots.py:38-44
    return str
        .replace(/0783406516/g, '0987654321')
        .replace(/PHAN\s*MINH\s*QUAN/gi, 'NGUYEN VAN AN')
        .replace(/Phan\s*Minh\s*Quân/gi, 'Nguyễn Văn An')
        .replace(/MBBank\s*\(0783406516\)/g, 'VietinBank - 101889998888');
    ```
- **Mức độ nghiêm trọng**: **Critical**. Rò rỉ dữ liệu cá nhân, vi phạm chuẩn mực doanh nghiệp và gây rủi ro thất thoát dòng tiền nếu chuyển nhầm tài khoản cá nhân thay vì tài khoản công ty.
- **Giải pháp khắc phục đề xuất**:
  - Đưa toàn bộ cấu hình tài khoản thụ hưởng vào tệp `appsettings.json` dưới mục `BankingConfig: { BankId: "ICB", AccountNo: "101889998888", AccountName: "CONG TY TNHH RENTAL SYSTEM" }`.
  - Tiêm `IOptions<BankingConfig>` vào Controller/View thông qua Dependency Injection.

---

#### 3.1.2. DEF-04: Dead Anchor Link `#bankTransferInstructions` tại `ContractDetail.cshtml`
- **Vị trí tệp và dòng mã**: `RentalSystem/Views/Cart/ContractDetail.cshtml` dòng 76 và dòng 361-367.
- **Trích xuất mã nguồn thực tế**:
  ```html
  <!-- Dòng 76: Nút bấm điều hướng -->
  <a class="btn btn-primary mt-2" href="#bankTransferInstructions">Chuyển khoản @Math.Ceiling(firstBalance.Total).ToString("N0") đ</a>

  <!-- Dòng 361-367: Khối hiển thị có điều kiện -->
  @{
      bool shouldShowVietQr = pendingFirstPayment
          ? canTransferFirstPayment && firstBalance.Total > 0
          : (!Model.YeuCauThanhToanLanDau || Model.TrangThai != 3) && (hasUnpaidInstallments || unpaidDamages > 0 || vietQrAmountLong > 0);
  }
  @if (shouldShowVietQr)
  {
      <div class="card border border-primary shadow-sm mb-4" id="bankTransferInstructions">
  ```
- **Hiện tượng & Bằng chứng kiểm toán**:
  - Khi hợp đồng đang ở trạng thái Chờ duyệt nhưng biến `canTransferFirstPayment` bằng `false` (ví dụ: khách chưa ký Canvas hoặc nhân viên chưa ký số xác nhận), biểu thức `shouldShowVietQr` nhận giá trị `false`.
  - Hậu quả là phần tử `<div id="bankTransferInstructions">` hoàn toàn không được render ra cây DOM.
  - Tuy nhiên, khối thông báo alert ở dòng 76 vẫn hiển thị nút `<a href="#bankTransferInstructions">Chuyển khoản ... đ</a>`. Khi người dùng bấm chuột vào nút này, trình duyệt không tìm thấy anchor tương ứng, hoàn toàn không có phản hồi thị giác nào, tạo cảm giác nút bị liệt.
- **Mức độ nghiêm trọng**: **Major**. Gây nhầm lẫn nghiêm trọng cho khách hàng trong bước thanh toán tiền cọc đợt đầu.
- **Giải pháp khắc phục đề xuất**:
  - Bọc nút bấm tại dòng 76 trong điều kiện đồng bộ `@if (shouldShowVietQr)`. Nếu chưa đủ điều kiện chuyển khoản, hiển thị thông báo hướng dẫn: *"Vui lòng hoàn tất ký hợp đồng trước khi thanh toán"*.

---

#### 3.1.3. DEF-13: Thiếu `_ValidationScriptsPartial` gây reload mất dữ liệu form nhập liệu
- **Vị trí tệp**: 
  - `RentalSystem/Views/Account/Register.cshtml`
  - `RentalSystem/Views/Account/Login.cshtml`
  - `RentalSystem/Views/Cart/Checkout.cshtml`
  - `RentalSystem/Views/BaoTri/TaoPhieu.cshtml`
  - `RentalSystem/Areas/Admin/Views/KhuyenMai/Create.cshtml`
  - `RentalSystem/Areas/Admin/Views/HopDong/Create.cshtml`
  - `RentalSystem/Areas/Admin/Views/PhanCong/Create.cshtml`
- **Hiện tượng & Bằng chứng kiểm toán**:
  - Rà soát toàn bộ 65 tệp Razor View trong dự án cho thấy chỉ có duy nhất 4 tệp view chứa đoạn mã `@section Scripts { <partial name="_ValidationScriptsPartial" /> }` (gồm: `ThietBi/Create`, `ThietBi/Edit`, `SanPham/Create`, `SanPham/Edit`).
  - Toàn bộ các trang biểu mẫu quan trọng còn lại hoàn toàn không tải thư viện `jquery.validate.min.js` và `jquery.validate.unobtrusive.min.js`.
  - Hậu quả: Khi người dùng nhập sai quy cách email, số điện thoại hoặc để trống trường bắt buộc, form không thể hiển thị cảnh báo ngay tại client mà phải thực hiện gửi toàn bộ HTTP POST lên máy chủ. Nếu model không hợp lệ, máy chủ trả về view kèm `ModelState` lỗi, dẫn đến hiện tượng chớp nháy reload trang và trong nhiều trường hợp làm mất trắng các trường dữ liệu mật khẩu hoặc tệp đính kèm người dùng đã chọn.
- **Mức độ nghiêm trọng**: **Major**. Vi phạm nguyên tắc bảo toàn trạng thái nhập liệu người dùng và tạo trải nghiệm người dùng kém chuyên nghiệp.
- **Giải pháp khắc phục đề xuất**:
  - Bổ sung `@section Scripts { <partial name="_ValidationScriptsPartial" /> }` vào chân trang của tất cả các form nhập liệu có sử dụng DataAnnotations.

---

#### 3.1.4. DEF-12: Trùng lặp class CSS, xung đột thuộc tính màu sắc & xung đột chuỗi tiện ích (`bg-white` vs `admin-card`)
- **Vị trí tệp và dòng mã**:
  - `RentalSystem/Views/Cart/Checkout.cshtml` dòng 15.
  - `RentalSystem/Views/Cart/SignContract.cshtml` dòng 19 và dòng 99.
  - `RentalSystem/Areas/Admin/Views/PhanCong/Create.cshtml` dòng 14, 88 và dòng 97.
  - `RentalSystem/Areas/Admin/Views/PhanCong/Edit.cshtml` dòng 125.
  - `RentalSystem/Areas/Admin/Views/PhanCong/MyTasks.cshtml` dòng 255.
- **Trích xuất mã nguồn thực tế**:
  ```html
  <!-- Views/Cart/Checkout.cshtml:15: Xung đột màu sắc & lặp class -->
  <div class="card-header text-warning fw-bold text-dark fw-bold py-3">

  <!-- Views/Cart/SignContract.cshtml:19 & 99: Lặp class màu và độ đậm -->
  <div class="card-header text-warning fw-bold text-dark fw-bold">
  <div class="card-header text-success fw-bold fw-bold">

  <!-- Areas/Admin/Views/PhanCong/Create.cshtml:14 vs 97: Xung đột kiến trúc CSS -->
  <!-- Dòng 14 (Khung bên trái dùng semantic class chuẩn): -->
  <div class="admin-card">
  ...
  <!-- Dòng 97 (Khung bên phải dùng chuỗi utility Bootstrap dài có bg-white): -->
  <div class="card border-0 shadow-sm rounded-3 bg-white">
  ```
- **Hiện tượng & Bằng chứng kiểm toán**:
  - *Về xung đột màu sắc*: Tại dòng 15 của `Checkout.cshtml` và dòng 19 của `SignContract.cshtml`, thẻ `div` được khai báo đồng thời cả hai class màu chữ mâu thuẫn trực tiếp: `text-warning` (màu vàng cảnh báo) và `text-dark` (màu tối), đồng thời thuộc tính `fw-bold` bị viết lặp 2 lần liên tiếp. Tại dòng 99 của `SignContract.cshtml`, class `fw-bold` cũng bị lặp 2 lần.
  - *Về xung đột chuỗi tiện ích (`bg-white` vs `admin-card`)*: Trong cùng một trang giao diện quản trị (`PhanCong/Create.cshtml`), cột bên trái tuân thủ chuẩn semantic đóng gói `<div class="admin-card">` (đã có sẵn `background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; box-shadow: ...` trong `classic-navy.css`), nhưng cột hướng dẫn bên phải (dòng 88 và 97) lại gọi trực tiếp chuỗi class Bootstrap dài: `<div class="card border-0 shadow-sm rounded-3 bg-white">`.
  - Sự pha trộn giữa chuỗi utility class cũ (`card border-0 shadow-sm rounded-3 bg-white`) và semantic class mới (`admin-card`) phá vỡ tính đóng gói CSS, tạo ra độ bóng (box-shadow) và bo góc (border-radius) không đồng nhất giữa hai cột của cùng một màn hình (cột trái bo 8px theo `.admin-card`, cột phải bo `rounded-3` 16px của Bootstrap).
- **Mức độ nghiêm trọng**: **Minor**. Lỗi cú pháp HTML/CSS và bất đồng nhất kiến trúc giao diện.
- **Giải pháp khắc phục đề xuất**:
  - Dọn dẹp các class trùng lặp trong `Checkout.cshtml` và `SignContract.cshtml`: `<div class="admin-card-header">`.
  - Chuẩn hóa toàn bộ các khối `<div class="card border-0 shadow-sm rounded-3 bg-white">` tại `PhanCong/Create.cshtml` và các view phụ về chuẩn `<div class="admin-card">`.

---

### 3.2. Nhóm 2: Sai lệch trạng thái hiển thị & Vi phạm chuẩn giao diện Doanh nghiệp (Classic Navy & Pure White)

Theo quy định bắt buộc trong `GEMINI.md` và `.agents/rules/ui-design-system.md`:
1. Bảng màu chủ đạo: Deep Navy `#0f2b5c`, Royal Blue `#1e3a8a`, Off-white canvas `#f8fafc`, Pure White surface `#ffffff`, Slate border `#e2e8f0`.
2. Tuyệt đối cấm sử dụng màu neon chói lọi (xanh lá chói, vàng chói, cyan rải rác).
3. Tối ưu hóa CSS ngữ nghĩa (Semantic Classes), không lặp lại chuỗi utility class dài lê thê của Bootstrap (như `card border-0 shadow-sm rounded-3 border-start...`).

#### 3.2.1. DEF-10: Chuỗi tiện ích Bootstrap dài và màu Neon tại `CongNo/Index.cshtml`
- **Vị trí tệp và dòng mã**: `RentalSystem/Areas/Admin/Views/CongNo/Index.cshtml` dòng 43, dòng 59, dòng 75, dòng 212-213 và dòng 226.
- **Trích xuất mã nguồn thực tế**:
  ```html
  <!-- Dòng 43: Thẻ KPI Tổng công nợ -->
  <div class="card border-0 shadow-sm rounded-3 border-start border-primary border-4 h-100 kpi-card">
      <div class="card-body">
          <div class="rounded-circle bg-primary bg-opacity-10 p-2 text-primary">
              <i class="fas fa-wallet fa-lg"></i>
          </div>
  ...
  <!-- Dòng 59: Thẻ KPI Tổng nợ quá hạn -->
  <div class="card border-0 shadow-sm rounded-3 border-start border-danger border-4 h-100 kpi-card">
  ...
  <!-- Dòng 75: Thẻ KPI Tỷ lệ thu hồi -->
  <div class="card border-0 shadow-sm rounded-3 border-start border-success border-4 h-100 kpi-card">
  ...
  <!-- Dòng 212-213: Nút thao tác -->
  <button type="button" class="btn btn-sm btn-outline-danger" onclick="guiNhacNo(@k.MaKyHan, this)">Nhắc nợ</button>
  <a href="/Admin/HopDong/Details/@hd.MaHopDong" class="btn btn-sm btn-outline-dark">Chi tiết</a>
  ...
  <!-- Dòng 226: Bảng tổng hợp hợp đồng -->
  <table class="table table-hover align-middle mb-0 text-center">
  ```
- **Hiện tượng & Bằng chứng kiểm toán**:
  - Trang quản lý công nợ chưa được chuyển đổi sang chuẩn `classic-navy.css`. Các thẻ KPI dùng viền dày 4px với màu sắc phân tán (`border-primary`, `border-danger`, `border-success`).
  - Bảng tổng hợp công nợ không sử dụng khung `.admin-card` và class bảng `.admin-table`.
  - Bộ nút hành động không sử dụng bộ nút Monochrome Slate `.action-btn` mà dùng các nút viền màu Bootstrap phân mảnh.
- **Mức độ nghiêm trọng**: **Major**. Vi phạm trực tiếp UI Design System bắt buộc của hệ thống.
- **Giải pháp khắc phục đề xuất**:
  - Chuyển đổi toàn bộ các khối card KPI sang cấu trúc `.stat-card` với `.stat-icon`, `.stat-label`, `.stat-value`.
  - Thay thế bảng thành `<div class="admin-card"><table class="admin-table">...</table></div>`.
  - Đưa nút bấm về class `.action-btn` và `.btn-navy`.

---

#### 3.2.2. DEF-11: Vi phạm thẻ KPI và màu sắc trạng thái tại `Database/Index.cshtml`
- **Vị trí tệp và dòng mã**: `RentalSystem/Areas/Admin/Views/Database/Index.cshtml` dòng 41, dòng 57, dòng 73 và dòng 89.
- **Trích xuất mã nguồn thực tế**:
  ```html
  <!-- Dòng 41: Thẻ Máy chủ SQL -->
  <div class="card shadow-sm border-0 h-100 border-start border-primary border-4">
  ...
  <!-- Dòng 57: Thẻ Cơ sở dữ liệu -->
  <div class="card shadow-sm border-0 h-100 border-start border-info border-4">
  ...
  <!-- Dòng 73: Thẻ Trạng thái kết nối -->
  <div class="card shadow-sm border-0 h-100 border-start @(Model.IsConnected ? "border-success" : "border-danger") border-4">
  ```
- **Hiện tượng & Bằng chứng kiểm toán**:
  - Các thẻ thông số máy chủ database vẫn duy trì phong cách dashboard Bootstrap cũ với viền dày lòe loẹt (`border-info`, `border-primary`, `border-success`), chưa đồng bộ với bảng màu Deep Navy thanh lịch.
- **Mức độ nghiêm trọng**: **Major**. Vi phạm tính đồng nhất của toàn bộ phân hệ quản trị Admin.
- **Giải pháp khắc phục đề xuất**:
  - Chuẩn hóa về semantic class `.stat-card` đã đóng gói trong `classic-navy.css`.

---

#### 3.2.3. DEF-14: Sử dụng nút bấm ngoài quy chuẩn tại trang chủ và giỏ hàng
- **Vị trí tệp và dòng mã**:
  - `RentalSystem/Views/Home/Index.cshtml` dòng 19, 28, 37: `class="btn btn-dark btn-lg fw-bold px-5 rounded-pill shadow"`.
  - `RentalSystem/Views/Cart/Checkout.cshtml` dòng 44: `class="btn btn-outline-primary"`.
- **Hiện tượng**:
  - Sử dụng nút bấm bo tròn quả trứng tròn xoe (`rounded-pill`) màu đen tuyền trên trang chủ, tạo sự lệch tông nghiêm trọng so với phong cách vuông vắn, trang nhã của bộ nhận diện doanh nghiệp (Classic Navy & Pure White).
- **Mức độ nghiêm trọng**: **Minor**. Khiếm khuyết thẩm mỹ giao diện.
- **Giải pháp khắc phục đề xuất**:
  - Đổi thành `.btn-navy` và `.btn-outline-navy`.

---

### 3.3. Nhóm 3: Bất đối xứng nghiêm trọng luồng nghiệp vụ Web vs Mobile (Parity Breaks)

#### 3.3.1. DEF-01: Lỗi logic nghiệp vụ nghiêm trọng trong API gia hạn `POST /api/contracts/{id}/renew`
- **Vị trí tệp và dòng mã**: `RentalSystem/Controllers/ApiContractsController.cs` dòng 278-298.
- **Trích xuất mã nguồn thực tế xử lý trên Mobile API**:
  ```csharp
  // RentalSystem/Controllers/ApiContractsController.cs:278-298
  [Authorize(Roles = "KhachHang")]
  [HttpPost("{id}/renew")]
  public async Task<IActionResult> RenewContract(int id, [FromBody] RenewContractApiRequest request)
  {
      int customerId = User.UserId();
      var hopDong = await _context.HopDongs.FirstOrDefaultAsync(h =>
          h.MaHopDong == id && h.MaKhachHang == customerId);
      if (hopDong == null)
      {
          return NotFound(new { message = $"Không tìm thấy hợp đồng #{id}" });
      }

      string renewalNote = $"[Yêu cầu gia hạn {DateTime.Now:dd/MM/yyyy HH:mm}]: Thời gian '{request?.Duration}', ghi chú: '{request?.Notes}'";
      hopDong.GhiChu = string.IsNullOrEmpty(hopDong.GhiChu) ? renewalNote : $"{hopDong.GhiChu}\n{renewalNote}";

      await _context.SaveChangesAsync();
      return Ok(new
      {
          success = true,
          message = "Yêu cầu gia hạn hợp đồng đã được gửi thành công (Chờ xử lý).",
          contractId = id.ToString()
      });
  }
  ```
- **So sánh đối chiếu với quy trình chuẩn trên Web (`CartController.cs` dòng 831-846)**:
  ```csharp
  // RentalSystem/Controllers/CartController.cs:831-846 (Quy trình chuẩn)
  var yc = new YeuCauGiaHan
  {
      MaHopDong = id,
      SoNgayGiaHan = soNgayGiaHan,
      LyDo = lyDo?.Trim(),
      NgayYeuCau = DateTime.Now,
      TrangThai = 0 // 0: Chờ duyệt
  };
  _context.YeuCauGiaHans.Add(yc);

  // Đồng bộ các cờ trên HopDong
  hd.YeuCauGiaHan = true;
  hd.SoNgayGiaHan = soNgayGiaHan;
  hd.TrangThaiGiaHan = 0; // 0: Chờ duyệt
  hd.LyDoGiaHan = lyDo?.Trim();
  await _context.SaveChangesAsync();
  ```
- **Hiện tượng & Hậu quả thực tế**:
  - Khi khách hàng thao tác xin gia hạn hợp đồng trên Mobile App (qua màn hình `RenewalRequestScreen` và datasource `RemoteRenewalDataSource`), ứng dụng gọi API `POST /api/contracts/{id}/renew`.
  - Action này **CHỈ NỐI MỘT CHUỖI VĂN BẢN VÀO CỘT `HopDong.GhiChu`** rồi trả về HTTP 200 thành công!
  - Nó **KHÔNG HỀ TẠO BẢN GHI TRONG BẢNG `YeuCauGiaHans`** và **KHÔNG HỀ BẬT CỜ `HopDong.YeuCauGiaHan = true`**.
  - Trong khi đó, màn hình quản trị Web của Quản trị viên/Kinh doanh (`/Admin/HopDong/YeuCauGiaHan` hoặc `/Admin/HopDong/Details`) quét danh sách chờ duyệt bằng câu truy vấn `_context.YeuCauGiaHans.Where(y => y.TrangThai == 0)` hoặc kiểm tra `hd.YeuCauGiaHan == true`.
  - Vì vậy, yêu cầu gia hạn gửi từ điện thoại **HOÀN TOÀN TÀNG HÌNH (BIẾN MẤT)** khỏi luồng làm việc của nhân viên! Khách hàng cứ ngỡ đã gửi thành công trong khi nhân viên quản trị không hề nhận được bất kỳ tín hiệu hay thông báo nào để phê duyệt.
- **Mức độ nghiêm trọng**: **Critical**. Đứt gãy luồng quy trình nghiệp vụ cốt lõi Quy trình 6 (Bảng 2.9 và Use Case UC-09 trong `CNTT_KLCN058.docx`).
- **Giải pháp khắc phục đề xuất**:
  - Tái cấu trúc action `RenewContract` trong `ApiContractsController.cs`: phân tích tham số số ngày gia hạn (`request.Duration`), kiểm tra tính khả dụng của thiết bị không bị trùng lịch, tạo bản ghi `YeuCauGiaHan` và cập nhật các cờ `hopDong.YeuCauGiaHan = true`, `hopDong.SoNgayGiaHan = days`, `hopDong.TrangThaiGiaHan = 0`.

---

#### 3.3.2. DEF-05: Khiếm khuyết chức năng Ký số điện tử (Canvas) và Tải CCCD trên Mobile
- **Vị trí tệp và dòng mã**: `MobileApp/lib/screens/requests/rental_confirm_screen.dart` dòng 54-58.
- **Trích xuất mã nguồn thực tế**:
  ```dart
  // MobileApp/lib/screens/requests/rental_confirm_screen.dart:54-58
  Text(
    '$contractCode · Chờ duyệt\nTổng tiền: ${_money(createdRental.estimatedAmount)}\nBạn có thể ký hợp đồng trên Web.',
    style: AppTextStyles.bodySecondary, 
    textAlign: TextAlign.center,
  ),
  ```
- **Hiện tượng & Bằng chứng kiểm toán**:
  - Trên Web (`Views/Cart/SignContract.cshtml`), khách hàng có đầy đủ màn hình tương tác với HTML5 Canvas để vẽ chữ ký điện tử, tải lên ảnh Căn cước công dân 2 mặt (`AnhCCCD_Truoc`, `AnhCCCD_Sau`), và chọn số kỳ hạn thanh toán (1, 2, 3, 4, 6 kỳ).
  - Ngược lại, trên Mobile App, sau khi bấm gửi đơn thuê tại `RentalConfirmScreen`, ứng dụng chỉ hiện hộp thoại dialog với dòng chữ thừa nhận: *"Bạn có thể ký hợp đồng trên Web."*.
  - Ứng dụng di động hoàn toàn không có canvas vẽ chữ ký, không có tính năng đính kèm ảnh CCCD và không cho phép chọn số kỳ thanh toán.
  - Do quy định nghiêm ngặt tại Backend (`HopDongController.UpdateStatus` dòng 639-651 kiểm tra: bắt buộc phải có chữ ký khách hàng và ảnh CCCD mới được phép xuất kho bàn giao máy), khách hàng dùng Mobile bắt buộc phải mở trình duyệt máy tính lên Web để ký, làm mất đi tính độc lập tiện lợi của ứng dụng di động.
- **Mức độ nghiêm trọng**: **Major**. Khiếm khuyết lớn về độ hoàn thiện nghiệp vụ di động.
- **Giải pháp khắc phục đề xuất**:
  - Bổ sung thư viện `signature` vào Flutter, xây dựng màn hình `ContractSignatureScreen` cho phép khách vẽ chữ ký ngón tay, chụp/tải ảnh CCCD qua `image_picker` và gửi qua endpoint API chuyên biệt.

---

#### 3.3.3. DEF-06: Khiếm khuyết chức năng Sổ công nợ và chức năng quét VietQR trên Mobile
- **Vị trí tệp**: `MobileApp/lib/screens/contracts/` và các datasource liên quan.
- **Hiện tượng & Bằng chứng kiểm toán**:
  - Trên Web, trang `/Account/MyDebt` là trung tâm tài chính của khách hàng, cho phép:
    1. Theo dõi tổng nợ, nợ trong hạn, nợ quá hạn và phí phạt trễ hạn.
    2. Xem chi tiết từng kỳ hạn trong bảng phân kỳ.
    3. Mở mã VietQR động được tạo tự động chứa chính xác số tiền kỳ nợ và cú pháp chuẩn `HD<MaHopDong>`.
    4. Tải ảnh biên lai giao dịch chuyển khoản ngân hàng lên để nhân viên đối soát gạch nợ (`UploadMinhChungThanhToan`).
  - Trên Mobile App, hoàn toàn **KHÔNG TỒN TẠI** màn hình Sổ công nợ. Người dùng di động không có cách nào biết được kỳ thanh toán tiếp theo đến hạn vào ngày nào, không có mã VietQR để quét và không có form nộp minh chứng chuyển tiền.
- **Mức độ nghiêm trọng**: **Major**. Vi phạm tính đối xứng nghiệp vụ giữa hai nền tảng (Quy trình 3 và Quy trình 7 trong `CNTT_KLCN058.docx`).
- **Giải pháp khắc phục đề xuất**:
  - Xây dựng màn hình `CustomerDebtScreen` trên Flutter, tích hợp widget hiển thị mã VietQR từ API `https://img.vietqr.io/image/...` và form gửi biên lai.

---

#### 3.3.4. DEF-07: Giỏ hàng đơn máy trên Mobile vs Giỏ hàng đa máy trên Web
- **Vị trí tệp**: `MobileApp/lib/screens/requests/rental_form_screen.dart`.
- **Hiện tượng**:
  - Trên Web, khách hàng có thể duyệt danh mục, thêm nhiều sản phẩm khác nhau (ví dụ: 2 Laptop Dell, 1 Máy in HP, 1 Màn hình Dell) vào giỏ hàng session `/Cart`, sau đó chuyển sang thanh toán gộp một lần.
  - Trên Mobile, luồng đặt thuê được gắn chặt 1-1 với chi tiết thiết bị (`RentalFormScreen(device: device)`). Khách hàng chỉ có thể thuê duy nhất một dòng thiết bị trong một lần đặt, không có khái niệm giỏ hàng lưu tạm. Nếu muốn thuê 3 thiết bị khác nhau, khách phải tạo 3 hợp đồng rời rạc.
- **Mức độ nghiêm trọng**: **Major**. Bất đối xứng trải nghiệm mua sắm.

---

#### 3.3.5. DEF-08: Gộp chung vai trò Kinh doanh và Kỹ thuật (`Role.staff`) trên Mobile
- **Vị trí tệp và dòng mã**: `MobileApp/lib/models/role_enum.dart` dòng 22-24.
- **Trích xuất mã nguồn thực tế**:
  ```dart
  // MobileApp/lib/models/role_enum.dart:22-24
  if (r == 'nhân viên' || r == 'nhanvien' || r == 'staff' || r == 'kinhdoanh' || r == 'kythuat') {
    return Role.staff;
  }
  ```
- **Hiện tượng**:
  - Hệ thống cơ sở dữ liệu và Web phân định 4 vai trò độc lập với mã định danh rõ ràng: `Admin` (1), `KhachHang` (2), `KyThuat` (3), `KinhDoanh` (4).
  - Phân hệ Mobile lại thu hẹp chỉ còn 3 enum: `customer`, `staff`, `admin`. Cả nhân viên kinh doanh lẫn kỹ thuật viên khi đăng nhập đều được gán chung là `Role.staff`.
  - Hậu quả: Thanh điều hướng di động của cả hai vai trò đều hiển thị giống hệt nhau gồm 5 tab (Trang chủ, Công việc, Bảo trì, Thông báo, Tài khoản). Nhân viên kinh doanh nhìn thấy cả danh sách phân công sửa chữa phần cứng, trong khi kỹ thuật viên lại nhìn thấy các tác vụ hợp đồng kinh doanh.
- **Mức độ nghiêm trọng**: **Major**. Vi phạm nguyên tắc phân quyền đặc tả trong Chương 2 (`CNTT_KLCN058.docx`).

---

#### 3.3.6. DEF-09: Bất đồng bộ dòng thời gian tiến trình hợp đồng (Timeline Mismatch)
- **Vị trí tệp**: `MobileApp/lib/screens/requests/rental_detail_screen.dart` và `rental_status.dart`.
- **Hiện tượng**:
  - Mô hình thực thể CSDL backend (`HopDong.cs`) định nghĩa 5 trạng thái vòng đời hợp đồng:
    - `0`: Chờ duyệt (Chờ ký / Chờ cọc)
    - `1`: Đang hiệu lực (Đang thuê)
    - `2`: Hoàn tất (Đã trả máy, đã quyết toán)
    - `3`: Đã hủy
    - `4`: Đã trả máy (Chờ quyết toán cọc)
  - Trên màn hình chi tiết hợp đồng của Mobile (`RentalDetailScreen`), giao diện lại hiển thị một Timeline 7 bước giả lập:
    `Chờ xác nhận -> Đã xác nhận -> Đang chuẩn bị -> Đang giao -> Đã lắp đặt -> Đang thuê -> Hoàn thành`.
  - Các bước "Đang chuẩn bị", "Đang giao", "Đã lắp đặt" hoàn toàn không có thực thể tương ứng trong CSDL mà chỉ là các trạng thái nội suy cục bộ trên client dựa vào thời gian, gây lệch pha thông tin khi đối chiếu với hệ thống Web quản trị.
- **Mức độ nghiêm trọng**: **Minor**. Gây bối rối cho khách hàng khi trạng thái trên web báo "Đang hiệu lực" nhưng điện thoại lại hiển thị các bước giao vận không có thật.

---

### 3.4. Nhóm 4: Lỗi biên dịch bộ kiểm thử tự động `ChallengerTests`

#### 3.4.1. DEF-02: Lỗi CS0117 thiếu `DebtCalculationHelper.GetAgingBadgeClass`
- **Vị trí tệp và dòng mã**:
  - `ChallengerTests/Program.cs` dòng 1971-1975.
  - `RentalSystem/Common/DebtCalculationHelper.cs` dòng 48-56.
- **Bằng chứng thông báo lỗi biên dịch thực tế**:
  ```
  D:\DoAnCuNhan\ChallengerTests\Program.cs(1971,42): error CS0117: 'DebtCalculationHelper' does not contain a definition for 'GetAgingBadgeClass'
  D:\DoAnCuNhan\ChallengerTests\Program.cs(1972,42): error CS0117: 'DebtCalculationHelper' does not contain a definition for 'GetAgingBadgeClass'
  D:\DoAnCuNhan\ChallengerTests\Program.cs(1973,42): error CS0117: 'DebtCalculationHelper' does not contain a definition for 'GetAgingBadgeClass'
  D:\DoAnCuNhan\ChallengerTests\Program.cs(1974,42): error CS0117: 'DebtCalculationHelper' does not contain a definition for 'GetAgingBadgeClass'
  D:\DoAnCuNhan\ChallengerTests\Program.cs(1975,42): error CS0117: 'DebtCalculationHelper' does not contain a definition for 'GetAgingBadgeClass'
  ```
- **Trích xuất mã nguồn kiểm thử tại `ChallengerTests/Program.cs:1964-1975`**:
  ```csharp
  // Kiểm tra tên nhóm tuổi nợ
  Assert(DebtCalculationHelper.GetAgingTierName(0) == "Đúng hạn", "M4-01.16: GetAgingTierName(0) returns 'Đúng hạn'");
  Assert(DebtCalculationHelper.GetAgingTierName(1) == "Nhóm 1 (Cần chú ý)", "M4-01.17: GetAgingTierName(1) returns 'Nhóm 1 (Cần chú ý)'");
  Assert(DebtCalculationHelper.GetAgingTierName(2) == "Nhóm 2 (Dưới tiêu chuẩn)", "M4-01.18: GetAgingTierName(2) returns 'Nhóm 2 (Dưới tiêu chuẩn)'");
  Assert(DebtCalculationHelper.GetAgingTierName(3) == "Nhóm 3 (Nghi ngờ)", "M4-01.19: GetAgingTierName(3) returns 'Nhóm 3 (Nghi ngờ)'");
  Assert(DebtCalculationHelper.GetAgingTierName(4) == "Nhóm 4 (Nợ xấu / Khóa thuê)", "M4-01.20: GetAgingTierName(4) returns 'Nhóm 4 (Nợ xấu / Khóa thuê)'");
  Assert(DebtCalculationHelper.GetAgingTierName(99) == "Không xác định", "M4-01.21: GetAgingTierName(99) returns 'Không xác định' for invalid tier");

  // Kiểm tra class badge CSS tương ứng
  Assert(DebtCalculationHelper.GetAgingBadgeClass(0) == "badge bg-success", "M4-01.22: GetAgingBadgeClass(0) returns 'badge bg-success'");
  Assert(DebtCalculationHelper.GetAgingBadgeClass(1) == "badge bg-info text-dark", "M4-01.23: GetAgingBadgeClass(1) returns 'badge bg-info text-dark'");
  Assert(DebtCalculationHelper.GetAgingBadgeClass(2) == "badge bg-warning text-dark", "M4-01.24: GetAgingBadgeClass(2) returns 'badge bg-warning text-dark'");
  Assert(DebtCalculationHelper.GetAgingBadgeClass(3) == "badge bg-orange text-white", "M4-01.25: GetAgingBadgeClass(3) returns 'badge bg-orange text-white'");
  Assert(DebtCalculationHelper.GetAgingBadgeClass(4) == "badge bg-danger", "M4-01.26: GetAgingBadgeClass(4) returns 'badge bg-danger'");
  ```
- **So sánh đối chiếu với mã nguồn thực tế tại `DebtCalculationHelper.cs:48-56`**:
  ```csharp
  // Mã nguồn hiện tại trong RentalSystem/Common/DebtCalculationHelper.cs
  public static string GetAgingTierName(int tier) => tier switch
  {
      0 => "Chưa quá hạn",
      1 => "1–30 ngày",
      2 => "31–60 ngày",
      3 => "61–90 ngày",
      4 => "Trên 90 ngày",
      _ => "Chưa xác định"
  };
  // HOÀN TOÀN THIẾU PHƯƠNG THỨC GetAgingBadgeClass!
  ```
- **Hiện tượng & Hậu quả**:
  - Trong quá trình tái cấu trúc các tệp dùng chung, phương thức `GetAgingBadgeClass` đã bị xóa nhầm khỏi `DebtCalculationHelper.cs`.
  - Đồng thời, chuỗi nhãn hiển thị trong `GetAgingTierName` đã bị sửa đổi thành dạng số ngày ("Chưa quá hạn", "1–30 ngày"...), lệch hoàn toàn với chuỗi định danh phân loại nợ tiêu chuẩn ngành ngân hàng ("Đúng hạn", "Nhóm 1 (Cần chú ý)", "Nhóm 2 (Dưới tiêu chuẩn)", "Nhóm 3 (Nghi ngờ)", "Nhóm 4 (Nợ xấu / Khóa thuê)", "Không xác định") mà bộ kiểm thử `ChallengerTests` bắt buộc kiểm tra.
  - Hậu quả trực tiếp: Lệnh `dotnet build ChallengerTests/ChallengerTests.csproj` bị gãy (Failed) với 5 lỗi CS0117, làm tê liệt toàn bộ quy trình kiểm thử hồi quy tự động.
- **Mức độ nghiêm trọng**: **Blocker**. Vi phạm tiêu chí bảo tồn kiểm thử tự động của dự án.
- **Giải pháp khắc phục đề xuất**:
  - Bổ sung phương thức `GetAgingBadgeClass` và đồng bộ lại chuỗi trả về của `GetAgingTierName` trong `DebtCalculationHelper.cs`.

---

## PHẦN IV: MA TRẬN KỊCH BẢN MÔ PHỎNG TƯƠNG TÁC THỰC TẾ TỪNG MÀN HÌNH

### 4.1. Ma trận mô phỏng 4 vai trò trên phân hệ Web

#### Vai trò 1: Quản trị viên (Admin - `admin@rentalsystem.com`)

| STT | Màn hình Mô phỏng | Đường dẫn (URL) | Thao tác Tương tác Chi tiết | Kết quả Mong đợi | Bất cập / Lỗi Phát hiện Được |
|:---:|:---|:---|:---|:---|:---|
| 1 | Bảng điều khiển (Dashboard) | `/Admin/Dashboard` | Đăng nhập tài khoản Admin, xem tổng quan chỉ số doanh thu, hợp đồng đang chạy, tồn kho thiết bị và cảnh báo nợ. | Hiển thị đầy đủ các thẻ KPI chuẩn Classic Navy, biểu đồ thống kê trực quan. | Bình thường. Không có lỗi. |
| 2 | Danh sách Hợp đồng | `/Admin/HopDong` | Lọc hợp đồng theo trạng thái Chờ duyệt (0), Đang hiệu lực (1), Hoàn thành (2). Mở xem chi tiết hợp đồng bất kỳ. | Danh sách hiển thị đúng mã, tên khách, ngày thuê, trạng thái thanh toán và các nút thao tác. | Bình thường. |
| 3 | Chi tiết Hợp đồng & Bàn giao | `/Admin/HopDong/Details/{id}` | Kiểm tra chữ ký khách, chữ ký nhân viên và tiền thanh toán đợt đầu. Bấm nút Bàn giao máy (chuyển sang `DangHieuLuc`). | Máy chủ kiểm tra 3 điều kiện tiên quyết. Nếu đủ, sinh biên bản bàn giao và đưa máy sang Đang thuê. | Nếu thiếu cọc hoặc thiếu chữ ký, hệ thống chặn đúng nghiệp vụ. |
| 4 | Thu hồi & Quyết toán hoàn cọc | `/Admin/HopDong/Details/{id}` $\rightarrow$ Settlement | Khi khách trả máy, bấm Thu hồi thiết bị. Mở bản xem trước quyết toán (`SettlementPreview`), kiểm tra cấn trừ nợ và chi hoàn cọc. | Thiết bị về kho sẵn sàng (0), hợp đồng sang Hoàn thành (2), sinh 1 phiếu chi duy nhất. Chặn hoàn lặp. | Đạt tuyệt đối tính toàn vẹn (Kiểm tra bởi `verify_contract_settlements.py`). |
| 5 | Quản lý Sự cố & Bảo trì | `/Admin/BaoTri` | Mở danh sách sự cố, chọn phiếu mới tiếp nhận (1), phân công kỹ thuật viên phụ trách, đặt hạn SLA (12h, 24h, 48h). | Phiếu tự động đồng bộ sang bảng `PhanCongCongViec`. Kỹ thuật viên được chỉ định nhận thông báo. | Hoạt động chính xác theo SLA. |
| 6 | Quản trị Công nợ Toàn hệ thống | `/Admin/CongNo` | Xem bảng tổng hợp công nợ 4 cấp tuổi nợ. Bấm nút "Nhắc nợ" từng kỳ quá hạn. | Gửi thông báo nhắc nợ vào `LichSuNhacNo`. | **DEF-10**: Giao diện dùng class utility dài, màu neon chói, bảng và nút chưa áp dụng chuẩn `.admin-card`, `.action-btn`. |
| 7 | Báo cáo Thống kê & Xuất Excel | `/Admin/ThongKe` | Chọn bộ lọc khoảng ngày (từ ngày... đến ngày...), xem cơ cấu doanh thu theo dòng máy, bấm "Xuất Excel". | Tải về tệp `BaoCao_ThongKe.xlsx` chuẩn ClosedXML, dữ liệu khớp từng ô với báo cáo trên màn hình. | Đạt chuẩn (Kiểm tra bởi `verify_operations_reports.py`). |
| 8 | Sao lưu & Phục hồi CSDL | `/Admin/Database` | Mở trang giám sát máy chủ SQL, kiểm tra trạng thái kết nối, bấm "Sao lưu JSON" để tải gói backup. | Tải về tệp sao lưu dữ liệu kèm đường dẫn chữ ký/ảnh hợp lệ. | **DEF-11**: Thẻ thông tin máy chủ dùng viền neon Bootstrap tiện ích chưa đồng bộ chuẩn `.stat-card`. |

---

#### Vai trò 2: Nhân viên Kinh doanh (Sales / CSKH - `sale.linh@rentalsystem.com`)

| STT | Màn hình Mô phỏng | Đường dẫn (URL) | Thao tác Tương tác Chi tiết | Kết quả Mong đợi | Bất cập / Lỗi Phát hiện Được |
|:---:|:---|:---|:---|:---|:---|
| 1 | Tiếp nhận Yêu cầu Thuê mới | `/Admin/HopDong?status=0` | Xem danh sách đơn thuê mới gửi từ Web và Mobile API. Mở đơn kiểm tra thông tin khách và địa chỉ giao. | Đơn hiển thị rõ thời gian thuê, tổng tiền, thiết bị giữ chỗ đang ở trạng thái Giữ chỗ (3). | Bình thường. |
| 2 | Ký số Đại diện Nhân viên | `/Admin/HopDong/SignContract/{id}` | Nhân viên kiểm tra hồ sơ, vẽ chữ ký số trên Canvas để lưu vào `ChuKyNhanVien`. | Chữ ký nhân viên được cập nhật, sẵn sàng cho bước bàn giao. | Bình thường. |
| 3 | Duyệt Yêu cầu Gia hạn Hợp đồng | `/Admin/HopDong/YeuCauGiaHan` | Xem danh sách yêu cầu xin gia hạn thêm ngày của khách hàng. Bấm "Phê duyệt gia hạn". | Máy chủ kiểm tra xung đột serial máy; nếu trống lịch, kéo dài `NgayKetThuc` và sinh kỳ nợ mới. | **DEF-01**: Yêu cầu gia hạn gửi từ Mobile **hoàn toàn không xuất hiện** ở màn hình này do API chỉ ghi chú vào `GhiChu`! |
| 4 | Theo dõi & Đôn đốc Công nợ | `/Admin/CongNo` | Lọc danh sách nợ Nhóm 1 (1-30 ngày) và Nhóm 2 (31-60 ngày). Bấm "Chi tiết" để xem hồ sơ liên hệ khách. | Hiển thị số điện thoại, lịch sử nhắc nợ để nhân viên gọi điện đôn đốc. | **DEF-10**: Nút bấm "Chi tiết" dùng `btn-outline-dark` thay vì `.action-btn`. |
| 5 | Quản lý Mã Giảm Giá | `/Admin/KhuyenMai` | Tạo mới voucher khuyến mãi (`MaCode`, `% giảm`, số lượng, thời hạn hiệu lực). | Voucher được lưu vào `KhuyenMais`, áp dụng giảm trừ trực tiếp khi khách checkout. | Trang `Create.cshtml` thiếu `_ValidationScriptsPartial` (**DEF-13**). |

---

#### Vai trò 3: Kỹ thuật viên (Technician - `kt.tuan@rentalsystem.com`)

| STT | Màn hình Mô phỏng | Đường dẫn (URL) | Thao tác Tương tác Chi tiết | Kết quả Mong đợi | Bất cập / Lỗi Phát hiện Được |
|:---:|:---|:---|:---|:---|:---|
| 1 | Danh sách Công việc Phân công | `/Admin/PhanCong` | Xem các nhiệm vụ bàn giao máy, thu hồi máy hoặc sửa chữa sự cố được giao cho cá nhân. | Hiển thị tiêu đề công việc, hạn hoàn thành SLA, liên kết tới hợp đồng hoặc phiếu bảo trì. | Bình thường. |
| 2 | Bàn giao & Lập Biên bản Xuất kho | `/Admin/HopDong/Details/{id}` $\rightarrow$ Biên bản | Đối chiếu số serial vật lý, kiểm tra ngoại quan máy và phụ kiện (sạc, chuột). Lập biên bản bàn giao (`LoaiBienBan = 0`). | Lưu ảnh minh chứng và ghi chú ngoại quan vào bảng `BienBanBanGiaos`. | Bình thường. |
| 3 | Xử lý Phiếu Bảo trì Sự cố | `/Admin/BaoTri/Details/{id}` | Mở phiếu sự cố được giao. Chuyển trạng thái sang "2 - Đang sửa chữa", ghi chú kỹ thuật. Sau khi sửa xong, chuyển sang "3 - Chờ nghiệm thu". | Cập nhật tiến độ tức thì, ghi nhận linh kiện thay thế, gửi thông báo để khách hàng nghiệm thu. | Hoạt động xuất sắc, logic SLA chặt chẽ. |
| 4 | Thu hồi Máy & Nghiệm thu Trả máy | `/Admin/HopDong/Details/{id}` $\rightarrow$ Thu hồi | Khi khách trả máy, kỹ thuật viên kiểm tra trầy xước, thiếu hụt phụ kiện. Lập biên bản thu hồi (`LoaiBienBan = 1`). | Thiết bị chuyển về kho sẵn sàng (0), hợp đồng chuyển sang Chờ quyết toán (4). | Lưu vết nhật ký `LichSuThietBis` đầy đủ. |

---

#### Vai trò 4: Khách hàng (Customer - `khach@gmail.com`)

| STT | Màn hình Mô phỏng | Đường dẫn (URL) | Thao tác Tương tác Chi tiết | Kết quả Mong đợi | Bất cập / Lỗi Phát hiện Được |
|:---:|:---|:---|:---|:---|:---|
| 1 | Đăng ký & Đăng nhập | `/Account/Register` & `/Account/Login` | Nhập họ tên, email, SĐT, CCCD, mật khẩu. Bấm đăng ký. | Cấp Cookie phiên làm việc, chuyển hướng trang chủ. | **DEF-13**: Thiếu script validation client, gõ sai format phải chờ server reload. |
| 2 | Duyệt Thiết bị & Thêm Giỏ hàng | `/Home/Index` & `/Cart` | Xem danh mục sản phẩm, cấu hình máy, thêm 2 sản phẩm khác nhau vào giỏ hàng với số lượng tùy ý. | Giỏ hàng lưu session, tính tổng tiền thuê và tiền cọc gộp chính xác. | **DEF-14**: Nút trên trang chủ dùng bo tròn `rounded-pill` lệch chuẩn Classic Navy. |
| 3 | Chốt Ngày & Đặt Thuê (Checkout) | `/Cart/Checkout` | Chọn ngày bắt đầu, ngày kết thúc, nhập địa chỉ nhận máy, áp dụng mã voucher giảm giá. Bấm "Xác nhận đặt thuê". | Máy chủ dùng `SemaphoreSlim` khóa giữ chỗ, tạo đơn `HopDong` trạng thái Chờ ký (0). | **DEF-12**: Thẻ header có class xung đột màu `text-warning` và `text-dark`. |
| 4 | Ký Hợp đồng & Tải CCCD | `/Cart/SignContract/{id}` | Xem điều khoản hợp đồng điện tử. Tải ảnh CCCD mặt trước/sau. Vẽ chữ ký trên khung Canvas tương tác. Bấm "Lưu chữ ký". | Lưu tệp ảnh chữ ký vào `ChuKyKhachHang`, cập nhật `NgayKy`. | **DEF-12**: Class `fw-bold` bị viết lặp 2 lần tại dòng 19 và 99. |
| 5 | Quét VietQR Thanh toán Đợt đầu | `/Cart/ContractDetail/{id}` | Xem khoản cần nộp đợt đầu (Tiền cọc + Tiền thuê kỳ 1). Quét mã VietQR động với cú pháp `HD<id> LD`. | Quét mã chuyển khoản ngân hàng chính xác. | **DEF-03**: Lộ STK cá nhân `0783406516` - PHAN MINH QUAN.<br>**DEF-04**: Dead link `#bankTransferInstructions`. |
| 6 | Sổ Công nợ & Quét VietQR Định kỳ | `/Account/MyDebt` | Xem danh sách các kỳ nợ đến hạn, mở mã VietQR động theo từng kỳ, tải ảnh biên lai nộp tiền đối soát. | Gửi biên lai thành công (`TrangThaiXacNhan = 1`). | **DEF-03**: Lộ STK cá nhân tại modal thanh toán (dòng 519). |
| 7 | Báo Sự cố & Đánh giá Sao | `/BaoTri/TaoPhieu` & `/BaoTri/NghiemThu` | Chọn thiết bị đang thuê bị hỏng, tải ảnh sự cố. Sau khi kỹ thuật sửa xong, bấm Nghiệm thu và chấm điểm 5 sao. | Ghi nhận nghiệm thu (`DaNghiemThu = 1`) và lưu điểm đánh giá độc lập. | Quy trình chuẩn xác 100%. |

---

### 4.2. Ma trận mô phỏng 3 vai trò trên phân hệ Mobile

#### Vai trò 1: Khách hàng (Customer - Mobile App)

| STT | Màn hình Di động | Lớp Màn hình (Screen Class) | Thao tác Tương tác Chi tiết | Kết quả Mong đợi | Bất cập / Lỗi Phát hiện Được |
|:---:|:---|:---|:---|:---|:---|
| 1 | Trang chủ & Danh mục | `HomeScreen`, `DevicesScreen` | Xem danh sách thiết bị có sẵn, lọc theo loại máy (Laptop, PC, Server), tìm kiếm theo tên hoặc cấu hình. | Hiển thị ảnh đại diện, giá thuê/ngày, tiền cọc và thông số kỹ thuật mượt mà. | Hoạt động tốt. |
| 2 | Chi tiết Máy & Đặt thuê | `DeviceDetailScreen` $\rightarrow$ `RentalFormScreen` | Chọn thời gian thuê (ngày bắt đầu, ngày kết thúc), nhập địa chỉ nhận máy. | Ứng dụng tính toán tổng tiền tạm tính chính xác. | **DEF-07**: Chỉ hỗ trợ thuê 1 máy đơn lẻ, không có giỏ hàng đa máy như trên Web. |
| 3 | Xác nhận Đơn thuê | `RentalConfirmScreen` | Xem lại tóm tắt đơn thuê, bấm "Xác nhận gửi yêu cầu thuê". | Gửi API `POST /api/contracts`, máy chủ tạo hợp đồng chờ duyệt thành công. | **DEF-05**: Hiện dialog thông báo: *"Bạn có thể ký hợp đồng trên Web."*. Thiếu tính năng ký Canvas và tải CCCD! |
| 4 | Danh sách Hợp đồng | `ContractsScreen` | Xem danh sách các hợp đồng của tôi theo các tab Chờ duyệt, Đang hiệu lực, Lịch sử thuê. | Danh sách tải từ API với đầy đủ mã hợp đồng, số tiền và trạng thái. | Hoạt động tốt. |
| 5 | Chi tiết Đơn & Xuất PDF | `RentalDetailScreen`, `ContractPdfViewerScreen` | Xem thông tin chi tiết hợp đồng, bấm nút "Xem bản in PDF", kết xuất PDF chuẩn A4 qua Syncfusion/Printing. | Hiển thị tài liệu hợp đồng định dạng PDF chuẩn mực với font Times New Roman nhúng. | **DEF-09**: Hiển thị Timeline 7 bước giả lập cục bộ không khớp với 5 trạng thái CSDL backend. |
| 6 | Yêu cầu Gia hạn Hợp đồng | `RenewalRequestScreen` | Tại hợp đồng đang hiệu lực, nhập số ngày muốn thuê thêm và lý do, bấm "Gửi yêu cầu gia hạn". | Ứng dụng gửi `POST /api/contracts/{id}/renew`, báo gửi thành công. | **DEF-01 (Critical)**: Backend chỉ nối chuỗi vào `GhiChu`, không tạo yêu cầu duyệt, làm yêu cầu bị "bốc hơi" khỏi Admin! |
| 7 | Báo sự cố & Nghiệm thu | `CreateIncidentScreen`, `IncidentDetailScreen` | Chụp ảnh lỗi thiết bị, gửi yêu cầu bảo trì. Theo dõi tiến độ kỹ thuật viên, bấm Nghiệm thu đạt và chấm 1-5 sao. | Gửi API bảo trì hoàn chỉnh, đồng bộ tiến độ thời gian thực với Web. | Phân hệ hoạt động xuất sắc, tương đương 100% với Web. |
| 8 | Sổ Công nợ & VietQR | *(Không có màn hình)* | Tìm kiếm màn hình xem lịch sử kỳ hạn nợ hoặc mã VietQR thanh toán tiền thuê. | *(Kỳ vọng có màn hình công nợ)* | **DEF-06**: Mobile hoàn toàn thiếu chức năng Sổ công nợ và quét mã VietQR. |

---

#### Vai trò 2: Nhân viên (Staff - Kỹ thuật & Kinh doanh gộp chung)

| STT | Màn hình Di động | Lớp Màn hình (Screen Class) | Thao tác Tương tác Chi tiết | Kết quả Mong đợi | Bất cập / Lỗi Phát hiện Được |
|:---:|:---|:---|:---|:---|:---|
| 1 | Bảng công việc Nhân viên | `TasksScreen` | Đăng nhập tài khoản `kt.tuan@rentalsystem.com` hoặc `sale.linh@rentalsystem.com`. Xem tab "Công việc". | Hiển thị danh sách các nhiệm vụ được phân công trong ngày. | **DEF-08**: Gộp chung `KinhDoanh` và `KyThuat` thành `Role.staff`, nhân viên kinh doanh cũng thấy danh sách sửa máy. |
| 2 | Danh sách Sự cố Bảo trì | `MaintenanceListScreen` | Kỹ thuật viên xem danh sách các sự cố cần xử lý, lọc theo mức độ khẩn cấp SLA (12h, 24h, 48h). | Hiển thị mã phiếu, thiết bị, hợp đồng liên quan và hạn hoàn thành SLA. | Hoạt động tốt. |
| 3 | Cập nhật Tiến độ Sửa chữa | `StaffIncidentDetailScreen` | Kỹ thuật viên đến hiện trường, cập nhật trạng thái "Đang sửa chữa", ghi nhận linh kiện thay thế, báo "Đã sửa xong". | Đồng bộ dữ liệu về backend, kích hoạt trạng thái sẵn sàng nghiệm thu cho khách hàng. | Hoạt động rất tốt và ổn định. |
| 4 | Thông báo Công việc | `NotificationsScreen` | Xem các thông báo phân công nhiệm vụ mới hoặc phản hồi từ khách hàng. | Danh sách thông báo được cập nhật thời gian thực. | Hoạt động bình thường. |

---

#### Vai trò 3: Quản lý (Admin - Mobile App)

| STT | Màn hình Di động | Lớp Màn hình (Screen Class) | Thao tác Tương tác Chi tiết | Kết quả Mong đợi | Bất cập / Lỗi Phát hiện Được |
|:---:|:---|:---|:---|:---|:---|
| 1 | Tổng quan Báo cáo Nhanh | `AdminDashboardScreen` | Đăng nhập `admin@rentalsystem.com`. Xem tóm tắt chỉ số thiết bị, hợp đồng và sự cố đang mở. | Thống kê số lượng theo thời gian thực từ API. | Hoạt động tốt. |
| 2 | Giám sát Sự cố Toàn hệ thống | `AdminIncidentsScreen` | Xem toàn bộ các phiếu sự cố chưa được phân công hoặc đang xử lý quá hạn SLA. | Hiển thị cảnh báo trực quan cho quản lý. | Hoạt động tốt. |

---

### 4.3. Kịch bản mô phỏng tích hợp liên nền tảng xuyên suốt vòng đời thuê máy

Kịch bản mô phỏng tích hợp thực tế (End-to-End Cross-Platform Simulation) chứng minh luồng dữ liệu luân chuyển liên tục và phát hiện các điểm gãy:

```
[BƯỚC 1: Mobile Khách hàng]
Khách duyệt Laptop Dell Latitude 5430 -> Thuê 7 ngày -> Gửi đơn thuê
  |
  +---> Backend tạo HopDong (TrangThai = 0), ThietBi chuyển sang Giữ chỗ (TrangThai = 3)
  |
  +---> [ĐIỂM GÃY DEF-05]: Mobile không có Canvas ký số, thông báo: "Bạn có thể ký trên Web."
  |
[BƯỚC 2: Web Khách hàng]
Khách bắt buộc phải mở Web (/Cart/SignContract) -> Vẽ chữ ký Canvas -> Tải ảnh CCCD 2 mặt
  |
  +---> Khách mở /Cart/ContractDetail để thanh toán cọc đợt đầu
  |
  +---> [ĐIỂM GÃY DEF-03 & DEF-04]: Lộ STK cá nhân 0783406516; Nút chuyển khoản dính Dead Link nếu chưa render VietQR
  |
  +---> Khách quét VietQR chuyển đủ 100% khoản đầu -> Backend sinh Phiếu thu cọc (LoaiPhieu = 1) & Phiếu thu thuê (LoaiPhieu = 0)
  |
[BƯỚC 3: Web Nhân viên Kinh doanh & Kỹ thuật]
Kinh doanh ký số đại diện -> Kỹ thuật viên đối chiếu serial vật lý, kiểm tra ngoại quan máy
  |
  +---> Lập biên bản bàn giao (LoaiBienBan = 0) -> Hợp đồng sang Đang hiệu lực (1), Thiết bị sang Đang thuê (1)
  |
[BƯỚC 4: Mobile Khách hàng & Kỹ thuật viên]
Trong quá trình sử dụng, máy hỏng Wi-Fi -> Khách dùng Mobile báo sự cố đính kèm ảnh chụp
  |
  +---> Admin phân công kỹ thuật viên -> Kỹ thuật nhận thông báo trên Mobile, đến sửa máy và báo hoàn tất
  |
  +---> Khách dùng Mobile nghiệm thu thành công và đánh giá 5 sao (Đồng bộ xuất sắc)
  |
[BƯỚC 5: Mobile Khách hàng xin gia hạn hợp đồng]
Khách dùng Mobile gửi yêu cầu gia hạn thêm 5 ngày qua `RenewalRequestScreen`
  |
  +---> [ĐIỂM GÃY DEF-01 (CRITICAL)]: API `POST /api/contracts/{id}/renew` chỉ ghi một dòng vào `HopDong.GhiChu`!
  |     Không sinh bản ghi `YeuCauGiaHan`! Admin trên Web không hề nhìn thấy yêu cầu gia hạn! Luồng bị đứt hoàn toàn!
  |
[BƯỚC 6: Web Quản trị viên Quyết toán]
Khách trả máy -> Kỹ thuật lập biên bản thu hồi (LoaiBienBan = 1) -> Hợp đồng sang Chờ quyết toán (4)
  |
  +---> Kế toán mở bản quyết toán cọc nguyên tử: Cấn trừ nợ thuê, hoàn cọc còn dư qua đúng 1 Phiếu chi
  |
  +---> Hợp đồng sang Hoàn thành (2), thiết bị trở về kho sẵn sàng (0). Toàn vẹn tài chính 100%.
```

---

## PHẦN V: KẾT LUẬN & ĐỀ XUẤT NỀN TẢNG CHO KẾ HOẠCH SỬA ĐỔI

### 5.1. Đánh giá tổng quan chất lượng hệ thống

1. **Về Kiến trúc Cơ sở Dữ liệu & Nghiệp vụ Lõi**:
   - Kiến trúc CSDL của RentalSystem cực kỳ vững chắc, đáp ứng 100% 18 bảng danh mục và các ràng buộc toàn vẹn của khóa luận tốt nghiệp `CNTT_KLCN058.docx`.
   - Các cơ chế kiểm soát đồng thời chống đặt trùng máy (`SemaphoreSlim` in-memory trên Web và `sp_getapplock` trên API Mobile) hoạt động rất chuẩn mực.
   - Cơ chế quyết toán cọc nguyên tử chống hoàn vượt số dư và chống hoàn lặp đạt chuẩn tài chính doanh nghiệp.
2. **Về Các Lỗi Cần Khắc Phục Khẩn Cấp**:
   - **DEF-02 (Blocker)**: Cần phục hồi phương thức `DebtCalculationHelper.GetAgingBadgeClass` và căn chỉnh tên nhóm tuổi nợ trong `RentalSystem/Common/DebtCalculationHelper.cs` để khôi phục 100% build health cho `ChallengerTests`.
   - **DEF-01 (Critical)**: Cần sửa đổi ngay action `RenewContract` trong `ApiContractsController.cs` để tạo bản ghi `YeuCauGiaHan` và bật cờ `hopDong.YeuCauGiaHan = true`, chấm dứt việc thất lạc yêu cầu gia hạn từ Mobile.
   - **DEF-03 (Critical)**: Cần loại bỏ hoàn toàn số tài khoản cá nhân hardcoded `0783406516` - `PHAN MINH QUAN`, chuyển sang cấu hình tài khoản doanh nghiệp an toàn trong `appsettings.json`.
   - **DEF-04 & DEF-12 & DEF-13 (Major/Minor)**: Sửa chữa lỗi dead link `#bankTransferInstructions`, dọn dẹp các class HTML/CSS trùng lặp xung đột và bổ sung `_ValidationScriptsPartial` cho các biểu mẫu.
   - **DEF-10 & DEF-11 (Major)**: Tái cấu trúc giao diện trang `CongNo/Index.cshtml` và `Database/Index.cshtml` tuân thủ nghiêm ngặt chuẩn Classic Navy & Pure White.
   - **DEF-05 & DEF-06 & DEF-08 (Major)**: Lập lộ trình nâng cấp phân hệ Mobile Flutter: bổ sung Canvas ký số, Sổ công nợ VietQR và phân định rõ 2 vai trò `KinhDoanh` và `KyThuat`.

---
*Tài liệu kiểm toán và mô phỏng được biên soạn độc lập, trung thực dựa trên bằng chứng kiểm tra mã nguồn thực tế và lưu trữ tại `docs/DANH_SACH_LOI_VA_MO_PHONG_TUONG_TAC_WEB_MOBILE.md`.*
