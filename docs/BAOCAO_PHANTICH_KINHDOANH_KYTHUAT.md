# BÁO CÁO PHÂN TÍCH TOÀN DIỆN QUY TRÌNH NGHIỆP VỤ, MA TRẬN PHÂN QUYỀN VÀ ĐÁNH GIÁ BẤT CẬP/CHỒNG CHÉO GIỮA HAI VAI TRÒ KINH DOANH VÀ KỸ THUẬT TRONG HỆ THỐNG RENTALSYSTEM

> **Cơ quan / Đơn vị thực hiện**: Ban Kiểm toán Quy trình & An ninh Hệ thống RentalSystem  
> **Nền tảng công nghệ**: ASP.NET Core MVC 9.0 (.NET 9.0 LTS), Entity Framework Core, SQL Server  
> **Mã văn bản**: `BC-KD-KT-AUDIT-20261030`  
> **Ngày phát hành**: 30/10/2026  
> **Chế độ kiểm toán**: Read-Only Empirical Audit (Bảo tồn 100% mã nguồn, duy trì 595/595 bài kiểm thử PASS, 0 Error, 0 Warning)  
> **Tài liệu căn cứ**: `ORIGINAL_REQUEST.md`, `GEMINI.md`, `.agents/rules/ui-design-system.md`, các báo cáo chuyên sâu `explorer_kd_1`, `explorer_kt_1`, `explorer_rbac_1`.

---

## MỤC LỤC TỔNG QUAN

- [PHẦN I: TỔNG QUAN HỆ THỐNG VÀ BỐI CẢNH VẬN HÀNH](#phần-i-tổng-quan-hệ-thống-và-bối-cảnh-vận-hành)
  - [1.1. Mô hình kinh doanh và bài toán vận hành cho thuê thiết bị công nghệ](#11-mô-hình-kinh-doanh-và-bài-toán-vận-hành-cho-thuê-thiết-bị-công-nghệ)
  - [1.2. Kiến trúc giải pháp phần mềm ASP.NET Core MVC 9.0](#12-kiến-trúc-giải-pháp-phần-mềm-aspnet-core-mvc-90)
  - [1.3. Danh mục vai trò và hạ tầng kiểm soát truy cập (Identity & RBAC)](#13-danh-mục-vai-trò-và-hạ-tầng-kiểm-soát-truy-cập-identity--rbac)
  - [1.4. Cơ chế điều hướng đăng nhập thông minh và trang AccessDenied](#14-cơ-chế-điều-hướng-đăng-nhập-thông-minh-và-trang-accessdenied)
- [PHẦN II: PHÂN TÍCH CHUYÊN SÂU QUY TRÌNH NGHIỆP VỤ VAI TRÒ KINH DOANH (SALES)](#phần-ii-phân-tích-chuyên-sâu-quy-trình-nghiệp-vụ-vai-trò-kinh-doanh-sales)
  - [2.1. Quy trình 1: Định giá, cấu hình gói cước, chiết khấu và thẩm định áp dụng Voucher](#21-quy-trình-1-định-giá-cấu-hình-gói-cước-chiết-khấu-và-thẩm-định-áp-dụng-voucher)
  - [2.2. Quy trình 2: Tiếp nhận và xử lý đơn thuê (Online qua Website vs Tại quầy Admin)](#22-quy-trình-2-tiếp-nhận-và-xử-lý-đơn-thuê-online-qua-website-vs-tại-quầy-admin)
  - [2.3. Quy trình 3: Thẩm định hồ sơ, ký đối chiếu, duyệt bàn giao máy và quản lý vòng đời đơn thuê 5 trạng thái](#23-quy-trình-3-thẩm-định-hồ-sơ-ký-đối-chiếu-duyệt-bàn-giao-máy-và-quản-lý-vòng-đời-đơn-thuê-5-trạng-thái)
  - [2.4. Quy trình 4: Xử lý và phê duyệt yêu cầu gia hạn hợp đồng (Extension Workflow)](#24-quy-trình-4-xử-lý-và-phê-duyệt-yêu-cầu-gia-hạn-hợp-đồng-extension-workflow)
  - [2.5. Quy trình 5: Quản trị công nợ, phân kỳ nợ, đối soát ngân hàng, tất toán và hoàn cọc](#25-quy-trình-5-quản-trị-công-nợ-phân-kỳ-nợ-đối-soát-ngân-hàng-tất-toán-và-hoàn-cọc)
  - [2.6. Quy trình 6: Phối hợp tác nghiệp giữa Kinh Doanh và Kỹ Thuật](#26-quy-trình-6-phối-hợp-tác-nghiệp-giữa-kinh-doanh-và-kỹ-thuật)
  - [2.7. Bảng danh mục chi tiết 30 chức năng đã triển khai của vai trò Kinh Doanh](#27-bảng-danh-mục-chi-tiết-30-chức-năng-đã-triển-khai-của-vai-trò-kinh-doanh)
- [PHẦN III: PHÂN TÍCH CHUYÊN SÂU QUY TRÌNH NGHIỆP VỤ VAI TRÒ KỸ THUẬT (KYTHUAT)](#phần-iii-phân-tích-chuyên-sâu-quy-trình-nghiệp-vụ-vai-trò-kỹ-thuật-kythuat)
  - [3.1. Quản lý kho máy vật lý theo Serial và vòng đời trạng thái thiết bị (0..4)](#31-quản-lý-kho-máy-vật-lý-theo-serial-và-vòng-đời-trạng-thái-thiết-bị-04)
  - [3.2. Quy trình kiểm tra thiết bị trước khi xuất kho (Pre-delivery Check)](#32-quy-trình-kiểm-tra-thiết-bị-trước-khi-xuất-kho-pre-delivery-check)
  - [3.3. Quy trình bàn giao máy hiện trường và lập/in Biên bản bàn giao chuẩn A4](#33-quy-trình-bàn-giao-máy-hiện-trường-và-lậpin-biên-bản-bàn-giao-chuẩn-a4)
  - [3.4. Quy trình tiếp nhận, điều phối và xử lý sự cố kỹ thuật & bảo dưỡng định kỳ](#34-quy-trình-tiếp-nhận-điều-phối-và-xử-lý-sự-cố-kỹ-thuật--bảo-dưỡng-định-kỳ)
  - [3.5. Cơ chế tài chính kỹ thuật, SLA và chính sách tạm dừng tính tiền thuê](#35-cơ-chế-tài-chính-kỹ-thuật-sla-và-chính-sách-tạm-dừng-tính-tiền-thuê)
  - [3.6. Quy trình thu hồi máy nhập kho khi kết thúc hợp đồng](#36-quy-trình-thu-hồi-máy-nhập-kho-khi-kết-thúc-hợp-đồng)
  - [3.7. Bảng danh mục chi tiết 18 chức năng đã triển khai của vai trò Kỹ Thuật](#37-bảng-danh-mục-chi-tiết-18-chức-năng-đã-triển-khai-của-vai-trò-kỹ-thuật)
- [PHẦN IV: PHỐI HỢP LIÊN VAI TRÒ VÀ VÒNG ĐỜI THIẾT BỊ / ĐƠN THUÊ](#phần-iv-phối-hợp-liên-vai-trò-và-vòng-đời-thiết-bị--đơn-thuê)
  - [4.1. Ma trận phối hợp liên vai trò theo từng giai đoạn vòng đời](#41-ma-trận-phối-hợp-liên-vai-trò-theo-từng-giai-đoạn-vòng-đời)
  - [4.2. Cơ chế phân công công việc (`PhanCongCongViec`) và tương tác đa chiều](#42-cơ-chế-phân-công-công-việc-phancongcongviec-và-tương-tác-đa-chiều)
  - [4.3. Phân định ranh giới điểm chạm trách nhiệm (Touchpoints) giữa Sales và Kỹ thuật](#43-phân-định-ranh-giới-điểm-chạm-trách-nhiệm-touchpoints-giữa-sales-và-kỹ-thuật)
- [PHẦN V: MA TRẬN PHÂN QUYỀN TOÀN DIỆN (RBAC MATRIX)](#phần-v-ma-trận-phân-quyền-toàn-diện-rbac-matrix)
  - [5.1. Bảng ma trận đối chiếu 45 chức năng trên toàn bộ 18 Controllers](#51-bảng-ma-trận-đối-chiếu-45-chức-năng-trên-toàn-bộ-18-controllers)
  - [5.2. Đánh giá tính nhất quán giữa Controller Authorization và UI Guards](#52-đánh-giá-tính-nhất-quán-giữa-controller-authorization-và-ui-guards)
- [PHẦN VI: ĐÁNH GIÁ BẤT CẬP, LỖ HỔNG BẢO MẬT & CHỒNG CHÉO TRÁCH NHIỆM](#phần-vi-đánh-giá-bất-cập-lỗ-hổng-bảo-mật--chồng-chéo-trách-nhiệm)
  - [6.1. Nhóm 1: Vi phạm nguyên tắc phân tách trách nhiệm tài chính (Separation of Duties - SoD)](#61-nhóm-1-vi-phạm-nguyên-tắc-phân-tách-trách-nhiệm-tài-chính-separation-of-duties---sod)
  - [6.2. Nhóm 2: Lỗ hổng can thiệp và xóa Serial kho vật lý (`ThietBiController`)](#62-nhóm-2-lỗ-hổng-can-thiệp-và-xóa-serial-kho-vật-lý-thietbicontroller)
  - [6.3. Nhóm 3: Lộ lọt thông tin cá nhân (PII) và dữ liệu tài chính hợp đồng cho Kỹ thuật](#63-nhóm-3-lộ-lọt-thông-tin-cá-nhân-pii-và-dữ-liệu-tài-chính-hợp-đồng-cho-kỹ-thuật)
  - [6.4. Nhóm 4: Lỗi ngắt kết nối giao diện ký số nhân viên (UI-Backend Disconnect)](#64-nhóm-4-lỗi-ngắt-kết-nối-giao-diện-ký-số-nhân-viên-ui-backend-disconnect)
  - [6.5. Nhóm 5: Thiếu đồng bộ điều kiện hiển thị UI Guard (UI Guard Mismatch)](#65-nhóm-5-thiếu-đồng-bộ-điều-kiện-hiển-thị-ui-guard-ui-guard-mismatch)
  - [6.6. Nhóm 6: Đứt gãy luồng vận hành thiết bị thực tế khi trả máy / thanh lý trước hạn](#66-nhóm-6-đứt-gãy-luồng-vận-hành-thiết-bị-thực-tế-khi-trả-máy--thanh-lý-trước-hạn)
  - [6.7. Nhóm 7: Khuyết thiếu phân hệ Quản lý Khách Hàng (CRM) độc lập cho Kinh Doanh](#67-nhóm-7-khuyết-thiếu-phân-hệ-quản-lý-khách-hàng-crm-độc-lập-cho-kinh-doanh)
  - [6.8. Nhóm 8: Các lỗ hổng an ninh Web ứng dụng (CSRF và IDOR trong thanh toán)](#68-nhóm-8-các-lỗ-hổng-an-ninh-web-ứng-dụng-csrf-và-idor-trong-thanh-toán)
- [PHẦN VII: KIẾN NGHỊ GIẢI PHÁP & LỘ TRÌNH CHUẨN HÓA](#phần-vii-kiến-nghị-giải-pháp--lộ-trình-chuẩn-hóa)
  - [7.1. Kiến trúc phân quyền Policy-based Authorization chuẩn mực](#71-kiến-trúc-phân-quyền-policy-based-authorization-chuẩn-mực)
  - [7.2. Chuẩn hóa quy trình bàn giao - thu hồi thiết bị 2 bước (2-Step Handover & Return)](#72-chuẩn-hóa-quy-trình-bàn-giao---thu-hồi-thiết-bị-2-bước-2-step-handover--return)
  - [7.3. Tái cấu trúc thẩm quyền tài chính trong xử lý bảo trì & sự cố](#73-tái-cấu-trúc-thẩm-quyền-tài-chính-trong-xử-lý-bảo-trì--sự-cố)
  - [7.4. Thiết kế phân hệ CRM Khách Hàng độc lập (`/Admin/KhachHang`)](#74-thiết-kế-phân-hệ-crm-khách-hàng-độc-lập-adminkhachhang)
  - [7.5. Khắc phục lỗi UI Disconnect chữ ký nhân viên trên `HopDong/Details.cshtml`](#75-khắc-phục-lỗi-ui-disconnect-chữ-ký-nhân-viên-trên-hopdongdetailscshtml)
  - [7.6. Đồng bộ hóa 100% UI Guards trên Razor Views và Sidebar Admin](#76-đồng-bộ-hóa-100-ui-guards-trên-razor-views-và-sidebar-admin)
  - [7.7. Bịt kín các lỗ hổng bảo mật CSRF và IDOR](#77-bịt-kín-các-lỗ-hổng-bảo-mật-csrf-và-idor)
  - [7.8. Lộ trình triển khai khuyến nghị theo thứ tự ưu tiên (Roadmap)](#78-lộ-trình-triển-khai-khuyến-nghị-theo-thứ-tự-ưu-tiên-roadmap)

---

## PHẦN I: TỔNG QUAN HỆ THỐNG VÀ BỐI CẢNH VẬN HÀNH

### 1.1. Mô hình kinh doanh và bài toán vận hành cho thuê thiết bị công nghệ
Hệ thống **RentalSystem** được thiết kế để giải quyết bài toán quản trị vận hành trọn vòng đời cho các doanh nghiệp cung cấp dịch vụ cho thuê thiết bị công nghệ (Laptop cao cấp, Máy tính để bàn PC Workstation, Thiết bị văn phòng, Màn hình chuyên dụng, Máy in công nghiệp). 

Mô hình kinh doanh của doanh nghiệp bao quát hai nhóm khách hàng mục tiêu:
1. **Khách hàng Doanh nghiệp (B2B)**: Thuê theo dự án số lượng lớn, dài hạn từ vài tháng đến nhiều năm, yêu cầu bảo lãnh cọc tài sản, chia kỳ thanh toán trả góp định kỳ hàng tháng, cam kết chất lượng dịch vụ (SLA) khắc phục sự cố khắt khe và xuất hóa đơn chứng từ, biên bản bàn giao có giá trị pháp lý.
2. **Khách hàng Cá nhân (B2C)**: Thuê ngắn hạn phục vụ học tập, thi cử, hội thảo, đồ án hoặc làm việc từ xa, yêu cầu quy trình thẩm định danh tính qua CCCD/chữ ký điện tử nhanh chóng, thanh toán trực tuyến linh hoạt (VNPay, Napas 247 VietQR) và giao nhận máy tận nơi.

Đặc thù cốt lõi của hoạt động cho thuê công nghệ là **tài sản vật lý có giá trị cao, dễ phát sinh hao mòn hoặc hư hỏng trong quá trình khách hàng sử dụng, và liên tục xoay vòng giữa các hợp đồng thuê khác nhau**. Do đó, sự sống còn của doanh nghiệp phụ thuộc vào hai trụ cột tác nghiệp chính:
- **Bộ phận Kinh Doanh (Sales)**: Chịu trách nhiệm về doanh số, đàm phán hợp đồng, thẩm định tín nhiệm khách hàng, kiểm soát tiền cọc bảo đảm, chia kỳ hạn công nợ, đôn đốc thu hồi nợ và đối soát dòng tiền.
- **Bộ phận Kỹ Thuật (Tech/Operation)**: Chịu trách nhiệm bảo toàn giá trị tài sản vật lý, quản lý kho máy theo từng mã Serial duy nhất, kiểm tra chất lượng phần cứng trước khi xuất xưởng, giao máy và lập biên bản hiện trường, sửa chữa sự cố theo SLA cam kết, và nghiệm thu thu hồi máy khi kết thúc hợp đồng.

### 1.2. Kiến trúc giải pháp phần mềm ASP.NET Core MVC 9.0
Hệ thống được xây dựng trên nền tảng **ASP.NET Core MVC 9.0 (.NET 9 LTS)** hiện đại, áp dụng kiến trúc phân tầng (Layered MVC Architecture) kết hợp mô hình phân chia khu vực nghiệp vụ (`Areas`):
- **Phân hệ Quản trị (`Areas/Admin`)**: Gồm 11 Controllers chuyên trách quản trị vận hành nội bộ, sử dụng hệ thống Razor View kết hợp giao diện doanh nghiệp chuẩn mực (Executive Deep Navy `#0f2b5c` & Pure White `#ffffff` đóng gói trong `classic-navy.css`).
- **Phân hệ Người dùng Client (`Controllers/`)**: Gồm 7 Controllers phục vụ khách hàng trực tuyến trải nghiệm xem sản phẩm, giỏ hàng, đặt thuê máy, ký số hợp đồng, tra cứu sổ công nợ cá nhân, báo hỏng thiết bị và thanh toán số.
- **Tầng Dữ liệu & ORM (`Models/`, EF Core)**: Sử dụng **Entity Framework Core 9.0** kết nối Microsoft SQL Server, mô hình hóa các thực thể dữ liệu quan hệ mạnh mẽ (`SanPham`, `ThietBi`, `LichSuThietBi`, `HopDong`, `ChiTietHopDong`, `KyHanThanhToan`, `PhieuThu`, `PhieuChi`, `PhieuBaoTri`, `BienBanBanGiao`, `PhanCongCongViec`, `KhuyenMai`, `YeuCauGiaHan`, `LichSuNhacNo`).
- **Tầng Dịch vụ & Xử lý Nền (Background Services & Helpers)**:
  - `ReservationCleanupService`: Hosted Service chạy ngầm định kỳ quét và giải phóng các đơn hàng giữ chỗ quá hạn 24 giờ.
  - `DebtCalculationHelper`: Thư viện tính toán thuật toán công nợ, phân loại tuổi nợ, tính phí phạt chậm trả và khóa nợ xấu tự động.
  - `SemaphoreSlim`: Cơ chế khóa bất đối xứng đa luồng kiểm soát tương tranh tồn kho (`InventoryLock`) và giao dịch thanh toán (`_paymentLock`).
  - `ClosedXML`: Động cơ kết xuất báo cáo tài chính và công nợ định dạng Excel (`.xlsx`) chuyên nghiệp theo chuẩn kế toán.

### 1.3. Danh mục vai trò và hạ tầng kiểm soát truy cập (Identity & RBAC)
Hệ thống quản lý định danh người dùng thông qua thực thể `NguoiDung` liên kết với bảng `VaiTro`. Theo khởi tạo chuẩn tại `RentalSystem/Models/DbInitializer.cs` (dòng 149–152), hệ thống định nghĩa chính thức **4 vai trò người dùng**:

```
+---------------------------------------------------------------------------------+
|                                 HỆ THỐNG VAI TRÒ                                |
+-----------------+---------------+-----------------------------------------------+
| Tên Vai Trò     | Mã Vai Trò    | Phạm vi trách nhiệm                           |
+-----------------+---------------+-----------------------------------------------+
| Admin           | 1             | Toàn quyền quản trị hệ thống, dữ liệu, user  |
| KinhDoanh       | 2             | Bán hàng, hợp đồng, cọc, công nợ, khuyến mãi  |
| KyThuat         | 3             | Quản lý Serial kho, bàn giao, bảo trì, SLA    |
| KhachHang       | 4             | Thuê máy, ký hợp đồng, trả góp, báo hỏng      |
+-----------------+---------------+-----------------------------------------------+
```

*Ghi chú kiểm toán*: Trong một số Controller (`CongNoController.cs:15`, `DocumentController.cs:99`), mã nguồn có tham chiếu đến vai trò `KeToan`. Tuy nhiên trong bảng `VaiTro` của CSDL hiện hành chỉ có 4 vai trò trên. Do đó, người dùng thực tế không bao giờ nhận được claim `KeToan`, các nghiệp vụ tài chính hiện thời do `Admin` và `KinhDoanh` kiêm nhiệm.

Cơ chế xác thực sử dụng **Cookie Authentication** (`RentalSystem/Program.cs` dòng 26–32), tích hợp **Rate Limiter** (`LoginLimiter` dòng 14–24 cho phép tối đa 5 lần thử/phút). Khi đăng nhập, `AccountController.Login` (dòng 81–114) chuyển đổi vai trò người dùng thành Claim chuẩn:
- `ClaimTypes.Name`: Tên tài khoản hoặc họ tên người dùng.
- `ClaimTypes.Role`: `Admin`, `KinhDoanh`, `KyThuat`, hoặc `KhachHang`.
- `ClaimTypes.NameIdentifier`: ID người dùng (`MaNguoiDung`).

### 1.4. Cơ chế điều hướng đăng nhập thông minh và trang AccessDenied
Hệ thống triển khai cơ chế điều hướng thông minh sau đăng nhập (`AccountController.cs` dòng 121–129) căn cứ vào Claim vai trò để đưa nhân viên đến đúng không gian làm việc chuyên biệt:
- **`Admin` hoặc `KinhDoanh`**: Chuyển hướng trực tiếp vào Bảng điều khiển Quản trị (`/Admin/Home`).
- **`KyThuat`**: Chuyển hướng trực tiếp vào Không gian công việc kỹ thuật cá nhân (`/Admin/PhanCong/MyTasks`).
- **`KhachHang`**: Chuyển hướng về Cổng thông tin khách hàng (`/Home/Index`).

Khi người dùng cố tình truy cập vào các Controller hoặc Action vượt quá thẩm quyền của vai trò, middleware ủy quyền của ASP.NET Core sẽ chuyển hướng yêu cầu về trang từ chối truy cập chuyên nghiệp `RentalSystem/Views/Account/AccessDenied.cshtml` (dòng 21–37). Trang này trả về mã HTTP `403 Forbidden`, hiển thị định danh người dùng kèm thông báo: *"Tài khoản của bạn (@User.Identity.Name - @roleName) không có quyền truy cập vào chức năng này"*, đồng thời cung cấp các nút điều hướng nhanh quay về trang làm việc phù hợp thay vì để người dùng rơi vào trạng thái bế tắc.

---

## PHẦN II: PHÂN TÍCH CHUYÊN SÂU QUY TRÌNH NGHIỆP VỤ VAI TRÒ KINH DOANH (SALES)

Vai trò **KinhDoanh** đóng vai trò là "máy phát doanh thu" và "người gác cổng tài chính" của hệ thống RentalSystem. Toàn bộ hoạt động của nhân viên kinh doanh xoay quanh 6 quy trình cốt lõi được lập trình chi tiết trong mã nguồn:

### 2.1. Quy trình 1: Định giá, cấu hình gói cước, chiết khấu và thẩm định áp dụng Voucher
1. **Cơ chế tính giá thuê cơ sở**:
   - Được hiện thực hóa tại `CartController.cs` (dòng 309–310, 346–353) và `HopDongController.cs` (dòng 342–356).
   - Công thức tính tiền thuê:
     $$\text{Số ngày thuê} = \max\left(1, (\text{NgayKetThuc} - \text{NgayBatDau}).\text{TotalDays}\right)$$
     $$\text{Tổng tiền thuê gộp} = \sum \left(\text{GiaThueNgay} \times \text{SoLuong} \times \text{Số ngày thuê}\right)$$
   - *Đặc điểm hiện tại*: Hệ thống áp dụng đơn giá ngày phẳng (`GiaThueNgay` trên model `SanPham`). Chưa có bảng cước tuần/tháng riêng biệt.
2. **Cơ chế thẩm định và áp dụng Voucher khuyến mãi**:
   - Hiện thực tại `CartController.CheckPromo` (dòng 186–252) và `CartController.Checkout` (dòng 355–374).
   - Mã voucher (`KhuyenMai`) được chuẩn hóa in hoa (`ToUpperInvariant()`) và trải qua 4 bước kiểm tra nghiêm ngặt:
     1. Khóa tìm kiếm khớp với `Code` hoặc `MaCode`.
     2. Trạng thái kích hoạt: `KichHoat == true`.
     3. Khung thời gian hiệu lực: `NgayBatDau <= DateTime.Now <= NgayKetThuc`.
     4. Số lượng khả dụng: `SoLuong > 0`.
   - Khi hợp lệ, thuật toán tính giảm trừ:
     $$\text{Tiền giảm} = \text{Round}\left(\frac{\text{Tổng tiền} \times \text{PhanTramGiam}}{100}\right)$$
     $$\text{Tổng tiền thực thu} = \max\left(0, \text{Tổng tiền} - \text{Tiền giảm}\right)$$
     $$\text{Số lượng voucher} = \max\left(0, \text{SoLuong} - 1\right)$$
3. **Quyền hạn quản lý Voucher của Kinh Doanh**:
   - Tại `Areas/Admin/Controllers/KhuyenMaiController.cs`: Nhân viên Kinh Doanh có toàn quyền:
     - Tạo mới voucher với ràng buộc chống trùng mã, chặn ngày kết thúc nhỏ hơn ngày bắt đầu, giới hạn phần trăm từ 1% đến 100%.
     - Bật/Tắt kích hoạt tức thời (`ToggleStatus` dòng 220–234).
     - Xóa an toàn (`Delete` dòng 191–214): Nếu voucher đã từng liên kết với hợp đồng trong lịch sử (`hasContracts == true`), hệ thống tự động chuyển sang chế độ Tạm dừng (`KichHoat = false`) để bảo toàn tính toàn vẹn dữ liệu kế toán, tuyệt đối không hard-delete.

### 2.2. Quy trình 2: Tiếp nhận và xử lý đơn thuê (Online qua Website vs Tại quầy Admin)
Hệ thống thiết lập hai phễu tiếp nhận đơn thuê độc lập nhưng đồng bộ hóa dữ liệu tồn kho:

```
[ Phễu 1: Khách đặt qua Website ]                      [ Phễu 2: Kinh doanh tạo tại quầy ]
                │                                                          │
    Khách chọn giỏ hàng (/Cart)                                 NV mở /Admin/HopDong/Create
                │                                                          │
   Kiểm tra nợ xấu & Blacklist                                 Nhập thông tin khách & CCCD
                │                                                          │
   Kiểm tra tồn kho (InventoryLock)                            Kiểm tra tồn kho (InventoryLock)
                │                                                          │
     Tạo HopDong (TrangThai = 0)                                 Tạo HopDong (TrangThai = 0)
     Gán HanChotKy = Now + 24h                                   Thiết lập Cọc & Trả trước
     Gán ThietBi.TrangThai = 3 (Giữ chỗ)                         Thu tiền cọc (Sinh PhieuThu)
                │                                                Gán ThietBi.TrangThai = 3
     Khách ký số + Tải CCCD 2 mặt                                          │
          (/Cart/SignContract)                                    Chờ thẩm định & duyệt
```

- **Kênh Online qua Website (`CartController.Checkout`)**:
  - Tự động thẩm định nợ xấu qua `DebtCalculationHelper.IsCustomerBlacklisted`. Nếu khách có kỳ hạn trễ hạn >15 ngày hoặc tổng nợ xấu >3.000.000 VNĐ, hệ thống lập tức khóa quyền đặt đơn.
  - Sử dụng khóa đồng bộ `CartController.InventoryLock` (SemaphoreSlim) để kiểm tra số lượng máy vật lý khả dụng (`TrangThai == 0: Sẵn sàng`), tự động gán thiết bị cụ thể vào `ChiTietHopDong` và chuyển trạng thái thiết bị sang `3: Giữ chỗ`.
  - Hợp đồng tạo ra có `TrangThai = 0: Chờ duyệt`, hạn chốt giữ chỗ 24 giờ (`HanChotKy = DateTime.Now.AddHours(24)`). Khách hàng được chuyển hướng sang `/Cart/SignContract` để tải ảnh CCCD 2 mặt (kiểm tra dung lượng <5MB, whitelist PNG/JPEG, magic bytes) và ký số Base64 (kiểm tra dung lượng <256KB, header PNG).
- **Kênh Trực tiếp tại Quầy (`HopDongController.Create`)**:
  - Dành cho nhân viên Kinh Doanh tiếp nhận khách hàng trực tiếp tại showroom/văn phòng.
  - Hỗ trợ tra cứu khách hàng cũ theo SĐT hoặc tự động tạo tài khoản `KhachHang` mới nếu chưa có trong hệ thống (dòng 441–454).
  - Ngăn chặn triệt để việc lấy thông tin của nhân viên nội bộ làm khách hàng thuê máy (dòng 411–415).
  - Bắt buộc phải có số CMND/CCCD hợp lệ.
  - **Cơ chế tài chính tách bạch tại quầy**: Cho phép Kinh Doanh phân định rõ `TienCocBaoDamMay` (cọc tài sản hoàn trả khi hết hợp đồng) và `TienThueTraTruoc` (tiền thuê nộp trước để gạch nợ kỳ hạn). Tự động sinh `PhieuThu` loại 1 (Thu cọc) và loại 0 (Thu thuê trả trước) ngay khi lưu đơn.
  - Thiết bị được chuyển sang `TrangThai = 3: Giữ chỗ`, chờ bước thẩm định đối chiếu hồ sơ.

### 2.3. Quy trình 3: Thẩm định hồ sơ, ký đối chiếu, duyệt bàn giao máy và quản lý vòng đời đơn thuê 5 trạng thái
Vòng đời hợp đồng thuê máy gồm **5 trạng thái chuyển dịch chặt chẽ** tại `HopDongController.UpdateStatus` (dòng 599–1060):

```
       ┌───────────────────────────────┐
       │   0: Chờ duyệt (Giữ chỗ)      │ ──[Hủy đơn (status=3)]──► 3: Đã hủy (Giải phóng kho)
       └───────────────────────────────┘
                       │
         [Kinh doanh đối chiếu hồ sơ]
         [Bắt buộc: CCCD + Chữ ký KH]
         [Bắt buộc: Chữ ký nhân viên]
         [Duyệt giao máy (status=1)]
                       ▼
       ┌───────────────────────────────┐
       │    1: Đang cho thuê (Active)  │ ──[Trả máy trước hạn]───► 2: Hoàn tất (Quyết toán)
       └───────────────────────────────┘
           │                       │
     [Khách trả máy]         [Khách trả máy]
    [Còn nợ sau cọc]        [Hết nợ sau cọc]
           │                       │
           ▼                       ▼
┌───────────────────────┐  ┌───────────────────────┐
│ 4: Đã trả máy         │  │ 2: Hoàn tất           │
│ (Chờ quyết toán nợ)   │  │ (Thu hồi & Hoàn cọc)  │
└───────────────────────┘  └───────────────────────┘
           │
     [Tất toán đủ nợ]
           ▼
┌───────────────────────┐
│ 2: Hoàn tất           │
└───────────────────────┘
```

- **Điều kiện tiên quyết để Duyệt giao máy (`status = 1`)**:
  Tại dòng 653–664, hệ thống kiểm tra 2 điều kiện bắt buộc:
  1. Hợp đồng phải có chữ ký của khách hàng (`ChuKyKhachHang`) và ảnh CCCD (`AnhCCCD_Truoc` hoặc `AnhCMND`).
  2. Bắt buộc nhân viên Kinh Doanh phải hoàn tất Chữ ký nhân viên đối chiếu (`ChuKyNhanVien`).
- **Các tác vụ hệ thống tự động thực thi khi Duyệt giao máy (`status = 1`)**:
  1. *Cập nhật thiết bị*: Đổi toàn bộ máy từ `3: Giữ chỗ` sang `1: Đang cho thuê` (dòng 671), ghi nhật ký `LichSuThietBi`.
  2. *Lập biên bản bàn giao*: Tự động tạo `BienBanBanGiao` xuất kho (`LoaiBienBan = 0`) với thông tin phụ kiện tiêu chuẩn (dòng 683–698).
  3. *Sinh lịch trình trả góp (`KyHanThanhToan`)*: Thuật toán phân kỳ (dòng 700–749) lấy số tiền thuê còn lại sau khi trừ tiền thuê trả trước (`remainingRentToSplit = TongTien - TienThueTraTruoc`), chia đều cho `SoKyHan` (làm tròn đến hàng nghìn VNĐ). Kỳ 1 đến hạn ngay ngày nhận máy (`NgayBatDau`), các kỳ tiếp theo phân bố đều theo khoảng cách thời gian thuê.
- **Ràng buộc an toàn trạng thái**:
  - Không cho phép chuyển ngược từ `1` (Đang thuê) hoặc `4` (Đã trả máy) về `0` (Chờ duyệt).
  - Không cho phép hủy trực tiếp khi máy đang ở trạng thái `1: Đang cho thuê`.
  - Chặn hoàn tất hoặc hủy khi hợp đồng còn phiếu bảo trì chưa đóng (`TrangThai == 1 || TrangThai == 2`).
- **Cơ chế thu hồi giải phóng kho máy khi khách trả máy (`status = 4` hoặc `status = 2`)**:
  - Tại dòng 762–818: Hệ thống giải phóng thiết bị về kho (`TrangThai = 0: Sẵn sàng`), lập tức cho phép khách hàng khác thuê tiếp; ngoại trừ thiết bị đã bị hỏng hoàn toàn (`TrangThai = 4`) thì giữ nguyên trạng thái thanh lý để bảo vệ kho.
  - Tự động sinh `BienBanBanGiao` thu hồi nhập kho (`LoaiBienBan = 1`).
  - Nếu sau khi cấn trừ cọc khách vẫn còn nợ, hệ thống chuyển sang trạng thái `4: Đã trả máy (Chờ quyết toán công nợ)` để tiếp tục theo dõi thu hồi nợ (dòng 844–895).
- **Cơ chế tự động dọn dẹp đơn quá hạn giữ chỗ 24h**:
  - Thủ công: Kinh Doanh bấm nút "Quét Quá Hạn Giữ Chỗ" (`QuetDonQuaHanGiuCho` dòng 2133–2161).
  - Tự động: Background Hosted Service `ReservationCleanupService` (chạy ngầm mỗi 15 phút) tự động quét các đơn `TrangThai == 0`, quá `HanChotKy`, chưa nộp cọc và chưa ký, tự động hủy và giải phóng thiết bị về kho.

### 2.4. Quy trình 4: Xử lý và phê duyệt yêu cầu gia hạn hợp đồng (Extension Workflow)
Tại `HopDongController.cs` (`YeuCauGiaHan` dòng 1678, `DuyetGiaHan` dòng 1704–1823) và view `YeuCauGiaHan.cshtml`:
1. **Tiếp nhận yêu cầu**: Khách hàng gửi yêu cầu qua web (`/Cart/YeuCauGiaHan`). Hệ thống lưu vào bảng `YeuCauGiaHans` với `TrangThai = 0: Chờ duyệt`.
2. **Kinh Doanh tra cứu danh sách yêu cầu gia hạn**:
   - Giao diện chuyên biệt `/Admin/HopDong/YeuCauGiaHan` với bộ lọc 4 tab: Tất cả, Chờ duyệt, Đã chấp nhận, Từ chối. Thẻ cảnh báo nổi bật ngay trên đầu trang chi tiết hợp đồng `/Admin/HopDong/Details/{id}`.
3. **Thuật toán thẩm định khi Phê duyệt gia hạn (`DuyetGiaHan`)**:
   - *Kiểm tra xung đột lịch thiết bị*:
     ```csharp
     bool conflict = await _context.ChiTietHopDongs.AnyAsync(other =>
         other.MaHopDong != id &&
         other.MaThietBi == ct.MaThietBi &&
         other.HopDong.TrangThai != 2 && other.HopDong.TrangThai != 3 &&
         other.HopDong.NgayBatDau.Date < extEnd &&
         other.HopDong.NgayKetThuc.Date > extStart);
     ```
     Nếu bất kỳ thiết bị nào trong hợp đồng đã có đơn hàng khác đặt trước trong khoảng thời gian gia hạn, hệ thống lập tức từ chối và cảnh báo lỗi cụ thể.
   - *Tính toán chi phí phát sinh*:
     $$\text{Đơn giá ngày} = \frac{\text{TongTien}}{\text{Tổng số ngày thuê ban đầu}}$$
     $$\text{Tiền thuê phát sinh} = \text{Round}\left(\frac{\text{Đơn giá ngày} \times \text{Số ngày gia hạn}}{1000}\right) \times 1000$$
   - *Cập nhật hợp đồng và sinh kỳ hạn thanh toán mới*:
     - Tăng ngày kết thúc: `hopDong.NgayKetThuc = extEnd`.
     - Tăng tổng tiền hợp đồng: `hopDong.TongTien += additionalRent`.
     - Sinh thêm đúng 1 kỳ hạn thanh toán mới (`KyHanThanhToan`) với số tiền bằng `additionalRent`, ngày đến hạn là ngày bắt đầu gia hạn.
     - Cập nhật bản ghi `YeuCauGiaHan`: `TrangThai = 1: Đã duyệt`, lưu `MaNguoiDuyet`, `NgayDuyet`, `ChiPhiPhatSinh`, `GhiChuAdmin`.
4. **Từ chối gia hạn**: Chuyển `YeuCauGiaHan.TrangThai = 2: Từ chối`, ghi rõ lý do phản hồi cho khách hàng.

### 2.5. Quy trình 5: Quản trị công nợ, phân kỳ nợ, đối soát ngân hàng, tất toán và hoàn cọc
Phân hệ tài chính công nợ được xây dựng chuyên sâu tại `CongNoController.cs`, `DebtCalculationHelper.cs`, `PaymentController.cs` và `HopDongController.cs`:

1. **Thuật toán phân kỳ nợ, phạt chậm trả và phân loại nhóm tuổi nợ**:
   - Tại `DebtCalculationHelper.CalculateLateFee`: Sau thời gian ân hạn 3 ngày kể từ ngày đến hạn (`daysPastDue > 3`), áp dụng mức phạt `0.1%/ngày` trên số tiền gốc chưa trả:
     $$\text{Phí phạt} = \text{Round}\left(\text{Số tiền nợ} \times 0.001 \times \text{Số ngày trễ}, 0\right)$$
   - Tại `DebtCalculationHelper.CalculateAgingTier`: Tự động phân loại 4 nhóm tuổi nợ chuẩn kế toán:
     - Nhóm 0: Đúng hạn (`overdueDays <= 0`).
     - Nhóm 1 (Cần chú ý): Trễ hạn 1–30 ngày.
     - Nhóm 2 (Dưới tiêu chuẩn): Trễ hạn 31–60 ngày.
     - Nhóm 3 (Nghi ngờ): Trễ hạn 61–90 ngày.
     - Nhóm 4 (Nợ xấu / Khóa thuê): Trễ hạn > 90 ngày.
2. **Cơ chế khóa thuê tự động (Adversarial Blacklist Protection)**:
   - Tại `DebtCalculationHelper.IsCustomerBlacklisted`: Khách hàng bị khóa đặt thuê/ký hợp đồng mới nếu rơi vào 1 trong 2 điều kiện:
     - Điều kiện 1: Có bất kỳ kỳ hạn nào trễ hạn > 15 ngày.
     - Điều kiện 2: Tổng dư nợ quá hạn toàn hệ thống vượt hạn mức 3.000.000 VNĐ.
3. **Trung tâm Quản trị Công nợ (`/Admin/CongNo`)**:
   - Dashboard 4 chỉ số KPI: Tổng công nợ, Tổng nợ quá hạn, Tỷ lệ thu hồi (%), Số khoản nợ xấu.
   - Thống kê chi tiết số khoản và tổng số tiền của từng nhóm trong 4 nhóm tuổi nợ.
   - Bộ lọc tìm kiếm đa tiêu chí: Mã hợp đồng, Họ tên, SĐT, CCCD, nhóm tuổi nợ, khoảng ngày.
   - 3 Tab phân loại: *Tất cả công nợ*, *Nợ quá hạn*, *Sắp đến hạn (7 ngày tới)*.
   - **Nhắc nợ thông minh (`GuiNhacNo`)**: Tự động sinh mã VietQR động chuẩn NAPAS 247 kèm thông điệp nhắc nợ, gửi thông báo hệ thống đến khách hàng và lưu vết vào `LichSuNhacNo`.
   - **Xuất báo cáo Excel (`ExportExcel`)**: Sử dụng thư viện ClosedXML xuất file `.xlsx` định dạng số kế toán `#,##0 VNĐ`, phân loại chi tiết theo tuổi nợ.
4. **Quy trình thu tiền kỳ hạn & Đối soát thanh toán (`ConfirmPayment`)**:
   - Sử dụng khóa đồng bộ `_paymentLock` và transaction mức cô lập `Serializable` (dòng 1195–1200) chống tương tranh.
   - *Thanh toán thiếu (trả một phần)*: Ghi nhận số tiền thực thu, cho phép nhân viên nhập ngày hẹn trả tiếp theo (`NgayHenTraTiepTheo`) và ghi chú cam kết.
   - *Thanh toán thừa (Waterfall Cascade)*: Số tiền trả thừa tự động đổ dồn thanh toán tiếp cho các kỳ hạn tương lai; nếu vẫn còn thừa tiếp tục cấn trừ phí bồi thường hư hại; nếu vẫn còn thừa ghi nhận vào trường `TienTraThua` của hợp đồng để chuẩn bị hoàn trả cho khách.
5. **Duyệt biên lai chuyển khoản ngân hàng (`DuyetBienLai`)**:
   - Khách tải ảnh ủy nhiệm chi/biên lai tại `/Cart/ContractDetail`.
   - Kinh Doanh đối soát giao dịch tại modal chi tiết, bấm Duyệt để gạch nợ tức thời (sinh `PhieuThu` LoaiPhieu = 0) hoặc Từ chối để khách gửi lại.
6. **Thanh toán tự động gạch nợ qua VNPay & OpenBanking Webhook**:
   - VNPay IPN (`PaymentController.VnPayIPN`): Tự động gạch nợ sau khi nhận callback hợp lệ.
   - OpenBanking Webhook (`PaymentController.BankingWebhook`): Tiếp nhận biến động số dư ngân hàng qua Napas VietQR, phân tích cú pháp regex `HD{id}` và `KY{k}`, tự động gạch nợ và bảo vệ chống trùng lặp giao dịch bằng mã tham chiếu `referenceCode`.
7. **Tất toán sớm toàn bộ hợp đồng (`TatToanSom`)**:
   - Tính tổng toàn bộ nợ gốc và phí phạt còn lại của tất cả kỳ hạn mở, thu một lần duy nhất qua `PhieuThu`, đóng tất cả các kỳ hạn (`TrangThai = 1`).
8. **Trả máy trước hạn (`TraMayTruocHan`)**:
   - Tính lại số ngày thuê thực tế và tiền thuê thực dùng, cộng phí phạt trả sớm (`phiPhatTraSom`), hủy bỏ toàn bộ các kỳ hạn tương lai, quyết toán cấn trừ tiền thuê thực tế + phí phạt + phí bồi thường với tổng tiền đã nộp. Nếu thừa tiền tự động sinh `PhieuChi` hoàn tiền thừa; nếu thiếu chuyển sang theo dõi thu hồi nợ.
9. **Quyết toán cọc và hoàn cọc (`HoanCoc`, `CalculateDepositSettlement`)**:
   - Cấn trừ nợ thuê và phí bồi thường hư hại từ tiền cọc.
   - Lập phiếu chi tiền mặt hoặc chuyển khoản (`PhieuChi`, `LoaiChi = 0`), ghi nhận `TienCocThucHoan` và `NgayHoanCoc`.

### 2.6. Quy trình 6: Phối hợp tác nghiệp giữa Kinh Doanh và Kỹ Thuật
Quy trình phối hợp liên bộ phận diễn ra qua các mốc bàn giao trách nhiệm:
1. **Xuất kho bàn giao**: Kinh Doanh chốt đơn, thu tiền cọc và duyệt hồ sơ pháp lý, sau đó tạo phân công công việc (`PhanCongCongViec`) giao Kỹ thuật viên phụ trách giao máy và lập Biên bản bàn giao.
2. **Vận hành & Sự cố**: Khách báo sự cố qua web, KTV tiếp nhận xử lý theo SLA. Nếu lỗi do khách hàng, KTV nhập `PhiDenBu`; Kinh Doanh căn cứ vào đó để thu tiền (`ThuPhiDenBu`) hoặc cấn trừ tiền cọc. Nếu lỗi khách quan, KTV đề xuất miễn giảm ngày hỏng (`ApDungTamDungTienThue`).
3. **Thu hồi nhập kho**: Hết hạn thuê, Kinh Doanh giao việc thu hồi cho KTV. KTV đến kiểm tra máy, lập Biên bản thu hồi nhập kho (`LoaiBienBan = 1`). Kinh Doanh căn cứ biên bản để thực hiện hoàn cọc (`HoanCoc`) hoặc chuyển đơn sang trạng thái `4: Đã trả máy (chờ nợ)`.

### 2.7. Bảng danh mục chi tiết 30 chức năng đã triển khai của vai trò Kinh Doanh

| STT | Phân hệ / Nhóm chức năng | Tên chức năng | Controller & Action | Method | Đường dẫn Route | Mô tả logic & Quyền thực thi |
|:---:|:---|:---|:---|:---:|:---|:---|
| 1 | **Dashboard Quản trị** | Bảng điều khiển kinh doanh | `HomeController.Index` | `GET` | `/Admin/Home` | Hiển thị doanh thu thuần, tổng đơn thuê, máy đang chạy, khách hàng thân thiết, cảnh báo trễ hạn nợ và biểu đồ 6 tháng. |
| 2 | **Dòng Sản Phẩm** | Danh sách sản phẩm | `SanPhamController.Index` | `GET` | `/Admin/SanPham` | Xem danh mục sản phẩm, thống kê tổng máy kho, máy khả dụng và máy đang cho thuê. |
| 3 | **Dòng Sản Phẩm** | Thêm sản phẩm mới | `SanPhamController.Create` | `GET/POST` | `/Admin/SanPham/Create` | Khởi tạo cấu hình sản phẩm, thông số kỹ thuật, đơn giá ngày (`GiaThueNgay`) và tiền cọc mẫu (`TienCoc`). |
| 4 | **Dòng Sản Phẩm** | Sửa thông tin sản phẩm | `SanPhamController.Edit` | `GET/POST` | `/Admin/SanPham/Edit/{id}` | Cập nhật cấu hình, mô tả, đơn giá thuê sản phẩm. |
| 5 | **Dòng Sản Phẩm** | Xóa sản phẩm | `SanPhamController.DeleteConfirmed` | `POST` | `/Admin/SanPham/Delete/{id}` | Xóa sản phẩm nếu trong kho chưa có serial máy nào thuộc dòng sản phẩm này. |
| 6 | **Serial Máy Kho** | Danh sách máy vật lý | `ThietBiController.Index` | `GET` | `/Admin/ThietBi` | Theo dõi toàn bộ serial máy và trạng thái (Sẵn sàng, Đang thuê, Bảo trì, Giữ chỗ, Thanh lý). |
| 7 | **Serial Máy Kho** | Nhập serial máy mới | `ThietBiController.Create` | `GET/POST` | `/Admin/ThietBi/Create` | Nhập máy mới vào kho, chống trùng lặp số Serial. |
| 8 | **Serial Máy Kho** | Sửa serial máy | `ThietBiController.Edit` | `GET/POST` | `/Admin/ThietBi/Edit/{id}` | Chỉnh sửa tình trạng máy (chặn sửa máy đang có khách thuê). |
| 9 | **Serial Máy Kho** | Xóa máy khỏi kho | `ThietBiController.DeleteConfirmed` | `POST` | `/Admin/ThietBi/Delete/{id}` | Xóa máy kho (chặn xóa máy đang cho thuê hoặc đã có lịch sử hợp đồng). |
| 10 | **Hợp Đồng Thuê Máy** | Danh sách đơn thuê | `HopDongController.Index` | `GET` | `/Admin/HopDong` | Bộ lọc đa tab: Tất cả, Quá hạn trả máy, Chờ duyệt gia hạn, Yêu cầu hủy, Chờ duyệt biên lai, Đang thuê, Chờ duyệt, Đã trả máy (chờ nợ), Hoàn tất, Đã hủy. |
| 11 | **Hợp Đồng Thuê Máy** | Tạo đơn thuê tại quầy | `HopDongController.Create` | `GET/POST` | `/Admin/HopDong/Create` | Nhập khách mới/cũ, chọn ngày thuê, chọn máy, kiểm tra tồn kho bằng `InventoryLock`, tách bạch cọc bảo đảm và thuê trả trước, tự động sinh phiếu thu cọc/thuê trả trước. |
| 12 | **Hợp Đồng Thuê Máy** | Chi tiết hợp đồng | `HopDongController.Details` | `GET` | `/Admin/HopDong/Details/{id}` | Xem hồ sơ khách hàng, thời gian thuê, bảng tài chính, ảnh CCCD 2 mặt, chữ ký 2 bên, danh sách serial, lịch trả góp, lịch sử phiếu thu, phiếu chi, biên bản bàn giao, bảo trì. |
| 13 | **Hợp Đồng Thuê Máy** | Duyệt & Chuyển trạng thái HĐ | `HopDongController.UpdateStatus` | `POST` | `/Admin/HopDong/UpdateStatus` | Điều chuyển vòng đời hợp đồng: Duyệt giao máy (status=1), Trả máy chờ nợ (status=4), Hoàn tất quyết toán (status=2), Hủy đơn (status=3). |
| 14 | **Hợp Đồng Thuê Máy** | Ký điện tử nhân viên | `HopDongController.AdminSign` | `POST` | `/Admin/HopDong/AdminSign` | Lưu chữ ký đối chiếu của nhân viên kinh doanh vào hợp đồng (kiểm tra giới hạn 256KB, header PNG). |
| 15 | **Hợp Đồng Thuê Máy** | Thu tiền kỳ hạn trả góp | `HopDongController.ConfirmPayment` | `POST` | `/Admin/HopDong/ConfirmPayment` | Gạch nợ kỳ hạn, xử lý thanh toán thiếu (hẹn ngày trả), xử lý thanh toán thừa (waterfall đổ kỳ sau, cấn trừ đền bù, lưu tiền trả thừa). SemaphoreSlim `_paymentLock`. |
| 16 | **Hợp Đồng Thuê Máy** | Hủy phiếu thu | `HopDongController.HuyPhieuThu` | `POST` | `/Admin/HopDong/HuyPhieuThu` | Hủy phiếu thu sai sót, tự động hoàn tác công nợ kỳ hạn và tính toán lại ngày trễ hạn, phí phạt. |
| 17 | **Hợp Đồng Thuê Máy** | Tất toán sớm hợp đồng | `HopDongController.TatToanSom` | `POST` | `/Admin/HopDong/TatToanSom` | Thu trọn gói toàn bộ nợ còn lại, gạch nợ tất cả kỳ hạn đang mở. |
| 18 | **Hợp Đồng Thuê Máy** | Điều chỉnh ngày đến hạn | `HopDongController.DieuChinhKyHan` | `POST` | `/Admin/HopDong/DieuChinhKyHan` | Gia hạn ngày trả nợ cho kỳ hạn chưa đóng, ghi rõ lý do gia hạn. |
| 19 | **Hợp Đồng Thuê Máy** | Thu tiền cọc bổ sung | `HopDongController.ThemTienCoc` | `POST` | `/Admin/HopDong/ThemTienCoc` | Thu thêm cọc trong quá trình thuê, tự động cấn trừ dần vào các kỳ hạn nợ. |
| 20 | **Hợp Đồng Thuê Máy** | Trả máy trước hạn | `HopDongController.TraMayTruocHan` | `POST` | `/Admin/HopDong/TraMayTruocHan` | Thanh lý hợp đồng sớm: tính lại tiền thuê theo ngày thực dùng + phạt trả sớm, hủy kỳ hạn tương lai, hoàn cọc thừa hoặc cấn trừ nợ. |
| 21 | **Hợp Đồng Thuê Máy** | Duyệt biên lai chuyển khoản | `HopDongController.DuyetBienLai` | `POST` | `/Admin/HopDong/DuyetBienLai` | Kiểm tra ảnh ủy nhiệm chi của khách, bấm duyệt để gạch nợ hoặc từ chối để khách gửi lại. |
| 22 | **Hợp Đồng Thuê Máy** | Hoàn tiền cọc | `HopDongController.HoanCoc` | `POST` | `/Admin/HopDong/HoanCoc` | Lập phiếu chi tiền hoàn cọc sau khi thanh lý và trừ hết công nợ. |
| 23 | **Hợp Đồng Thuê Máy** | Quét đơn quá hạn giữ chỗ | `HopDongController.QuetDonQuaHanGiuCho` | `POST` | `/Admin/HopDong/QuetDonQuaHanGiuCho` | Quét thủ công giải phóng các đơn chờ duyệt quá 24h chưa ký/chưa cọc về kho. |
| 24 | **Yêu Cầu Gia Hạn** | Quản lý & Duyệt gia hạn | `HopDongController.YeuCauGiaHan` & `DuyetGiaHan` | `GET/POST` | `/Admin/HopDong/YeuCauGiaHan` | Tra cứu yêu cầu gia hạn, kiểm tra trùng lịch thiết bị, tính thêm tiền thuê phát sinh, tăng ngày kết thúc và sinh kỳ hạn trả góp mới. |
| 25 | **Mã Khuyến Mãi** | Quản lý voucher | `KhuyenMaiController.*` | `GET/POST` | `/Admin/KhuyenMai` | Quản lý toàn bộ danh mục mã giảm giá: Tạo, Sửa, Bật/Tắt kích hoạt, Xóa an toàn (Soft-disable nếu đã có đơn sử dụng). |
| 26 | **Quản Lý Công Nợ** | Bảng công nợ & Tuổi nợ | `CongNoController.Index` | `GET` | `/Admin/CongNo` | Theo dõi tổng nợ, nợ quá hạn, 4 nhóm tuổi nợ (1-30d, 31-60d, 61-90d, >90d), nợ xấu, gửi thông báo nhắc nợ VietQR động, xuất báo cáo Excel ClosedXML. |
| 27 | **Sự Cố & Đền Bù** | Thu phí bồi thường hư hại | `BaoTriController.ThuPhiDenBu` | `POST` | `/Admin/BaoTri/ThuPhiDenBu` | Lập phiếu thu loại 2 cho phí bồi thường sự cố do kỹ thuật viên xác định trách nhiệm khách hàng. |
| 28 | **Phân Công Việc** | Giao việc cho Kỹ thuật viên | `PhanCongController.Index`, `Create`, `Edit` | `GET/POST` | `/Admin/PhanCong` | Giao việc đi giao máy, thu hồi máy hoặc bảo trì thiết bị cho kỹ thuật viên. |
| 29 | **Thống Kê Báo Cáo** | Trung tâm phân tích Executive BI | `ThongKeController.Index`, `ExportExcel` | `GET` | `/Admin/ThongKe` | Báo cáo doanh thu thuần, dòng tiền, tỷ lệ khai thác kho máy, cơ cấu doanh thu danh mục, xuất Excel ClosedXML chuẩn kế toán. |
| 30 | **In Ấn Văn Bản** | In Hợp đồng & Biên bản | `DocumentController.InHopDong`, `InBienBanBanGiao`, `InPhieuThu` | `GET` | `/Document/*` | Mở và in trực tiếp Hợp đồng thuê máy, Biên bản bàn giao/thu hồi máy, Phiếu thu tiền. |

---

## PHẦN III: PHÂN TÍCH CHUYÊN SÂU QUY TRÌNH NGHIỆP VỤ VAI TRÒ KỸ THUẬT (KYTHUAT)

Vai trò **KyThuat** là "người bảo vệ tài sản vật lý" và "bảo chứng chất lượng dịch vụ" của hệ thống. Kỹ thuật viên đảm nhiệm toàn bộ vòng đời phần cứng của thiết bị:

### 3.1. Quản lý kho máy vật lý theo Serial và vòng đời trạng thái thiết bị (0..4)
1. **Định danh máy vật lý qua Serial**:
   - Mỗi máy vật lý cụ thể trong kho được định danh duy nhất bằng thuộc tính `SoSerial` trong thực thể `ThietBi` (`Models/AppModels.cs` dòng 41–51).
   - Hệ thống chống trùng lặp số Serial tuyệt đối khi nhập máy qua `AnyAsync(x => x.SoSerial == tb.SoSerial)`.
2. **Hệ thống 5 trạng thái thiết bị chuẩn hóa**:
   - `0 (Sẵn sàng - SanSang)`: Máy nằm trong kho, đã qua kiểm tra kỹ thuật, sẵn sàng xuất cho thuê.
   - `1 (Đang cho thuê - DangThue)`: Máy đang được khách hàng vận hành tại địa chỉ thuê.
   - `2 (Bảo trì / Sửa chữa - BaoTri)`: Máy đang được bảo dưỡng định kỳ trong kho hoặc đang sửa chữa sự cố phát sinh.
   - `3 (Giữ chỗ - GiuCho)`: Máy tạm khóa cho đơn hàng đang chờ duyệt (được bảo vệ bởi `ReservationCleanupService`).
   - `4 (Hỏng thanh lý - ThanhLy)`: Máy bị hư hại nghiêm trọng (cháy nổ mainboard, vỡ panel màn hình, ngâm nước rỉ sét nặng) không thể khắc phục kinh tế. Trạng thái này có tính chất **khóa vĩnh viễn (latch)** — máy bị loại khỏi danh sách khai thác và lưu vết lịch sử tài sản.
3. **Nhật ký biến động vòng đời (`LichSuThietBi`)**:
   - Mọi biến động trạng thái (nhập kho, xuất kho, sửa chữa, bàn giao, thu hồi) đều được tự động ghi nhận vào bảng `LichSuThietBi` kèm định danh nhân viên thực hiện (`MaNguoiThucHien`), hành động và mốc thời gian chính xác đến từng giây.

### 3.2. Quy trình kiểm tra thiết bị trước khi xuất kho (Pre-delivery Check)
1. **Tiếp nhận lệnh phân công**: KTV nhận thông báo nhiệm vụ trong `/Admin/PhanCong/MyTasks` với trạng thái `0 (Mới)`.
2. **Kiểm tra kỹ thuật tại kho**:
   - KTV nhấp vào liên kết `HĐ #...` để mở chi tiết hợp đồng, đối chiếu cấu hình và mã Serial chỉ định.
   - Tiến hành kiểm tra thực tế: Ngoại quan vỏ máy, bản lề, màn hình, cổng kết nối; Stress test phần cứng CPU/RAM/VGA, đo sức khỏe ổ cứng SSD và dung lượng pin; Cài đặt hệ điều hành sạch và phần mềm theo yêu cầu; Kiểm tra phụ kiện (dây sạc zin, chuột, túi chống sốc, tem niêm phong).
3. **Cập nhật tiến độ**: KTV bấm "Bắt đầu thực hiện" trên `MyTasks` để chuyển trạng thái việc sang `1 (Đang thực hiện)`.

### 3.3. Quy trình bàn giao máy hiện trường và lập/in Biên bản bàn giao chuẩn A4
1. **Bàn giao tại hiện trường**:
   - KTV mang máy đến địa chỉ khách hàng, cùng khách hàng bật máy kiểm tra cấu hình thực tế trùng khớp với hợp đồng, hướng dẫn sử dụng an toàn và phổ biến quy định bảo hành/hotline sự cố.
2. **Lập Biên bản bàn giao xuất kho**:
   - KTV mở modal `#modalLapBienBan` trên view chi tiết hợp đồng, chọn loại `Bàn giao xuất kho (LoaiBienBan = 0)`, ghi nhận danh mục phụ kiện và tình trạng ngoại quan máy.
3. **In ấn & Lưu trữ văn bản pháp lý**:
   - KTV mở `/Document/InBienBanBanGiao/{id}` để xuất bản in khổ A4 chuẩn pháp lý có Quốc hiệu, đại diện 2 bên, bảng danh mục Serial máy, phụ kiện và chữ ký hai bên.
   - In 02 bản cứng để ký tay lưu kho hoặc dùng bản PDF nhúng chữ ký số.

### 3.4. Quy trình tiếp nhận, điều phối và xử lý sự cố kỹ thuật & bảo dưỡng định kỳ
Hệ thống vận hành song song 2 luồng tiếp nhận sự cố:
- **Luồng 1: Khách hàng báo hỏng qua Client Portal (`/BaoTri/TaoPhieu`)**:
  - Khách chọn máy trong hợp đồng đang thuê (`TrangThai == 1`), chọn mức độ khẩn cấp (SLA: Tiêu chuẩn 48h, Khẩn cấp 12h, Ưu tiên cao 24h).
  - Tải lên hình ảnh góc hư hại (JPG/PNG <10MB) hoặc video quay hiện tượng chập chờn (MP4/MOV <50MB).
  - Hệ thống tự động tính hạn cam kết `HanHoanThanh` theo SLA, tạo `PhieuBaoTri` trạng thái `1 (Mới tiếp nhận)` và ghi nhật ký `LichSuThietBi`.
- **Luồng 2: Kỹ thuật viên lập phiếu bảo dưỡng nội bộ kho (`/Admin/BaoTri/Create`)**:
  - Dành cho máy trong kho cần vệ sinh, tra keo tản nhiệt hoặc thay pin (`MaHopDong = null`).
  - Gán `LoaiTrachNhiem = 2` (Cửa hàng chịu 100%), đổi trạng thái máy sang `2 (Bảo trì)`.
- **Quy trình xử lý sự cố tại xưởng (`/Admin/BaoTri/UpdateStatus`)**:
  - Chuyển trạng thái sang `2 (Đang sửa chữa)`, hệ thống tự động ghi nhận mốc `NgayBatDauBaoTri`.
  - Chẩn đoán nguyên nhân: Hao mòn tự nhiên (công ty chịu) hay rơi vỡ/vô nước do khách hàng (`LoaiTrachNhiem = 1`).
  - Nhập chi phí sửa thực tế của công ty (`ChiPhiSuaChua`), linh kiện thay thế (`LinhKienThayThe`), và phí bồi thường khách chịu (`PhiDenBu`). Khoản `PhiDenBu` tự động ghi nhận công nợ vào Hợp đồng (`DaGhiNhanCongNo = true`) và gửi thông báo cho khách hàng.
  - Sau khi sửa xong, chuyển sang `3 (Đã sửa xong)`. Khách hàng trên portal xác nhận Nghiệm thu (phiếu sang `5: Đã nghiệm thu & Đóng phiếu`, chấm điểm 1–5 sao) hoặc Từ chối yêu cầu sửa lại (phiếu quay về `2: Đang sửa`).

### 3.5. Cơ chế tài chính kỹ thuật, SLA và chính sách tạm dừng tính tiền thuê
Nhằm bảo vệ quyền lợi công bằng cho khách hàng khi thiết bị gặp lỗi kỹ thuật khách quan kéo dài, hệ thống tích hợp cơ chế **Tạm dừng tính tiền thuê** (`BaoTriController.ApDungTamDungTienThue` dòng 384–469):
- KTV nhập số ngày máy nằm xưởng (`SoNgayTamDung`).
- Hệ thống tự động tính đơn giá thuê ngày của máy trong hợp đồng:
  $$\text{Đơn giá ngày của máy} = \frac{\text{GiaChotThu}}{\text{Tổng số ngày thuê}}$$
  $$\text{Số tiền giảm trừ} = \text{Đơn giá ngày của máy} \times \text{SoNgayTamDung}$$
- Khấu trừ trực tiếp số tiền này vào tổng tiền hợp đồng (`hopDong.TongTien -= deduction`) và giảm trừ lũy kế vào các kỳ hạn nợ chưa thanh toán của khách hàng (`k.SoTienPhai = Math.Max(0, k.SoTienPhai - deductFromKy)`).

### 3.6. Quy trình thu hồi máy nhập kho khi kết thúc hợp đồng
1. Khi hợp đồng đến hạn hoặc khách trả máy sớm, KTV nhận nhiệm vụ thu hồi trên `MyTasks`.
2. KTV đến tiếp nhận máy, đối chiếu đúng số Serial vật lý, cắm sạc kiểm tra màn hình, bàn phím, pin, và kiểm tra phụ kiện đi kèm.
3. Đánh giá mức độ hao mòn: Hao mòn thông thường thì nhập kho; nếu có nứt vỡ, móp méo hoặc mất phụ kiện thì lập biên bản sự cố và nhập `PhiDenBu`.
4. Mở modal `#modalLapBienBan`, lập **Biên bản thu hồi nhập kho (`LoaiBienBan = 1`)**, in cho hai bên ký xác nhận.
5. Khi hợp đồng chuyển sang `4: Đã trả máy` hoặc thanh lý sớm: Các máy tốt tự động chuyển về `0: Sẵn sàng` để tái khai thác; các máy hỏng nặng chuyển sang `4: Hỏng thanh lý`.

### 3.7. Bảng danh mục chi tiết 18 chức năng đã triển khai của vai trò Kỹ Thuật

| STT | Phân hệ / Module | Đường dẫn URL | Action & Method | File Controller & Line | File View liên quan | Quyền hạn & Mô tả logic nghiệp vụ |
|:---:|---|---|---|---|---|---|
| **1** | **Điều hướng Đăng nhập** | `/Account/Login` | `Login` (POST) | `AccountController.cs:126` | `Views/Account/Login.cshtml` | Khi user có vai trò `KyThuat` đăng nhập thành công, tự động điều hướng trực tiếp vào trang công việc nội bộ `/Admin/PhanCong/MyTasks`. |
| **2** | **Công việc của tôi** | `/Admin/PhanCong/MyTasks` | `MyTasks` (GET) | `PhanCongController.cs:229` | `Areas/Admin/Views/PhanCong/MyTasks.cshtml` | Màn hình làm việc trung tâm: Thống kê 4 thẻ KPI cá nhân (Tổng, Mới, Đang làm, Hoàn thành); Lọc danh sách việc theo trạng thái; Cảnh báo hạn chót SLA đỏ nếu quá hạn; Chuyển nhanh sang chi tiết HĐ và PBT. |
| **3** | **Cập nhật Tiến độ Công việc** | `/Admin/PhanCong/UpdateStatus` | `UpdateStatus` (POST) | `PhanCongController.cs:268` | `Areas/Admin/Views/PhanCong/MyTasks.cshtml` | Cho phép KTV bắt đầu nhận việc (chuyển sang 1), ghi chú tiến độ thực hiện (`GhiChuTienDo`), hoặc báo hoàn tất (chuyển sang 2, tự động ghi nhận `NgayHoanThanh`). Hỗ trợ AJAX JSON. |
| **4** | **Chi tiết Công việc (API)** | `/Admin/PhanCong/Details/{id}` | `Details` (GET) | `PhanCongController.cs:342` | `MyTasks.cshtml` (Modal) | API trả về JSON chi tiết công việc phục vụ hiển thị modal popup xem nhanh và cập nhật tiến độ công việc ngay trên giao diện `MyTasks`. |
| **5** | **Kho máy Serial** | `/Admin/ThietBi` | `Index` (GET) | `ThietBiController.cs:24` | `Areas/Admin/Views/ThietBi/Index.cshtml` | Xem toàn bộ danh sách thiết bị vật lý trong kho kèm Dòng sản phẩm, Số Serial, Tình trạng máy và Huy hiệu trạng thái chuẩn Executive Dot Pill (`Sẵn sàng`, `Đang thuê`, `Bảo trì`, `Giữ chỗ`, `Hỏng thanh lý`). |
| **6** | **Khai báo Máy mới** | `/Admin/ThietBi/Create` | `Create` (GET/POST) | `ThietBiController.cs:31` | `Areas/Admin/Views/ThietBi/Create.cshtml` | Mở form và lưu máy mới vào kho: Chọn sản phẩm cha, nhập số Serial (kiểm tra chống trùng lặp), khởi tạo trạng thái `0 (Sẵn sàng)`, tình trạng `Mới 100%`. |
| **7** | **Cập nhật Serial Máy** | `/Admin/ThietBi/Edit/{id}` | `Edit` (GET/POST) | `ThietBiController.cs:70` | `Areas/Admin/Views/ThietBi/Edit.cshtml` | Chỉnh sửa thông tin máy vật lý. Có cơ chế an ninh khóa chặn không cho sửa máy đang có khách thuê hoặc máy đã được đặt trước trong hợp đồng. |
| **8** | **Xóa Thiết bị khỏi Kho** | `/Admin/ThietBi/Delete/{id}` | `Delete` & `DeleteConfirmed` (GET/POST) | `ThietBiController.cs:124` | `Areas/Admin/Views/ThietBi/Delete.cshtml` | Xác nhận và xóa máy khỏi hệ thống. Có cơ chế an ninh: Chặn xóa máy đang cho thuê và chặn xóa máy đã có lịch sử trong hợp đồng cũ để bảo toàn dữ liệu giao dịch. |
| **9** | **Quản lý Bảo trì & Sự cố** | `/Admin/BaoTri` | `Index` (GET) | `BaoTriController.cs:23` | `Areas/Admin/Views/BaoTri/Index.cshtml` | Xem danh sách toàn bộ phiếu sự cố từ khách và bảo dưỡng nội bộ kho. Bộ lọc đa chiều theo 5 trạng thái và lọc nhanh các phiếu trễ hạn cam kết SLA (`overdue_sla`). |
| **10** | **Lập Phiếu Bảo dưỡng Kho** | `/Admin/BaoTri/Create` | `Create` (GET/POST) | `BaoTriController.cs:50` | `Areas/Admin/Views/BaoTri/Create.cshtml` | Lập phiếu bảo dưỡng định kỳ cho thiết bị tồn kho (`MaHopDong = null`). Chọn máy kho (trạng thái 0 hoặc 2), phân công KTV, đặt hạn cam kết SLA, chuyển máy sang trạng thái 2 (Bảo trì), ghi nhật ký `LichSuThietBi`. |
| **11** | **Chi tiết Xử lý Bảo trì** | `/Admin/BaoTri/Details/{id}` | `Details` (GET) | `BaoTriController.cs:126` | `Areas/Admin/Views/BaoTri/Details.cshtml` | Xem hồ sơ sự cố toàn diện: Bằng chứng ảnh/video lỗi của khách, thông tin máy, thông tin khách hàng, lịch sử vòng đời máy `LichSuThietBis`, số tiền đền bù đã thu. |
| **12** | **Cập nhật Tiến độ & Chi phí Sửa chữa** | `/Admin/BaoTri/UpdateStatus` | `UpdateStatus` (POST) | `BaoTriController.cs:165` | `Areas/Admin/Views/BaoTri/Details.cshtml` | Cập nhật trạng thái phiếu (1..5), phân công KTV, nhập chi phí sửa thực tế của tiệm (`chiPhiSuaChua`), nhập phí đền bù (`phiDenBu`), phân định trách nhiệm, ghi nhận nguyên nhân và linh kiện thay thế. Tự động chuyển máy sang 4 (Hỏng thanh lý) nếu không thể khắc phục. |
| **13** | **Tạm dừng tính Tiền thuê** | `/Admin/BaoTri/ApDungTamDungTienThue` | `ApDungTamDungTienThue` (POST) | `BaoTriController.cs:386` | `Areas/Admin/Views/BaoTri/Details.cshtml` | Áp dụng chính sách miễn giảm tiền thuê khi máy nằm xưởng bảo dưỡng: Tự động tính đơn giá ngày của máy, tính số tiền khấu trừ theo số ngày tạm dừng, cấn trừ trực tiếp vào các kỳ hạn nợ chưa trả của Hợp đồng. |
| **14** | **Xem Chi tiết Hợp đồng** | `/Admin/HopDong/Details/{id}` | `Details` (GET) | `HopDongController.cs:171` | `Areas/Admin/Views/HopDong/Details.cshtml` | Cho phép KTV xem chi tiết đơn thuê được giao từ link trên `MyTasks`: Xem địa chỉ giao hàng, thông tin khách, danh sách serial máy cần giao, hồ sơ CCCD, chữ ký và danh sách biên bản bàn giao. |
| **15** | **Lập Biên bản Bàn giao / Thu hồi** | `/Admin/HopDong/LapBienBanBanGiao` | `LapBienBanBanGiao` (POST) | `HopDongController.cs:1986` | `Areas/Admin/Views/HopDong/Details.cshtml` (Modal) | KTV lập biên bản bàn giao xuất kho (`LoaiBienBan = 0`) hoặc thu hồi nhập kho (`LoaiBienBan = 1`), ghi nhận phụ kiện kèm theo, hiện trạng ngoại quan máy và chữ ký xác nhận của nhân viên phụ trách. |
| **16** | **In Biên bản Bàn giao / Thu hồi** | `/Document/InBienBanBanGiao/{id}` | `InBienBanBanGiao` (GET) | `DocumentController.cs:54` | `Views/Document/InBienBanBanGiao.cshtml` | Xuất bản in Biên bản bàn giao/thu hồi máy khổ A4 chuẩn pháp lý có Quốc hiệu, chi tiết đại diện 2 bên, bảng danh mục Serial máy, phụ kiện, hiện trạng máy và chữ ký số. Tích hợp nút in nhanh `window.print()`. |
| **17** | **In Hợp đồng Thuê máy** | `/Document/InHopDong/{id}` | `InHopDong` (GET) | `DocumentController.cs:23` | `Views/Document/InHopDong.cshtml` | Cho phép KTV mở và in hợp đồng điện tử của khách hàng để mang theo đối chiếu pháp lý, kiểm tra số Serial và đối chiếu chữ ký khách hàng khi đi giao máy tận nơi. |
| **18** | **Thông báo Hệ thống** | `/Account/ThongBao` | `ThongBao` (GET) | `AccountController.cs` | `Views/Account/ThongBao.cshtml` | KTV nhận các thông báo điều phối công việc, nhắc nhở nhiệm vụ mới và biến động sự cố thiết bị từ hệ thống. |

---

## PHẦN IV: PHỐI HỢP LIÊN VAI TRÒ VÀ VÒNG ĐỜI THIẾT BỊ / ĐƠN THUÊ

### 4.1. Ma trận phối hợp liên vai trò theo từng giai đoạn vòng đời
Vòng đời một hợp đồng thuê thiết bị công nghệ là một chuỗi phối hợp chặt chẽ giữa Kinh Doanh và Kỹ Thuật, được mô hình hóa qua bảng ma trận 6 giai đoạn:

| Giai đoạn vòng đời | Trách nhiệm của Kinh Doanh (Sales) | Trách nhiệm của Kỹ Thuật (Tech) | Sản phẩm bàn giao (Artifacts) |
|---|---|---|---|
| **1. Khởi tạo & Đặt cọc** | - Tư vấn, báo giá, áp dụng voucher.<br>- Kiểm tra nợ xấu, thẩm định CCCD.<br>- Thu cọc bảo đảm, ký hợp đồng đối chiếu.<br>- Chuyển HĐ sang `0: Chờ duyệt`. | - Theo dõi thiết bị ở trạng thái `3: Giữ chỗ`.<br>- Chuẩn bị sẵn máy vật lý trong kho. | - Đơn thuê `HopDong` (`TrangThai = 0`).<br>- Phiếu thu cọc `PhieuThu` (Loại 1).<br>- Ảnh CCCD & Chữ ký số khách hàng. |
| **2. Xuất kho & Giao nhận** | - Duyệt đơn hàng (`TrangThai = 1`).<br>- Tạo nhiệm vụ phân công giao máy.<br>- Kích hoạt lịch trình trả góp định kỳ. | - Nhận việc trên `MyTasks`.<br>- Kiểm tra ngoại quan, stress test phần cứng.<br>- Đi giao máy tận nơi, hướng dẫn sử dụng.<br>- Lập & In `BienBanBanGiao` (Loại 0). | - Biên bản bàn giao xuất kho có chữ ký 2 bên.<br>- Thiết bị chuyển `TrangThai = 1: Đang thuê`.<br>- Lịch trình trả góp `KyHanThanhToan`. |
| **3. Vận hành & Thanh toán** | - Theo dõi kỳ hạn nợ, gửi VietQR nhắc nợ.<br>- Thu tiền định kỳ, duyệt biên lai ngân hàng.<br>- Phê duyệt gia hạn hợp đồng (nếu có). | - Theo dõi tình trạng kỹ thuật thiết bị.<br>- Bảo dưỡng định kỳ thiết bị tồn kho. | - Phiếu thu tiền kỳ hạn `PhieuThu` (Loại 0).<br>- Kỳ thanh toán mới khi gia hạn. |
| **4. Xử lý sự cố kỹ thuật** | - Tiếp nhận thông tin phản ánh từ khách.<br>- Thu tiền bồi thường hư hại (`PhiDenBu`).<br>- Đối soát điều chỉnh công nợ khi miễn giảm. | - Tiếp nhận phiếu báo hỏng theo SLA.<br>- Đến tận nơi kiểm tra, sửa chữa/thay linh kiện.<br>- Xác định lỗi và nhập `PhiDenBu`.<br>- Đề xuất miễn giảm ngày hỏng (`ApDungTamDungTienThue`). | - Phiếu sự cố `PhieuBaoTri` (Trạng thái 1..5).<br>- Phiếu thu bồi thường `PhieuThu` (Loại 2).<br>- Đánh giá nghiệm thu 1..5 sao từ khách. |
| **5. Thu hồi & Nhập kho** | - Thông báo kết thúc hợp đồng hoặc trả sớm.<br>- Tạo nhiệm vụ phân công thu hồi máy.<br>- Chờ biên bản kiểm định tình trạng máy. | - Nhận việc thu hồi trên `MyTasks`.<br>- Đến nơi nhận máy, cắm nguồn kiểm tra toàn diện.<br>- Kiểm tra đủ phụ kiện, đối chiếu Serial.<br>- Lập & In `BienBanBanGiao` (Loại 1). | - Biên bản thu hồi nhập kho có chữ ký.<br>- Hợp đồng chuyển `4: Đã trả máy`.<br>- Máy tốt về `0: Sẵn sàng`, hỏng về `4: Thanh lý`. |
| **6. Quyết toán & Hoàn cọc** | - Chạy thuật toán quyết toán cọc:<br>  $$\text{Hoàn} = \text{Cọc} - \text{Nợ thuê} - \text{Đền bù}$$<br>- Lập phiếu chi hoàn cọc hoặc đôn đốc nợ.<br>- Đóng hợp đồng sang `2: Hoàn tất`. | - Đưa máy tốt vào khai thác lượt thuê mới.<br>- Lập phiếu bảo dưỡng/thanh lý máy hỏng. | - Phiếu chi hoàn cọc `PhieuChi` (Loại 0).<br>- Hợp đồng đóng hoàn tất `TrangThai = 2`. |

### 4.2. Cơ chế phân công công việc (`PhanCongCongViec`) và tương tác đa chiều
Hệ thống sử dụng bảng trung gian `PhanCongCongViec` làm cầu nối điều phối công việc giữa Kinh Doanh và Kỹ Thuật:
- **Người giao việc (`MaNguoiGiao`)**: Thường là nhân viên Kinh Doanh hoặc Quản trị viên Admin.
- **Người thực hiện (`MaNhanVien`)**: Kỹ thuật viên chịu trách nhiệm.
- **Liên kết ngữ cảnh**: Bắt buộc gắn với `MaHopDong` (khi đi giao máy hoặc thu hồi máy) hoặc `MaPhieuBaoTri` (khi sửa chữa sự cố).
- **Quy trình tương tác**:
  ```
  Kinh Doanh tạo việc ──> KTV nhận việc (MyTasks) ──> KTV Bắt đầu làm (Status=1) ──> KTV Báo xong (Status=2)
  ```

### 4.3. Phân định ranh giới điểm chạm trách nhiệm (Touchpoints) giữa Sales và Kỹ thuật
Hệ thống phân định ranh giới chức năng rõ ràng để đảm bảo kiểm soát nội bộ:
1. **Ranh giới Tài chính**: Kinh Doanh chịu trách nhiệm 100% về tiền bạc (thu cọc, hoàn cọc, gạch nợ kỳ hạn, duyệt biên lai chuyển khoản, xuất hóa đơn). Kỹ thuật viên tuyệt đối không được phép thao tác thu tiền mặt hay ký duyệt hoàn trả cọc tại quầy.
2. **Ranh giới Phần cứng & Kho**: Kỹ thuật viên chịu trách nhiệm 100% về tính toàn vẹn vật lý của máy móc (độ bền, nhiệt độ, linh kiện, số Serial, chẩn đoán nguyên nhân hỏng hóc). Kinh Doanh không được phép tự ý sửa đổi đánh giá kỹ thuật của máy.
3. **Điểm chạm chuyển giao (Handoff Points)**:
   - *Điểm chạm 1*: Chuyển giao đơn hàng từ Kinh Doanh sang Kỹ Thuật để xuất máy.
   - *Điểm chạm 2*: Chuyển giao biên bản đánh giá hư hỏng từ Kỹ Thuật sang Kinh Doanh để cấn trừ tiền cọc.
   - *Điểm chạm 3*: Chuyển giao biên bản thu hồi máy hoàn tất từ Kỹ Thuật sang Kinh Doanh để thanh lý hợp đồng.

---

## PHẦN V: MA TRẬN PHÂN QUYỀN TOÀN DIỆN (RBAC MATRIX)

### 5.1. Bảng ma trận đối chiếu 45 chức năng trên toàn bộ 18 Controllers
Dưới đây là bảng ma trận kiểm toán chi tiết toàn bộ 45 chức năng trên 18 Controllers (11 Admin Controllers và 7 Client Controllers):

> **Quy ước ký hiệu**:
> - **ALLOWED**: Cho phép thực thi hợp lệ theo đúng thẩm quyền nghiệp vụ.
> - **DENIED**: Bị chặn truy cập (HTTP 403 Forbidden hoặc HTTP 401 Unauthorized).
> - **PARTIAL**: Cho phép có điều kiện (chỉ xem/sửa dữ liệu thuộc quyền sở hữu của chính mình).
> - **RISK**: Cho phép nhưng tiềm ẩn rủi ro lấn quyền, vi phạm phân tách trách nhiệm (SoD), hoặc thiếu kiểm soát.
> - **UI MISMATCH**: Giao diện hiển thị không đồng bộ với Controller (gây lỗi 403 hoặc để lộ nút bấm thừa).

| STT | Phân Hệ / Controller | Action / Chức Năng | Thuộc Tính Authorize Thực Tế | KinhDoanh | KyThuat | Admin | KhachHang | Kiểm Tra UI Guard & Đánh Giá An Ninh |
|:---:|---|---|---|:---:|:---:|:---:|:---:|---|
| **I** | **ADMIN AREA (11 CONTROLLERS)** | | | | | | | |
| 1 | `Admin/Home` | `Index` (Dashboard tổng quan) | `[Authorize(Roles = "Admin,KinhDoanh")]` | ALLOWED | DENIED | ALLOWED | DENIED | **Khớp UI**: Sidebar ẩn hoàn toàn với `KyThuat` và `KhachHang`. |
| 2 | `Admin/SanPham` | `Index` (Danh sách sản phẩm) | `[Authorize(Roles = "Admin,KinhDoanh")]` | ALLOWED | DENIED | ALLOWED | DENIED | **Khớp UI**: Sidebar ẩn với `KyThuat`. |
| 3 | `Admin/SanPham` | `Create`, `Edit`, `Delete` | `[Authorize(Roles = "Admin,KinhDoanh")]` | ALLOWED | DENIED | ALLOWED | DENIED | **An toàn**: Chỉ Admin & Kinh doanh quản lý danh mục giá. |
| 4 | `Admin/ThietBi` | `Index` (Danh sách serial kho) | Class `Admin,KinhDoanh,KyThuat` | ALLOWED | ALLOWED | ALLOWED | DENIED | **Bất cập**: Cả 2 vai trò đều xem được toàn bộ kho máy. |
| 5 | `Admin/ThietBi` | `Create (GET/POST)` (Nhập serial mới) | Kế thừa Class (Không có Action guard) | **RISK** | **RISK** | ALLOWED | DENIED | **LỖ HỔNG LẤN QUYỀN**: Thiếu Action guard. Cả KD và KT đều tự nhập máy vào CSDL. |
| 6 | `Admin/ThietBi` | `Edit (GET/POST)` (Sửa serial/tình trạng) | Kế thừa Class (Không có Action guard) | **RISK** | **RISK** | ALLOWED | DENIED | **LỖ HỔNG LẤN QUYỀN**: KD có thể tự sửa tình trạng máy từ Hỏng sang Sẵn sàng. |
| 7 | `Admin/ThietBi` | `Delete`, `DeleteConfirmed` (Xóa máy) | Kế thừa Class (Không có Action guard) | **RISK** | **RISK** | ALLOWED | DENIED | **RỦI RO CAO**: Kỹ thuật hoặc Kinh doanh có thể xóa vĩnh viễn serial máy khỏi kho. |
| 8 | `Admin/HopDong` | `Index` (Danh sách đơn thuê) | `[Authorize(Roles = "Admin,KinhDoanh")]` | ALLOWED | DENIED | ALLOWED | DENIED | **Khớp UI**: `KyThuat` bị chặn ở cả Menu Sidebar lẫn Controller. |
| 9 | `Admin/HopDong` | `Details` (Chi tiết hợp đồng) | Kế thừa Class `Admin,KinhDoanh,KyThuat` | ALLOWED | **PARTIAL (OPEN)** | ALLOWED | DENIED | **LỘ THÔNG TIN PII/TÀI CHÍNH**: `KyThuat` xem được toàn bộ nợ, thanh toán, CCCD. |
| 10 | `Admin/HopDong` | `Create (GET/POST)` (Tạo đơn thủ công) | `[Authorize(Roles = "Admin,KinhDoanh")]` | ALLOWED | DENIED | ALLOWED | DENIED | **An toàn**: Kỹ thuật không thể tạo hợp đồng kinh doanh. |
| 11 | `Admin/HopDong` | `UpdateStatus` (Duyệt/Giao/Hoàn tất đơn) | `[Authorize(Roles = "Admin,KinhDoanh")]` | ALLOWED | DENIED | ALLOWED | DENIED | **Khớp UI**: Các nút chuyển trạng thái được ẩn với `KyThuat`. |
| 12 | `Admin/HopDong` | `AdminSign`, `LuuChuKy` (Ký số công ty) | `[Authorize(Roles = "Admin,KinhDoanh")]` | ALLOWED | DENIED | ALLOWED | DENIED | **An toàn**: Chỉ người đại diện KD/Admin được ký số. |
| 13 | `Admin/HopDong` | `ConfirmPayment`, `TatToanSom` | `[Authorize(Roles = "Admin,KinhDoanh")]` | ALLOWED | DENIED | ALLOWED | DENIED | **An toàn**: Chức năng thu tiền kinh doanh được bảo vệ. |
| 14 | `Admin/HopDong` | `ThemTienCoc`, `HoanCoc` (Thu/Chi cọc) | `[Authorize(Roles = "Admin,KinhDoanh")]` | ALLOWED | DENIED | ALLOWED | DENIED | **An toàn**: Chỉ Admin/Kinh doanh thao tác tài chính cọc. |
| 15 | `Admin/HopDong` | `DuyetGiaHan` (Xét duyệt gia hạn đơn) | `[Authorize(Roles = "Admin,KinhDoanh")]` | ALLOWED | DENIED | ALLOWED | DENIED | **An toàn**: Chỉ Kinh doanh duyệt kéo dài thời gian thuê. |
| 16 | `Admin/HopDong` | `TraMayTruocHan` (Thanh lý sớm) | `[Authorize(Roles = "Admin,KinhDoanh")]` | ALLOWED | DENIED | ALLOWED | DENIED | **ĐỨT GÃY NGHIỆP VỤ**: KD thanh lý và giải phóng máy về kho trước khi KT kiểm tra. |
| 17 | `Admin/HopDong` | `LapBienBanBanGiao` (Giao/Nhận máy) | Kế thừa Class `Admin,KinhDoanh,KyThuat` | ALLOWED | ALLOWED | ALLOWED | DENIED | **CHỒNG CHÉO VAI TRÒ**: Cả KD và KT đều có quyền lập biên bản giao nhận máy. |
| 18 | `Admin/HopDong` | `DuyetBienLai` (Khớp lệnh CK ngân hàng) | `[Authorize(Roles = "Admin,KinhDoanh")]` | ALLOWED | DENIED | ALLOWED | DENIED | **An toàn**: Kỹ thuật không thể can thiệp duyệt biên lai nợ. |
| 19 | `Admin/BaoTri` | `Index` (Danh sách phiếu sự cố) | Class `Admin,KyThuat,KinhDoanh` | ALLOWED | ALLOWED | ALLOWED | DENIED | **Bất cập**: KD thấy menu BT dù yêu cầu gốc là ẩn với KD. |
| 20 | `Admin/BaoTri` | `Create (GET)` (Form bảo dưỡng kho) | Kế thừa Class | ALLOWED | ALLOWED | ALLOWED | DENIED | **UI MISMATCH**: KD mở được form nhưng submit thì bị 403. |
| 21 | `Admin/BaoTri` | `Create (POST)` (Lưu phiếu bảo dưỡng kho) | `[Authorize(Roles = "Admin,KyThuat")]` | DENIED | ALLOWED | ALLOWED | DENIED | **Đúng phân quyền**: Chỉ Kỹ thuật/Admin tạo phiếu kho. |
| 22 | `Admin/BaoTri` | `Details` (Chi tiết phiếu bảo trì) | Class `Admin,KyThuat,KinhDoanh` | ALLOWED | ALLOWED | ALLOWED | DENIED | **Xem chung**: Cả 2 vai trò đều theo dõi được tiến trình sửa. |
| 23 | `Admin/BaoTri` | `UpdateStatus` (Cập nhật tiến độ & gán KTV) | `[Authorize(Roles = "Admin,KyThuat")]` | DENIED | ALLOWED | ALLOWED | DENIED | **UI MISMATCH**: Form hiện trên UI cho KD, KD submit bị 403. |
| 24 | `Admin/BaoTri` | `ApDungTamDungTienThue` (Giảm tiền thuê) | `[Authorize(Roles = "Admin,KyThuat")]` | DENIED | **RISK (SoD)** | ALLOWED | DENIED | **VI PHẠM SoD**: Kỹ thuật tự quyền giảm trừ tiền thuê của công ty không qua KD/Kế toán. |
| 25 | `Admin/BaoTri` | `ThuPhiDenBu`, `ThuPhiBaoTri` | `[Authorize(Roles = "Admin,KinhDoanh")]` | ALLOWED | DENIED | ALLOWED | DENIED | **UI MISMATCH**: Form hiện trên UI cho KT, KT submit bị 403. |
| 26 | `Admin/PhanCong` | `Index`, `Create`, `Edit`, `Delete` | `[Authorize(Roles = "Admin,KinhDoanh")]` | ALLOWED | DENIED | ALLOWED | DENIED | **Khớp UI**: Kỹ thuật bị ẩn menu Phân công việc. |
| 27 | `Admin/PhanCong` | `MyTasks` (Việc được giao của tôi) | `[Authorize]` (Kế thừa Class) | ALLOWED | ALLOWED | ALLOWED | DENIED | **PARTIAL**: Mỗi nhân viên chỉ thấy việc giao cho chính mình. |
| 28 | `Admin/PhanCong` | `UpdateStatus` (Cập nhật tiến độ việc) | `[Authorize]` (Kế thừa Class) | ALLOWED | ALLOWED (Cá nhân) | ALLOWED | DENIED | **THIẾU CSRF**: Thiếu `[ValidateAntiForgeryToken]`. |
| 29 | `Admin/CongNo` | `Index`, `ExportExcel` | `[Authorize(Roles = "Admin,KinhDoanh,KeToan")]` | ALLOWED | DENIED | ALLOWED | DENIED | **Khớp UI**: Kỹ thuật bị chặn hoàn toàn khỏi module công nợ. |
| 30 | `Admin/CongNo` | `GuiNhacNo` (Gửi SMS/Zalo nhắc nợ) | `[Authorize(Roles = "Admin,KinhDoanh,KeToan")]` | ALLOWED | DENIED | ALLOWED | DENIED | **THIẾU CSRF**: Thiếu `[ValidateAntiForgeryToken]`. |
| 31 | `Admin/KhuyenMai` | `Index`, `Create`, `Edit`, `Delete`, `Toggle` | `[Authorize(Roles = "Admin,KinhDoanh")]` | ALLOWED | DENIED | ALLOWED | DENIED | **Khớp UI**: Kỹ thuật bị chặn khỏi quản lý voucher. |
| 32 | `Admin/NguoiDung` | Toàn bộ chức năng quản lý User | `[Authorize(Roles = "Admin")]` | DENIED | DENIED | ALLOWED | DENIED | **An toàn tuyệt đối**: Chỉ Super Admin được phân quyền. |
| 33 | `Admin/Database` | Sao lưu và Phục hồi CSDL | `[Authorize(Roles = "Admin")]` | DENIED | DENIED | ALLOWED | DENIED | **An toàn tuyệt đối**: Chỉ Super Admin được backup/restore. |
| 34 | `Admin/ThongKe` | Báo cáo tài chính & Xuất Excel | `[Authorize(Roles = "Admin,KinhDoanh")]` | ALLOWED | DENIED | ALLOWED | DENIED | **Khớp UI**: Kỹ thuật bị chặn khỏi báo cáo doanh thu. |
| **II** | **CLIENT AREA (7 CONTROLLERS)** | | | | | | | |
| 35 | `Document` | `InHopDong` (Bản in hợp đồng) | `[Authorize]` + Code Check | ALLOWED | ALLOWED | ALLOWED | PARTIAL (Sở hữu) | **BẢO VỆ IDOR**: Khách chỉ in được HĐ của chính mình. |
| 36 | `Document` | `InBienBanBanGiao` (Bản in biên bản) | `[Authorize]` + Code Check | ALLOWED | ALLOWED | ALLOWED | PARTIAL (Sở hữu) | **BẢO VỆ IDOR**: Khách chỉ in được BB của chính mình. |
| 37 | `Document` | `InPhieuThu` (Bản in phiếu thu tiền) | `[Authorize]` + Code Check | ALLOWED | **DENIED** | ALLOWED | PARTIAL (Sở hữu) | **BẢO VỆ IDOR**: Kỹ thuật không được in phiếu thu (trừ phi là khách). |
| 38 | `BaoTri (Client)` | `TaoPhieu`, `TaoYeuCau` (Báo hỏng) | `[Authorize]` + Code Check | PARTIAL | PARTIAL | PARTIAL | PARTIAL (Sở hữu) | **BẢO VỆ IDOR**: Chỉ tạo phiếu cho HĐ đang thuê của chính mình. |
| 39 | `BaoTri (Client)` | `ChiTiet` (Tiến độ xử lý sự cố) | `[Authorize]` + Code Check | PARTIAL | PARTIAL | PARTIAL | PARTIAL (Sở hữu) | **BẢO VỆ IDOR**: Chặn xem phiếu nội bộ kho (`MaHopDong == null`). |
| 40 | `BaoTri (Client)` | `NghiemThu`, `DanhGia` (1-5 sao) | `[Authorize]` + Code Check | PARTIAL | PARTIAL | PARTIAL | PARTIAL (Sở hữu) | **BẢO VỆ IDOR**: Khách hàng nghiệm thu dịch vụ của chính mình. |
| 41 | `Cart` | `MyContracts`, `ContractDetail` | `[Authorize]` + Code Check | PARTIAL | PARTIAL | PARTIAL | PARTIAL (Sở hữu) | **BẢO VỆ IDOR**: Chống truy cập chéo đơn hàng giữa các khách. |
| 42 | `Cart` | `SignContract`, `EditContract`, `Delete` | `[Authorize]` + Code Check | PARTIAL | PARTIAL | PARTIAL | PARTIAL (Sở hữu) | **An toàn**: Chỉ khách sở hữu đơn chưa duyệt mới được thao tác. |
| 43 | `Cart` | `YeuCauGiaHan`, `GuiBienLai`, `TatToan` | `[Authorize]` + Code Check | PARTIAL | PARTIAL | PARTIAL | PARTIAL (Sở hữu) | **An toàn**: Khách tương tác với hợp đồng đang thuê của mình. |
| 44 | `Account` | `Profile`, `DoiMatKhau`, `MyDebt` | `[Authorize]` + Code Check | PARTIAL | PARTIAL | PARTIAL | PARTIAL (Sở hữu) | **BẢO VỆ IDOR**: Chỉ xem nợ và thông tin của chính mình. |
| 45 | `Payment` | `CreatePaymentUrl` (Tạo URL VNPay) | **Anonymous (Thiếu Authorize)** | ALLOWED | ALLOWED | ALLOWED | ALLOWED | **LỖ HỔNG IDOR / INFO DISCLOSURE**: Không kiểm tra đăng nhập/sở hữu. |

### 5.2. Đánh giá tính nhất quán giữa Controller Authorization và UI Guards
Qua khảo sát đối chiếu, hệ thống bộc lộ hai dạng lệch pha (Mismatch):
1. **Controller chặn nhưng UI hiển thị nút**: Điển hình là form `ThuPhiDenBu` và `UpdateStatus` trên `Areas/Admin/Views/BaoTri/Details.cshtml`. Giao diện không bọc điều kiện vai trò khiến nhân viên bấm nút bị văng lỗi 403.
2. **Controller mở rộng nhưng Menu UI ẩn**: Điển hình là menu "Đơn thuê máy" ẩn với Kỹ thuật nhưng Action `HopDong/Details` lại mở cho Kỹ thuật kế thừa từ Class. Khi KTV click vào link từ `MyTasks`, họ vẫn truy cập được vào toàn bộ dữ liệu tài chính của đơn thuê.

---

## PHẦN VI: ĐÁNH GIÁ BẤT CẬP, LỖ HỔNG BẢO MẬT & CHỒNG CHÉO TRÁCH NHIỆM

Qua kiểm toán toàn diện mã nguồn, chúng tôi chỉ ra **8 nhóm vấn đề, lỗ hổng bảo mật và bất cập nghiệp vụ cốt lõi**:

### 6.1. Nhóm 1: Vi phạm nguyên tắc phân tách trách nhiệm tài chính (Separation of Duties - SoD)
- **Vị trí mã nguồn**: `RentalSystem/Areas/Admin/Controllers/BaoTriController.cs` dòng 384–469 (`ApDungTamDungTienThue`).
- **Thực trạng**: Action được gán quyền `[Authorize(Roles = "Admin,KyThuat")]`. Khi kỹ thuật viên gọi action này, hệ thống tự động trừ tiền vào tổng tiền hợp đồng (`hopDong.TongTien -= deduction`) và tự động giảm số tiền nợ trên các kỳ hạn thanh toán (`k.SoTienPhai = Math.Max(0, k.SoTienPhai - deductFromKy)`). Ngược lại, nhân viên Kinh Doanh (người quản lý hợp đồng và tài chính khách hàng) lại bị chặn (HTTP 403).
- **Hệ quả rủi ro**: Vi phạm nghiêm trọng nguyên tắc SoD trong quản trị tài chính doanh nghiệp. Kỹ thuật viên có quyền tự ý "miễn giảm doanh thu" của công ty mà không cần sự phê duyệt của Trưởng phòng Kinh doanh hay Kế toán.

### 6.2. Nhóm 2: Lỗ hổng can thiệp và xóa Serial kho vật lý (`ThietBiController`)
- **Vị trí mã nguồn**: `RentalSystem/Areas/Admin/Controllers/ThietBiController.cs` dòng 12–13, 124, 134.
- **Thực trạng**: Controller đặt quyền Class `[Authorize(Roles = "Admin,KinhDoanh,KyThuat")]`. Các action `Create`, `Edit`, `Delete`, `DeleteConfirmed` không có thuộc tính hạn chế quyền ở mức Action.
- **Hệ quả rủi ro**: 
  - Kỹ thuật viên có quyền bấm Xóa vĩnh viễn serial máy khỏi CSDL (`DeleteConfirmed`).
  - Nhân viên Kinh Doanh có quyền tự ý sửa tình trạng máy từ "Bảo trì/Hỏng" sang "Sẵn sàng" để xuất cho thuê ép chỉ tiêu doanh số mà không qua kiểm định kỹ thuật phần cứng.

### 6.3. Nhóm 3: Lộ lọt thông tin cá nhân (PII) và dữ liệu tài chính hợp đồng cho Kỹ thuật
- **Vị trí mã nguồn**: `RentalSystem/Areas/Admin/Controllers/HopDongController.cs` dòng 171 (`Details`) và view `Areas/Admin/Views/HopDong/Details.cshtml`.
- **Thực trạng**: Action `Details` kế thừa quyền Class gồm cả `KyThuat`. View `Details.cshtml` không hề che mờ hay ẩn các khối tài chính đối với kỹ thuật viên.
- **Hệ quả rủi ro**: Khi kỹ thuật viên bấm vào link HĐ từ `MyTasks` để xem địa chỉ giao máy, họ thấy toàn bộ: doanh thu đơn hàng, số tiền cọc, lịch sử trả tiền, các kỳ nợ quá hạn, số CMND/CCCD và ảnh chụp 2 mặt của khách hàng. Điều này vi phạm quy định bảo vệ dữ liệu cá nhân (PII) và bảo mật thông tin tài chính nội bộ.

### 6.4. Nhóm 4: Lỗi ngắt kết nối giao diện ký số nhân viên (UI-Backend Disconnect)
- **Vị trí mã nguồn**:
  - Backend: `HopDongController.UpdateStatus` (dòng 660–664) bắt buộc hợp đồng phải có `ChuKyNhanVien` mới cho phép duyệt giao máy (`status = 1`). Action `AdminSign` (dòng 1097–1170) đã lập trình sẵn sàng.
  - Frontend: `Areas/Admin/Views/HopDong/Details.cshtml` (dòng 286–294) chỉ hiển thị ảnh chữ ký hoặc dòng chữ tĩnh `<span class="text-muted fst-italic">Chưa ký</span>`. Toàn bộ file **hoàn toàn không có form, modal hoặc canvas vẽ chữ ký điện tử nào** để nhân viên Kinh Doanh ký tên!
- **Hệ quả thực tế**: Nhân viên Kinh Doanh khi bấm nút "Giao máy & Cho thuê" sẽ bị chặn vĩnh viễn bởi thông báo lỗi: *"Vui lòng hoàn tất Chữ ký nhân viên đối chiếu trước khi thực hiện bàn giao máy!"* mà không có công cụ nào trên màn hình để ký. Đây là điểm nghẽn nghiệp vụ nghiêm trọng khiến quy trình bị đứt gãy hoàn toàn trên giao diện.

### 6.5. Nhóm 5: Thiếu đồng bộ điều kiện hiển thị UI Guard (UI Guard Mismatch)
- **Vị trí mã nguồn**: `Areas/Admin/Views/BaoTri/Details.cshtml` dòng 195 và dòng 322; `Areas/Admin/Views/Shared/_AdminLayout.cshtml` dòng 33 và 44.
- **Thực trạng**:
  - Form `ThuPhiDenBu` (chỉ dành cho KD) không có `@if`, hiển thị cho cả KTV, bấm vào bị lỗi 403.
  - Form `UpdateStatus` (chỉ dành cho KT) không có `@if`, hiển thị cho cả KD, bấm vào bị lỗi 403.
  - Sidebar hiển thị thêm menu *Serial Máy* cho Kỹ thuật và *Bảo trì* cho Kinh Doanh, lệch so với đặc tả yêu cầu gốc tại `ORIGINAL_REQUEST.md` (R1).

### 6.6. Nhóm 6: Đứt gãy luồng vận hành thiết bị thực tế khi trả máy / thanh lý trước hạn
- **Vị trí mã nguồn**: `HopDongController.TraMayTruocHan` (dòng 1952) và `UpdateStatus` khi `status == 4` (dòng 762–814).
- **Thực trạng**: Khi nhân viên Kinh Doanh tại văn phòng bấm nút trả máy hoặc thanh lý trước hạn, hệ thống tự động cập nhật toàn bộ thiết bị về `TrangThai = 0: Sẵn sàng` và hoàn cọc cho khách.
- **Hệ quả rủi ro**: Máy vật lý chưa về tới kho, KTV chưa cắm điện kiểm tra xem có bị cháy mainboard hay tráo linh kiện hay không, nhưng trên website máy đã được đánh dấu "Sẵn sàng" cho khách hàng tiếp theo đặt thuê. Rủi ro thất thoát tài sản và tranh chấp chất lượng dịch vụ cực cao.

### 6.7. Nhóm 7: Khuyết thiếu phân hệ Quản lý Khách Hàng (CRM) độc lập cho Kinh Doanh
- **Vị trí mã nguồn**: `RentalSystem/Areas/Admin/Controllers/NguoiDungController.cs` dòng 11 (`[Authorize(Roles = "Admin")]`).
- **Thực trạng**: Phân hệ người dùng chứa cả tài khoản nhân viên nên bị khóa chỉ dành cho Super Admin. Kinh Doanh bị chặn hoàn toàn khỏi menu này.
- **Hệ quả rủi ro**: Kinh Doanh không có danh bạ khách hàng (Customer Directory/CRM), không tra cứu được lịch sử thuê tích lũy (Customer Lifetime Value - LTV), xếp hạng tín nhiệm, hay cập nhật thông tin liên hệ của khách hàng khi khách chưa tạo đơn mới.

### 6.8. Nhóm 8: Các lỗ hổng an ninh Web ứng dụng (CSRF và IDOR trong thanh toán)
- **Vị trí mã nguồn**:
  - `CongNoController.GuiNhacNo` (dòng 430) và `PhanCongController.UpdateStatus` (dòng 269): Phương thức `[HttpPost]` thay đổi trạng thái nhưng **thiếu thuộc tính `[ValidateAntiForgeryToken]`**.
  - `PaymentController.CreatePaymentUrl` (dòng 38): Action public **không có `[Authorize]`** và không kiểm tra quyền sở hữu hợp đồng `hopDong.MaKhachHang == currentUserId`. Kẻ xấu có thể quét ID hợp đồng để đọc thông tin nợ và tạo giao dịch thanh toán rác.

---

## PHẦN VII: KIẾN NGHỊ GIẢI PHÁP & LỘ TRÌNH CHUẨN HÓA

### 7.1. Kiến trúc phân quyền Policy-based Authorization chuẩn mực
Thay thế việc gắn cứng các chuỗi `[Authorize(Roles = "...")]` rải rác trong Controller bằng cơ chế **Policy-based Authorization** tập trung tại `RentalSystem/Program.cs`:

```csharp
builder.Services.AddAuthorization(options =>
{
    // 1. Phân hệ Kinh doanh & Quản lý Hợp đồng
    options.AddPolicy("SalesPolicy", policy => 
        policy.RequireRole("Admin", "KinhDoanh"));
        
    // 2. Phân hệ Kỹ thuật & Kho vận vật lý
    options.AddPolicy("TechPolicy", policy => 
        policy.RequireRole("Admin", "KyThuat"));
        
    // 3. Phân hệ Tác nghiệp Chung (Xem tiến độ & Chi tiết điều phối)
    options.AddPolicy("StaffSharedPolicy", policy => 
        policy.RequireRole("Admin", "KinhDoanh", "KyThuat"));
        
    // 4. Quyền Kiểm soát Tài chính Cốt lõi (Thu/Chi tiền, hoàn cọc, giảm trừ doanh thu)
    options.AddPolicy("FinancialControlPolicy", policy => 
        policy.RequireRole("Admin", "KinhDoanh"));
        
    // 5. Quản trị Hệ thống Tối cao
    options.AddPolicy("SuperAdminPolicy", policy => 
        policy.RequireRole("Admin"));
});
```

### 7.2. Chuẩn hóa quy trình bàn giao - thu hồi thiết bị 2 bước (2-Step Handover & Return)
Bịt kín lỗ hổng đứt gãy luồng vận hành thiết bị bằng quy trình 2 bước kiểm định vật lý:
1. **Quy trình Xuất kho Bàn giao (2 bước)**:
   - *Bước 1 (Kinh Doanh)*: Duyệt hợp đồng và ký số đối chiếu. Máy vẫn giữ ở trạng thái `3: Giữ chỗ`. Hệ thống tự động phát sinh nhiệm vụ xuất kho trên `PhanCongCongViec`.
   - *Bước 2 (Kỹ Thuật)*: KTV kiểm tra phần cứng, giao máy tận nơi và lập `BienBanBanGiao (Loai = 0)` kèm ảnh chụp thực địa. Khi biên bản được lưu, máy mới chính thức chuyển sang `1: Đang cho thuê`.
2. **Quy trình Thu hồi & Quyết toán Nhập kho (2 bước an toàn tài sản)**:
   - *Bước 1 (Kỹ Thuật)*: Khi nhận máy từ khách, KTV lập `BienBanBanGiao (Loai = 1)` ghi nhận hao mòn và cắm máy test lỗi. Thiết bị chuyển sang trạng thái trung gian `5: Chờ kiểm định kho` (thay vì tự động về 0). Nếu phát hiện hư hại, KTV tạo phiếu bảo trì đền bù.
   - *Bước 2 (Kinh Doanh)*: Căn cứ vào Biên bản thu hồi đã có xác nhận của KTV để thực hiện quyết toán nợ và hoàn cọc (`HoanCoc`).
   - *Bước 3 (Kỹ Thuật)*: KTV hoàn tất vệ sinh, cài lại Windows và test phần cứng, sau đó bấm "Xác nhận nhập kho" đưa máy về `0: Sẵn sàng`.

### 7.3. Tái cấu trúc thẩm quyền tài chính trong xử lý bảo trì & sự cố
1. **Khắc phục quyền giảm trừ tiền thuê (`ApDungTamDungTienThue`)**:
   - Tách biệt thành luồng 2 bước:
     - Kỹ thuật viên: Chỉ có quyền xác nhận "Số ngày thiết bị nằm xưởng sửa chữa" (`SoNgayTamDung`).
     - Kinh Doanh hoặc Quản lý: Có quyền phê duyệt áp dụng giảm trừ tiền vào hợp đồng.
2. **Khắc phục form thu phí bồi thường**:
   - Đồng bộ UI guard: Chỉ hiển thị form `ThuPhiDenBu` cho vai trò `Admin,KinhDoanh`.
   - Loại bỏ checkbox `thuPhiNgay` khỏi form `UpdateStatus` của kỹ thuật viên để bảo đảm KTV không gián tiếp sinh phiếu thu kế toán.

### 7.4. Thiết kế phân hệ CRM Khách Hàng độc lập (`/Admin/KhachHang`)
Xây dựng Controller mới `Areas/Admin/Controllers/KhachHangController.cs` phân quyền `[Authorize(Roles = "Admin,KinhDoanh")]`:
- Tra cứu danh bạ khách hàng, lọc theo nhóm nợ xấu, địa chỉ, mức độ chi tiêu.
- Xem chi tiết hồ sơ khách: Toàn bộ lịch sử các hợp đồng đã thuê, tổng doanh thu đã đóng góp (LTV), lịch sử thanh toán nợ, đánh giá tín nhiệm.
- Cập nhật số điện thoại, địa chỉ, CCCD của khách hàng độc lập với việc tạo đơn mới.

### 7.5. Khắc phục lỗi UI Disconnect chữ ký nhân viên trên `HopDong/Details.cshtml`
- Bổ sung Modal "Ký Biên Bản & Đối Chiếu Hợp Đồng" kèm HTML5 Signature Canvas trên giao diện `Areas/Admin/Views/HopDong/Details.cshtml`.
- Người dùng Kinh Doanh vẽ chữ ký trực tiếp trên màn hình cảm ứng hoặc chuột, bấm "Lưu Chữ Ký" để gọi action `AdminSign` đã có sẵn trong controller.
- Sau khi có chữ ký, nút "Giao máy & Cho thuê" kích hoạt bình thường, loại bỏ triệt để điểm nghẽn nghiệp vụ.

### 7.6. Đồng bộ hóa 100% UI Guards trên Razor Views và Sidebar Admin
1. **Trên `Areas/Admin/Views/BaoTri/Details.cshtml`**:
   - Bọc form `ThuPhiDenBu` trong `@if (User.IsInRole("Admin") || User.IsInRole("KinhDoanh"))`.
   - Bọc form `UpdateStatus` trong `@if (User.IsInRole("Admin") || User.IsInRole("KyThuat"))`.
2. **Trên `Areas/Admin/Views/ThietBi/Index.cshtml`**:
   - Ẩn nút "Xóa máy" đối với `KinhDoanh` và `KyThuat`, chỉ hiển thị cho `Admin`.
3. **Trên `Areas/Admin/Views/Shared/_AdminLayout.cshtml`**:
   - Ẩn menu `Bảo trì & Sự cố` đối với vai trò `KinhDoanh`.
   - Khóa quyền xóa trên giao diện Serial máy đối với nhân viên thường.
4. **Trên `Areas/Admin/Views/HopDong/Details.cshtml`**:
   - Ẩn các tab tài chính nhạy cảm (Sổ thu chi, Lịch sử nộp tiền, Nợ quá hạn) khi tài khoản đang đăng nhập có vai trò `KyThuat`.

### 7.7. Bịt kín các lỗ hổng bảo mật CSRF và IDOR
1. Bổ sung `[ValidateAntiForgeryToken]` cho:
   - `CongNoController.GuiNhacNo(int maKyHan)`
   - `PhanCongController.UpdateStatus(int id, int status, string? ghiChu)`
2. Bổ sung `[Authorize]` và kiểm tra quyền sở hữu hợp đồng trong `PaymentController.CreatePaymentUrl`:
   ```csharp
   if (!User.IsInRole("Admin") && !User.IsInRole("KinhDoanh") && hopDong.MaKhachHang != currentUserId)
   {
       return Forbid();
   }
   ```
3. Bổ sung thuộc tính `enctype="multipart/form-data"` và các thẻ `<input type="file">` trên Modal Lập Biên Bản Bàn Giao (`#modalLapBienBan`) để KTV tải ảnh minh chứng ngoại quan máy khi bàn giao/thu hồi.

### 7.8. Lộ trình triển khai khuyến nghị theo thứ tự ưu tiên (Roadmap)

```
GIAI ĐOẠN 1: KHẨN CẤP (Fix điểm nghẽn & Lỗ hổng an ninh tức thời)
├── 1. Bổ sung Canvas Ký số nhân viên trên HopDong/Details.cshtml (Khắc phục lỗi chặn duyệt đơn)
├── 2. Đồng bộ UI Guard trên BaoTri/Details.cshtml (Ẩn form thu tiền với KT, ẩn form cập nhật với KD)
├── 3. Thêm [ValidateAntiForgeryToken] cho GuiNhacNo và UpdateStatus (Phân công)
└── 4. Thêm [Authorize] & Kiểm tra sở hữu trên PaymentController.CreatePaymentUrl

GIAI ĐOẠN 2: CHUẨN HÓA VẬN HÀNH (Khắc phục SoD & An toàn tài sản)
├── 1. Khóa quyền xóa máy kho trên ThietBiController (Chỉ mở cho Admin)
├── 2. Tách thẩm quyền giảm tiền thuê ApDungTamDungTienThue (KTV đề xuất -> KD duyệt)
├── 3. Bổ sung upload ảnh hiện trạng trên Modal Lập Biên Bản Bàn Giao
└── 4. Ẩn thông tin tài chính/CCCD nhạy cảm trên HopDong/Details khi KTV xem

GIAI ĐOẠN 3: NÂNG TẦM HỆ THỐNG (Mở rộng tính năng & Kiến trúc bền vững)
├── 1. Xây dựng phân hệ CRM Khách Hàng chuyên biệt (/Admin/KhachHang) cho Kinh Doanh
├── 2. Triển khai quy trình Thu hồi Nhập kho 2 bước (Trạng thái trung gian Chờ kiểm định)
├── 3. Nâng cấp bảng cước linh hoạt (Gói ngày/tuần/tháng) và Voucher giảm tiền mặt tối đa
└── 4. Chuyển đổi toàn bộ hệ thống sang Policy-based Authorization tập trung
```

---

## KẾT LUẬN CHUNG

Hệ thống **RentalSystem** đã sở hữu một nền tảng kiến trúc nghiệp vụ rất ấn tượng, giải quyết thành công nhiều bài toán kỹ thuật phức tạp như kiểm soát tương tranh tồn kho đa luồng (`SemaphoreSlim InventoryLock`), quản lý phân kỳ nợ và đối soát ngân hàng tự động (Napas 247 VietQR, VNPay), cam kết chất lượng dịch vụ SLA sự cố, và báo cáo phân tích quản trị doanh nghiệp ClosedXML.

Tuy nhiên, sự phối hợp giữa hai vai trò **KinhDoanh** và **KyThuat** hiện tại vẫn còn tồn tại những ranh giới bị mờ nhạt và các điểm nghẽn giao diện (đặc biệt là vi phạm phân tách trách nhiệm tài chính SoD trong bảo trì, quyền xóa serial kho, đứt gãy luồng trả máy vật lý, và thiếu canvas ký số nhân viên). Việc thực hiện nghiêm túc các khuyến nghị trong bản báo cáo này sẽ đưa RentalSystem đạt chuẩn mực vận hành của một hệ thống ERP cho thuê thiết bị công nghệ chuyên nghiệp, an toàn và tối ưu trải nghiệm người dùng.

---
*(Báo cáo được hoàn lập và xác thực thực chứng trên mã nguồn hệ thống ngày 30/10/2026)*
