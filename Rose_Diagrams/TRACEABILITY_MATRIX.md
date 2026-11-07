# MA TRẬN TRUY VẾT HỆ THỐNG RENTALSYSTEM (MASTER TRACEABILITY MATRIX)
## Chuẩn Hóa Theo Phương Pháp Luận RUP (Rational Unified Process) & Quy Chuẩn Khóa Luận HUIT 2025

- **Tên dự án**: RentalSystem - Hệ thống cho thuê thiết bị công nghệ & văn phòng theo cấu hình Serial
- **Môi trường mô hình hóa**: IBM Rational Rose 2003 / 98 Enterprise Edition (Win32)
- **Định dạng mô hình**: Petal (.mdl) Version 47, charSet 0 (ANSI Windows-1252)
- **Quy chuẩn định danh**: 100% Tiếng Việt không dấu (Pure ASCII)
- **Tài liệu nguồn căn cứ**: `D:\DoAnCuNhan\KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025_USER_SAVED.docx`

---

## MỤC LỤC
1. [Nguyên Tắc Phương Pháp Luận & Phân Định Ranh Giới Hệ Thống](#1-nguyên-tắc-phương-pháp-luận--phân-định-ranh-giới-hệ-thống)
2. [Hệ Phân Loại RUP: Tác Nhân Ngoại Vi (Actors) & Nhân Sự Nghiệp Vụ (Workers)](#2-hệ-phân-loại-rup-tác-nhân-ngoại-vi-actors--nhân-sự-nghiệp-vụ-workers)
3. [Ma Trận Truy Vết Toàn Diện 100% (Master Traceability Matrix)](#3-ma-trận-truy-vết-toàn-diện-100-master-traceability-matrix)
4. [Đặc Tả Quy Trình Xử Lý 4 Ca Biên Nghiệp Vụ Trọng Yếu](#4-đặc-tả-quy-trình-xử-lý-4-ca-biên-nghiệp-vụ-trọng-yếu)
   - [4.1. Ca biên 1: Khách không nhận máy (Delivery Rejection / No-Show)](#41-ca-biên-1-khách-không-nhận-máy-delivery-rejection--no-show)
   - [4.2. Ca biên 2: Cọc thiếu (Insufficient Deposit Settlement)](#42-ca-biên-2-cọc-thiếu-insufficient-deposit-settlement)
   - [4.3. Ca biên 3: Đền bù hỏng máy (Equipment Damage & Penalty Settlement)](#43-ca-biên-3-đền-bù-hỏng-máy-equipment-damage--penalty-settlement)
   - [4.4. Ca biên 4: Trễ hạn không trả máy (Overdue Machine Retention)](#44-ca-biên-4-trễ-hạn-không-trả-máy-overdue-machine-retention)
5. [Phân Rã Phân Hệ Ca Sử Dụng Hệ Thống (3 Subsystems & 14 Use Cases)](#5-phân-rã-phân-hệ-ca-sử-dụng-hệ-thống-3-subsystems--14-use-cases)
6. [Từ Điển Danh Pháp Tiếng Việt Không Dấu (Unaccented Naming Dictionary)](#6-từ-điển-danh-pháp-tiếng-việt-không-dấu-unaccented-naming-dictionary)
7. [Quy Chuẩn Cú Pháp Petal & Chỉ Dẫn Kỹ Thuật Cho IBM Rational Rose](#7-quy-chuẩn-cú-pháp-petal--chỉ-dẫn-kỹ-thuật-cho-ibm-rational-rose)

---

## 1. NGUYÊN TẮC PHƯƠNG PHÁP LUẬN & PHÂN ĐỊNH RANH GIỚI HỆ THỐNG

### 1.1. Ranh giới Doanh nghiệp vs Ranh giới Phần mềm
Theo phương pháp luận RUP (Ivar Jacobson, Grady Booch, James Rumbaugh):
- **Mô hình nghiệp vụ (Business Modeling - Chương 2)**: Mô phỏng toàn bộ tổ chức doanh nghiệp cho thuê thiết bị.
  - Tác nhân nghiệp vụ ngoại vi (`Business Actor`): Nằm **ngoài** doanh nghiệp (`Khach hang`, `Ngan hang / Cong VietQR`).
  - Nhân sự nghiệp vụ nội bộ (`Business Worker`): Là nhân viên làm việc **trong** doanh nghiệp (`Nhan vien kinh doanh`, `Ky thuat vien`, `Quan tri vien`).
- **Mô hình phần mềm (System Modeling - Chương 3)**: Mô phỏng hệ thống ứng dụng ASP.NET Core 9 MVC.
  - Cả khách hàng bên ngoài lẫn nhân viên nội bộ đều là **Tác nhân hệ thống (`System Actor`)** tương tác với giao diện (`Boundary`).

### 1.2. Phản biện và loại bỏ triệt để các thành phần kỹ thuật khỏi vai trò Actor
- **Lỗi sai trong bản thảo Word**: Các bảng đặc tả và sơ đồ tuần tự tại Mục 2.2.2 đã đưa `SemaphoreSlim`, `Webhook`, `Hangfire`, `DebtCalculationHelper` vào làm Actor.
- **Khẳng định nguyên lý**:
  - `SemaphoreSlim`: Là cơ chế đồng bộ hóa luồng bộ nhớ trong tiến trình C#, thuộc tầng điều khiển (`Control Class`), **tuyệt đối không phải là Actor**.
  - `Webhook`: Là giao thức truyền tin HTTP POST callback giữa máy chủ ngân hàng và máy chủ web, đóng vai trò phương thức/endpoint tiếp nhận của tầng điều khiển.
  - `Hangfire / BackgroundService`: Là dịch vụ ngầm (Background Worker Service) thuộc tầng nghiệp vụ hệ thống.
  - `DebtCalculationHelper`: Là lớp thuật toán xử lý nghiệp vụ tài chính (Algorithmic Service).
- **Quy tắc bất biến**: 100% các thành phần kỹ thuật trên được quy hoạch chính xác vào tầng **Control (Lớp điều khiển)** hoặc **Business Logic (Lớp dịch vụ)**, loại bỏ hoàn toàn khỏi vai trò Actor/Worker trên mọi sơ đồ.

---

## 2. HỆ PHÂN LOẠI RUP: TÁC NHÂN NGOẠI VI (ACTORS) & NHÂN SỰ NGHIỆP VỤ (WORKERS)

```
+-----------------------------------------------------------------------------------------+
|                              RANH GIỚI DOANH NGHIỆP RENTALSYSTEM                        |
|                                                                                         |
|   +---------------------------------------------------------------------------------+   |
|   |                         RANH GIỚI HỆ THỐNG PHẦN MỀM (SOFTWARE)                  |   |
|   |                                                                                 |   |
|   |     <<boundary>>                     <<control>>                   <<entity>>   |   |
|   |   +---------------+              +-----------------+           +------------+   |   |
|   |   | Views / Forms | <----------> |   Controllers   | <-------> | DbContext  |   |   |
|   |   +---------------+              | Services/Engines|           |  Entities  |   |   |
|   |                                  +-----------------+           +------------+   |   |
|   +---------------------------------------------------------------------------------+   |
|           ^                                   ^                             ^           |
|           | Tương tác giao diện               | Phân công xử lý             | Truy vấn  |
|           v                                   v                             v           |
|   +---------------------------------------------------------------------------------+   |
|   |                    NHÂN SỰ NGHIỆP VỤ NỘI BỘ (BUSINESS WORKERS)                  |   |
|   |   - Nhan vien kinh doanh: Quản lý hợp đồng, thẩm định KYC, nhắc nợ, hoàn cọc    |   |
|   |   - Ky thuat vien: Xuất kho, quét serial, bàn giao tận nơi, bảo trì, nghiệm thu |   |
|   |   - Quan tri vien: Phân quyền, cấu hình danh mục/chính sách, giám sát BI        |   |
|   +---------------------------------------------------------------------------------+   |
+-----------------------------------------------------------------------------------------+
        ^                                                                     ^
        | Giao dịch, duyệt web, ký hợp đồng                                   | IPN / Webhook
        v                                                                     v
+-----------------------------------------------------------------------------------------+
|                       TÁC NHÂN NGHIỆP VỤ NGOẠI VI (BUSINESS ACTORS)                     |
|   - Khach hang: Khách cá nhân hoặc đại diện doanh nghiệp thuê thiết bị                  |
|   - Ngan hang / Cong VietQR: Ngân hàng MBBank, Cổng thanh toán NAPAS 247, SePay/Casso  |
+-----------------------------------------------------------------------------------------+
```

---

## 3. MA TRẬN TRUY VẾT TOÀN DIỆN 100% (MASTER TRACEABILITY MATRIX)

Ma trận dưới đây liên kết 100% xuyên suốt 6 tầng mô hình:
**BUC (Ca sử dụng nghiệp vụ) $\rightarrow$ Activity (Hoạt động) $\rightarrow$ Sequence / Collab (Tuần tự / Cộng tác) $\rightarrow$ SUC (Ca sử dụng hệ thống) $\rightarrow$ Analysis BCE (Lớp phân tích) $\rightarrow$ Design 3-Tier (Lớp thiết kế 3 tầng)**.

| BUC ID & Tên quy trình | Business Activity Diagram | Business Sequence / Collab Diagram | System Use Case (SUC) & Phân hệ | Analysis BCE Classes (Boundary, Control, Entity) | Design 3-Tier Classes (Presentation, Business, Data) |
|---|---|---|---|---|---|
| **BUC-01**<br>Dang ky & Xac thuc nguoi dung | **AD-01**<br>Nhập thông tin $\rightarrow$ Kiểm tra trùng Email/CCCD $\rightarrow$ Băm mật khẩu BCrypt $\rightarrow$ Phân quyền vai trò $\rightarrow$ Cấp Cookie Claims | **SD-01** / **CD-01**<br>Khach hang $\rightarrow$ Dang ky form $\rightarrow$ He thong $\rightarrow$ Luu thong tin tai khoan $\rightarrow$ Thong bao thanh cong | **UC-01**: Dang ky tai khoan<br>**UC-02**: Dang nhap & Phan quyen<br>*(Customer Portal & Admin)* | **B**: `DangKyView`, `DangNhapView`, `ProfileView`<br>**C**: `AccountControl`<br>**E**: `NguoiDung`, `VaiTro`, `ThongBao` | **Presentation**: `AccountController`, `RegisterViewModel`, `LoginViewModel`<br>**Business**: `CookieAuthenticationHandler`, `PasswordHasher`<br>**Data**: `ApplicationDbContext`, `NguoiDung`, `VaiTro` |
| **BUC-02**<br>Dat thue may & Kiem tra ton kho | **AD-02**<br>Duyệt máy $\rightarrow$ Chọn ngày thuê $\rightarrow$ Kích hoạt SemaphoreLock $\rightarrow$ Kiểm tra lịch khả dụng serial $\rightarrow$ Giữ chỗ 24h $\rightarrow$ Giải phóng Semaphore | **SD-02** / **CD-02**<br>Khach hang $\rightarrow$ Gio hang $\rightarrow$ Kiem tra ton kho $\rightarrow$ Tao don thue giu cho serial | **UC-03**: Dat thue thiet bi truc tuyen<br>*(Customer Portal)*<br>*(Ngoại lệ: Hết máy, Trùng lịch)* | **B**: `GioHangView`, `DatThueView`, `ThongBaoModal`<br>**C**: `CartControl`<br>**E**: `SanPham`, `ThietBi`, `HopDong`, `ChiTietHopDong` | **Presentation**: `CartController`, `CheckoutViewModel`<br>**Business**: `CartController.InventoryLock (SemaphoreSlim)`, `ReservationCleanupService`<br>**Data**: `SanPham`, `ThietBi`, `HopDong`, `ChiTietHopDong` |
| **BUC-03**<br>Thanh toan dat coc qua VietQR dong | **AD-03**<br>Tạo mã QR chuẩn EMVCo $\rightarrow$ Quét thanh toán NAPAS 247 $\rightarrow$ Webhook tiếp nhận $\rightarrow$ Mở PaymentLock $\rightarrow$ Gạch nợ $\rightarrow$ Sinh PhieuThu | **SD-03** / **CD-03**<br>Khach hang $\rightarrow$ Ngan hang / Cong VietQR $\rightarrow$ He thong $\rightarrow$ Cap nhat TienDaCoc $\rightarrow$ Xac nhan don | **UC-05**: Thanh toan VietQR & Doi soat Webhook<br>*(Customer Portal & Admin)*<br>*(Ngoại lệ: Coc thieu, Chuyen thua)* | **B**: `ThanhToanView`, `VietQRModalView`, `XacNhanThanhToanView`<br>**C**: `PaymentControl`<br>**E**: `HopDong`, `KyHanThanhToan`, `PhieuThu`, `ThongBao` | **Presentation**: `PaymentController`, `BankingWebhookModel`<br>**Business**: `VnPayService`, `HopDongController.PaymentLock (SemaphoreSlim)`, `VietQREngine`<br>**Data**: `PhieuThu`, `KyHanThanhToan`, `HopDong`, `ThongBao` |
| **BUC-04**<br>Ban giao & Ky bien ban ban giao may | **AD-04**<br>KTV quét barcode serial $\rightarrow$ Xuất kho $\rightarrow$ Vận chuyển tận nơi $\rightarrow$ Đồng kiểm cấu hình $\rightarrow$ Ký số Canvas HTML5 $\rightarrow$ Xuất PDF | **SD-04** / **CD-04**<br>Ky thuat vien $\rightarrow$ Giao dien ban giao $\rightarrow$ Khach hang dong kiem $\rightarrow$ Ky Canvas $\rightarrow$ Cap nhat may Dang thue | **UC-04**: Ky hop dong Canvas & Tai CCCD<br>**UC-06**: Ban giao & Xuat bien ban<br>*(Maintenance & Technical)*<br>*(Ngoại lệ: Khach khong nhan may)* | **B**: `BanGiaoView`, `KyCanvasModalView`, `BienBanView`<br>**C**: `HopDongControl`<br>**E**: `BienBanBanGiao`, `ThietBi`, `HopDong`, `LichSuThietBi` | **Presentation**: `HopDongController`, `DocumentController`, `BanGiaoViewModel`<br>**Business**: `MagicBytesValidator`, `PdfExportService`<br>**Data**: `BienBanBanGiao`, `ThietBi`, `HopDong`, `LichSuThietBi` |
| **BUC-05**<br>Bao cao su co & Phan cong bao tri | **AD-05**<br>Khách tạo ticket kèm ảnh $\rightarrow$ Admin điều phối phân công $\rightarrow$ KTV tiếp nhận $\rightarrow$ Tạm dừng tính tiền nếu >24h $\rightarrow$ Sửa/Đổi máy $\rightarrow$ Nghiệm thu | **SD-05** / **CD-05**<br>Khach hang $\rightarrow$ Gui ticket $\rightarrow$ Quan tri vien phan cong $\rightarrow$ Ky thuat vien xu ly $\rightarrow$ Dong phieu | **UC-07**: Bao cao su co & Tam dung SLA<br>**UC-08**: Dieu phoi ky thuat & Quan ly viec<br>*(Maintenance & Technical)*<br>*(Ngoại lệ: Den bu hong do khach)* | **B**: `SuCoTicketView`, `PhanCongBaoTriView`, `MyTasksView`<br>**C**: `BaoTriControl`, `PhanCongControl`<br>**E**: `PhieuBaoTri`, `PhanCongCongViec`, `ThietBi`, `HopDong` | **Presentation**: `BaoTriController`, `PhanCongController`, `TicketViewModel`<br>**Business**: `MaintenanceDispatcherService`, `SLATimerService`<br>**Data**: `PhieuBaoTri`, `PhanCongCongViec`, `ThietBi`, `HopDong` |
| **BUC-06**<br>Gia han hop dong & Phan ky no | **AD-06**<br>Khách chọn ngày gia hạn $\rightarrow$ Kiểm tra không xung đột đơn kế tiếp $\rightarrow$ Kinh doanh duyệt $\rightarrow$ Phân kỳ nợ trả góp bổ sung $\rightarrow$ Sinh lịch VietQR | **SD-06** / **CD-06**<br>Khach hang $\rightarrow$ Yeu cau gia han $\rightarrow$ Nhan vien kinh doanh duyet $\rightarrow$ He thong tao ky han no moi | **UC-09**: Yeu cau & Phe duyet gia han<br>**UC-11**: Quan ly so no & Nhac no 4 cap<br>*(Admin & Operations)*<br>*(Ngoại lệ: Tre han khong tra, Phat 0.1%)* | **B**: `GiaHanView`, `SoCongNoView`, `LichSuNhacNoView`<br>**C**: `HopDongControl`, `CongNoControl`<br>**E**: `YeuCauGiaHan`, `HopDong`, `KyHanThanhToan`, `LichSuNhacNo` | **Presentation**: `HopDongController`, `CongNoController`, `GiaHanViewModel`<br>**Business**: `DebtCalculationHelper`, `AutoDebtReminderService`<br>**Data**: `YeuCauGiaHan`, `HopDong`, `KyHanThanhToan`, `LichSuNhacNo` |
| **BUC-07**<br>Tra may, nghiem thu & Hoan coc | **AD-07**<br>KTV kiểm tra máy thu hồi $\rightarrow$ Thẩm định hư hại $\rightarrow$ Lập biên bản nghiệm thu $\rightarrow$ Cấn trừ nợ thuê & bồi thường $\rightarrow$ Lập PhieuChi hoàn cọc dư | **SD-07** / **CD-07**<br>Ky thuat vien $\rightarrow$ Nghiem thu thu hoi $\rightarrow$ Nhan vien kinh doanh quyet toan $\rightarrow$ Lap phieu chi hoan coc | **UC-10**: Nghiem thu tra may & Hoan coc<br>*(Admin & Operations)*<br>*(Ngoại lệ: Den bu hong, Coc thieu, Mat may)* | **B**: `NghiemThuView`, `QuyetToanHoanCocView`, `PhieuChiModal`<br>**C**: `HopDongControl`<br>**E**: `BienBanBanGiao`, `HopDong`, `PhieuChi`, `PhieuThu`, `ThietBi` | **Presentation**: `HopDongController` (NghiemThu, HoanCoc, TraMayTruocHan)<br>**Business**: `DebtCalculationHelper.CalculateDepositSettlement`<br>**Data**: `BienBanBanGiao`, `PhieuChi`, `PhieuThu`, `HopDong`, `ThietBi` |

---

## 4. ĐẶC TẢ QUY TRÌNH XỬ LÝ 4 CA BIÊN NGHIỆP VỤ TRỌNG YẾU

### 4.1. Ca biên 1: Khách không nhận máy (Delivery Rejection / No-Show)
- **Tình huống phát sinh**: Đơn thuê đã duyệt, tiền cọc đã đóng đủ, máy đang ở trạng thái `3 (Giu cho)`. Kỹ thuật viên vận chuyển thiết bị đến địa điểm bàn giao nhưng việc bàn giao không thành công.
- **Phân loại nguyên nhân**:
  1. *Nguyên nhân 1A (Khách đơn phương từ chối)*: Khách đổi ý, không có nhu cầu thuê nữa hoặc từ chối ký biên bản giao nhận.
  2. *Nguyên nhân 1B (Không liên lạc được)*: KTV đến điểm giao, gọi điện 3 lần (cách nhau 15 phút) nhưng khách tắt máy / không nghe máy / sai địa chỉ.
  3. *Nguyên nhân 1C (Lỗi từ bên cho thuê)*: Thiết bị giao đến không đúng cấu hình cam kết, trầy xước nặng ngoài thỏa thuận và khách không đồng ý đổi máy dự phòng.
- **Quy trình chuẩn (Standard Operating Procedure - SOP)**:
  ```
  [KTV Giao máy] ---> [Khách không nhận]
                            |
           +----------------+----------------+
           |                                 |
   [Lỗi bên cho thuê (1C)]          [Khách từ chối/Không nghe (1A, 1B)]
           |                                 |
   - Hoàn kho máy: TrangThai = 0    - Hoàn kho máy: TrangThai = 0
   - Hợp đồng: TrangThai = 3        - Hợp đồng: TrangThai = 3
   - Hoàn 100% Cọc & Tiền thuê      - Khấu trừ phí vận chuyển (vd: 150.000đ)
   - Lập PhieuChi: 100%             - Lập PhieuChi hoàn phần cọc còn lại
  ```
- **Tác động trạng thái dữ liệu**:
  - `ThietBi.TrangThai`: Chuyển từ `3 (Giu cho)` $\rightarrow$ `0 (San sang)`.
  - `LichSuThietBi`: Ghi bản ghi: *"Hoàn kho do giao máy không thành công: [Lý do]"*.
  - `HopDong.TrangThai`: Chuyển sang `3 (Da huy)`. `YeuCauHuy = true`, `LyDoHuy = [Chi tiết lý do]`.
  - `HopDong.TrangThaiHoanCoc`: Đặt `1 (Da hoan coc)`. Sinh `PhieuChi` với số tiền hoàn tương ứng.

---

### 4.2. Ca biên 2: Cọc thiếu (Insufficient Deposit Settlement)
- **Tình huống phát sinh**: Khách hàng quét mã VietQR nhưng chỉnh sửa giảm số tiền chuyển khoản, dẫn đến số tiền thực nhận nhỏ hơn số tiền cọc quy định (`transferAmount < TienCocBaoDamMay`).
- **Quy trình chuẩn (SOP)**:
  ```
  [Webhook nhận tiền cọc] ---> [Kiểm tra: transferAmount < TienCocBaoDamMay]
                                             |
                                 - Sinh PhieuThu (LoaiPhieu = 1)
                                 - HopDong.TienDaCoc += transferAmount
                                 - Giữ HopDong.TrangThai = 0 (Chờ cọc đủ)
                                 - HopDong.TrangThaiThanhToan = 1 (Thanh toán 1 phần)
                                 - Gửi thông báo nhắc cọc trước hạn HanChotKy (24h)
                                             |
                         +-------------------+-------------------+
                         |                                       |
                 [Nộp đủ trước 24h]                      [Quá hạn 24h không nộp]
                         |                                       |
           - Nhận tiếp Webhook lần 2             - BackgroundService quét quá hạn
           - Tổng cọc >= TienCocBaoDamMay        - Giải phóng máy: TrangThai = 0
           - HopDong.TrangThai = 1 (Đã cọc)      - HopDong.TrangThai = 3 (Đã hủy)
           - Chuyển KTV xuất kho giao máy        - Lập PhieuChi hoàn tiền cọc dở dang
  ```
- **Tác động trạng thái dữ liệu**:
  - `PhieuThu`: Tạo phiếu thu cọc dở dang (`LoaiPhieu = 1, HinhThucThanhToan = 1, MaNhanVienThu = null`).
  - `HopDong`: Giữ nguyên `TrangThai = 0`, ngăn chặn việc xuất kho bàn giao trái phép.
  - `ReservationCleanupService`: Tác vụ nền tự động giải phóng serial nếu quá 24h không nộp đủ.

---

### 4.3. Ca biên 3: Đền bù hỏng máy (Equipment Damage & Penalty Settlement)
- **Tình huống phát sinh**: Thiết bị khi thu hồi hoặc trong kỳ thuê bị hỏng hóc vật lý (vỡ màn hình, cháy nổ mainboard, cấn móp, mất linh kiện) do lỗi người dùng.
- **Giải thuật quyết toán tài chính (Căn cứ `DebtCalculationHelper.CalculateDepositSettlement`)**:
  $$\text{unpaidDamages} = \sum \text{PhiDenBu} - \sum \text{PhieuThu}_{\text{Loai 2}}$$
  $$\text{tienCoc} = \text{TienCocBaoDamMay} > 0 \ ? \ \text{TienCocBaoDamMay} : \text{TienDaCoc}$$
  $$\text{refund} = \text{tienCoc} - \text{unpaidRent} - \text{unpaidDamages}$$
- **Phân nhánh xử lý**:
  ```
  [KTV Thẩm định hư hại] ---> Lập PhieuBaoTri (Ghi nhận PhiDenBu)
                                        |
                 +----------------------+----------------------+
                 |                                             |
         [refund >= 0: Cọc đủ bù]                     [refund < 0: Cọc thiếu bù]
                 |                                             |
   - Sinh PhieuThu (Loai 2: Đền bù,              - Tịch thu toàn bộ tiền cọc:
     HinhThuc 2: Cấn trừ cọc)                      TrangThaiHoanCoc = 2 (Cấn trừ toàn bộ)
   - Nếu refund > 0: Sinh PhieuChi               - Thâm hụt |refund| ghi nhận nợ bồi thường
     hoàn cọc dư, TrangThaiHoanCoc = 1           - Kích hoạt IsCustomerBlacklisted = true
   - Nếu refund == 0: TrangThaiHoanCoc = 2       - Sinh VietQR truy thu phần còn thiếu
   - Máy: TrangThai = 2 (Sửa) hoặc 4 (Thanh lý)  - Nếu bất hợp tác: Khởi kiện pháp lý
  ```

---

### 4.4. Ca biên 4: Trễ hạn không trả máy (Overdue Machine Retention)
- **Tình huống phát sinh**: Hợp đồng đã quá `NgayKetThuc`, hợp đồng vẫn đang hiệu lực (`TrangThai = 1`), khách hàng không mang máy đến trả và không có đơn xin gia hạn hợp lệ.
- **Quy trình thực thi 4 giai đoạn nghiêm ngặt**:
  1. **Giai đoạn 1: Ân hạn tự động (Ngày 1 - 3 sau hạn)**:
     - Áp dụng `daysPastDue <= 3 => LateFee = 0`.
     - Hệ thống tự động gửi thông báo / SMS nhắc nhở vào Ngày 1 và Ngày 3.
     - Lưu vết vào `LichSuNhacNo`.
  2. **Giai đoạn 2: Tính phạt quá hạn & Thu hồi thương mại (Ngày 4 - 15 sau hạn - Nhóm nợ 1)**:
     - Kích hoạt tính tiền phạt trễ hạn tự động:
       $$\text{PhiPhat} = \text{unpaidAmount} \times 0.001 \times \text{daysPastDue} \quad (0.1\%/\text{ngày})$$
     - Cộng dồn tiền thuê phát sinh theo đơn giá ngày thực tế.
     - Nhân viên kinh doanh gọi điện thoại trực tiếp đôn đốc khách trả máy.
  3. **Giai đoạn 3: Khóa quyền thuê & Cảnh báo pháp lý (Ngày 16 - 30 sau hạn - Nhóm nợ 2)**:
     - Kích hoạt `IsCustomerBlacklisted = true`.
     - Khóa tài khoản: Chặn thêm máy vào giỏ, chặn tạo hợp đồng mới.
     - Gửi văn bản khuyến cáo vi phạm hợp đồng đến địa chỉ thường trú trên CCCD.
  4. **Giai đoạn 4: Đơn phương thanh lý & Khởi kiện hình sự (> 30 ngày sau hạn - Nhóm nợ 3 & 4)**:
     - Tịch thu toàn bộ tiền cọc bảo đảm máy: `TrangThaiHoanCoc = 2`.
     - Giá trị còn lại của thiết bị chuyển thành khoản nợ chiếm đoạt tài sản phải thu hồi.
     - Kích hoạt khóa máy từ xa (MDM).
     - Trích xuất toàn bộ hồ sơ điện tử (ảnh CCCD 2 mặt, chữ ký Canvas HTML5, biên bản giao nhận có ảnh) chuyển cơ quan công an / tòa án nhân dân khởi kiện tội Lạm dụng tín nhiệm chiếm đoạt tài sản.

---

## 5. PHÂN RÃ PHÂN HỆ CA SỬ DỤNG HỆ THỐNG (3 SUBSYSTEMS & 14 USE CASES)

Toàn bộ hệ thống được phân rã thành **3 phân hệ chuẩn hóa**:

```
                                  +-------------------------------------+
                                  | RENTALSYSTEM SYSTEM USE CASE MODEL  |
                                  +-------------------------------------+
                                                     |
         +-------------------------------------------+------------------------------------------+
         |                                           |                                          |
         v                                           v                                          v
+-------------------------------+   +---------------------------------+   +---------------------------------+
| PHÂN HỆ KHÁCH HÀNG            |   | PHÂN HỆ QUẢN TRỊ & VẬN HÀNH     |   | PHÂN HỆ BẢO TRÌ & KỸ THUẬT      |
| (Customer Portal Subsystem)   |   | (Admin & Operations Subsystem)  |   | (Maintenance & Technical Sub.)  |
+-------------------------------+   +---------------------------------+   +---------------------------------+
| UC-01: Đăng ký tài khoản      |   | UC-02: Đăng nhập & Phân quyền   |   | UC-02: Đăng nhập & Phân quyền   |
| UC-02: Đăng nhập & Phân quyền |   | UC-05: Đối soát Webhook số dư   |   | UC-06: Bàn giao & Biên bản      |
| UC-03: Đặt thuê máy online    |   | UC-09: Duyệt gia hạn hợp đồng   |   | UC-07: Tiếp nhận lỗi & SLA      |
| UC-04: Ký Canvas & CCCD       |   | UC-10: Nghiệm thu & Hoàn cọc    |   | UC-08: Điều phối & Việc của tôi |
| UC-05: Thanh toán VietQR      |   | UC-11: Quản lý nợ & Nhắc nợ     |   | UC-10: Nghiệm thu tem thiết bị  |
| UC-07: Báo sự cố & Tạm dừng   |   | UC-12: Báo cáo phân tích BI     |   +---------------------------------+
| UC-09: Yêu cầu gia hạn HĐ     |   +---------------------------------+
| UC-13: Đánh giá dịch vụ KTV   |
+-------------------------------+
```

### Danh mục 14 Ca sử dụng hệ thống tổng quát (`SYS-UC01` đến `SYS-UC14`):
1. `SYS-UC01`: Dang ky & Xac thuc tai khoan (Khach hang, Admin)
2. `SYS-UC02`: Dat thue & Giu cho may Serial (Khach hang)
3. `SYS-UC03`: Ky so hop dong Canvas HTML5 & CCCD (Khach hang)
4. `SYS-UC04`: Theo doi lich no ca nhan MyDebt (Khach hang)
5. `SYS-UC05`: Tham dinh & Duyet hop dong thue (Nhan vien kinh doanh)
6. `SYS-UC06`: Quan ly thiet bi Serial & Danh muc kho (Quan tri vien, Ky thuat vien)
7. `SYS-UC07`: Quan tri phan quyen nguoi dung RBAC (Quan tri vien)
8. `SYS-UC08`: Giam sat cong no & Tuoi no 4 cap (Nhan vien kinh doanh, Quan tri vien)
9. `SYS-UC09`: Xuat kho ban giao & Quet Barcode (Ky thuat vien)
10. `SYS-UC10`: Tiep nhan & Xu ly su co theo SLA (Ky thuat vien, Khach hang)
11. `SYS-UC11`: Thu hoi, nghiem thu & Doi may (Ky thuat vien)
12. `SYS-UC12`: Thanh toan dat coc VietQR dong NAPAS 247 (Khach hang, Ngan hang)
13. `SYS-UC13`: Doi soat tu dong Banking Webhook (Ngan hang, He thong)
14. `SYS-UC14`: Lap phieu chi hoan tien coc (Nhan vien kinh doanh)

---

## 6. TỪ ĐIỂN DANH PHÁP TIẾNG VIỆT KHÔNG DẤU (UNACCENTED NAMING DICTIONARY)

Toàn bộ danh xưng trong file Petal (.mdl) và RoseScript (.ebs) bắt buộc sử dụng bảng danh pháp chuẩn dưới đây để tương thích 100% với IBM Rational Rose Win32 (ANSI):

### 6.1. Tác nhân & Nhân sự (Actors & Workers)
| Tên có dấu (Tiếng Việt) | Tên không dấu (Rose ID) | Phân loại RUP (Stereotype) |
|---|---|---|
| Khách hàng | `Khach hang` | `<<business actor>>` / System Actor |
| Ngân hàng / Cổng VietQR | `Ngan hang / Cong VietQR` | `<<business actor>>` / System Actor |
| Nhân viên kinh doanh | `Nhan vien kinh doanh` | `<<business worker>>` / System Actor |
| Kỹ thuật viên | `Ky thuat vien` | `<<business worker>>` / System Actor |
| Quản trị viên | `Quan tri vien` | `<<business worker>>` / System Actor |

### 6.2. Ca sử dụng nghiệp vụ (Business Use Cases - BUCs)
| Mã | Tên không dấu (Rose ID) | Mục tiêu nghiệp vụ |
|---|---|---|
| `BUC-01` | `Dang ky & Xac thuc nguoi dung` | Đăng ký hồ sơ định danh KYC, băm mật khẩu, cấp quyền |
| `BUC-02` | `Dat thue may & Kiem tra ton kho` | Chọn máy, kích hoạt khóa chống race condition, giữ chỗ serial |
| `BUC-03` | `Thanh toan dat coc qua VietQR dong` | Sinh mã VietQR NAPAS 247, gạch nợ tự động qua Webhook |
| `BUC-04` | `Ban giao & Ky bien ban ban giao may` | Quét serial xuất kho, giao tận nơi, ký Canvas HTML5, xuất PDF |
| `BUC-05` | `Bao cao su co & Phan cong bao tri thiet bi` | Tiếp nhận lỗi ticket, điều phối KTV, kích hoạt SLA dừng tính tiền |
| `BUC-06` | `Gia han hop dong & Phan ky no` | Đề xuất gia hạn, kiểm tra lịch trống, chia kỳ trả góp bổ sung |
| `BUC-07` | `Tra may, nghiem thu & Hoan tra tien coc` | Thu hồi máy, giám định hư hại, cấn trừ công nợ, chi hoàn cọc |

### 6.3. Lớp phân tích BCE (Boundary, Control, Entity)
- **Boundary Classes (`<<boundary>>`)**:
  - `DangKyView`, `DangNhapView`, `GioHangView`, `DatThueView`, `ThanhToanView`, `VietQRModalView`, `BanGiaoView`, `KyCanvasModalView`, `SuCoTicketView`, `PhanCongBaoTriView`, `GiaHanView`, `SoCongNoView`, `NghiemThuView`, `HoanCocView`, `BaoCaoBIView`.
- **Control Classes (`<<control>>`)**:
  - `AccountControl`: Xử lý đăng ký, đăng nhập, xác minh claims, băm BCrypt.
  - `CartControl`: Điều phối giỏ hàng, gọi khóa `InventoryLock (SemaphoreSlim)`, giữ chỗ máy.
  - `PaymentControl`: Tiếp nhận IPN/Webhook, gọi khóa `PaymentLock (SemaphoreSlim)`, gạch nợ tự động.
  - `HopDongControl`: Lập hợp đồng, quản lý chữ ký số Canvas, duyệt hợp đồng, quyết toán hoàn cọc.
  - `BaoTriControl`: Tiếp nhận ticket hỏng máy, kích hoạt SLA tạm dừng tính tiền, cập nhật trạng thái sửa chữa.
  - `PhanCongControl`: Điều phối việc từ Admin/Kinh doanh sang Kỹ thuật viên.
  - `CongNoControl`: Tính toán tuổi nợ 4 cấp, tính tiền phạt trễ hạn 0.1%/ngày, lập báo cáo Excel.
- **Entity Classes (`<<entity>>`)**:
  - `NguoiDung`, `VaiTro`, `SanPham`, `LoaiThietBi`, `ThietBi`, `LichSuThietBi`, `HopDong`, `ChiTietHopDong`, `KyHanThanhToan`, `BienBanBanGiao`, `PhieuThu`, `PhieuChi`, `PhieuBaoTri`, `PhanCongCongViec`, `YeuCauGiaHan`, `LichSuNhacNo`, `ThongBao`, `KhuyenMai`.

### 6.4. Thông điệp Tuần tự / Cộng tác (Messages Dictionary)
- `1: NhapThongTinDangKy(hoTen, email, sdt, matKhau)`
- `2: KiemTraDuyNhat(email, sdt)`
- `3: MaHoaMatKhauBCrypt(matKhau)`
- `4: TaoNguoiDungMoi(thongTin)`
- `5: ChonThietBiVaNgayThue(maSanPham, tuNgay, denNgay)`
- `6: KichHoatKhoaKiemTraTonKho(InventoryLock)`
- `7: KiemTraLichKhaDungSerial(maSanPham, tuNgay, denNgay)`
- `8: GiuChoThietBiSerial(maThietBi, hanChotKy24h)`
- `9: GiaiPhongKhoaKiemTraTonKho()`
- `10: TaoMaVietQRDong(maHopDong, soTienCoc)`
- `11: ChuyenKhoanNAPAS247(maHopDong, soTien)`
- `12: GuiTinHieuWebhook(maGiaoDich, soTien, noiDung)`
- `13: KichHoatKhoaThanhToan(PaymentLock)`
- `14: GachNoVaTaoPhieuThu(maHopDong, soTien)`
- `15: QuetBarcodeXuatKho(soSerial)`
- `16: DongKiemVaKyCanvas(chuKyKhachHang)`
- `17: XuatBienBanBanGiaoPDF(maBienBan)`
- `18: GuiTicketBaoSuCo(maHopDong, maThietBi, moTa, hinhAnh)`
- `19: PhanCongKyThuatVien(maPhieuBaoTri, maKTV, hanXuLy)`
- `20: KichHoatSLATamDungTinhTien(maPhieuBaoTri)`
- `21: DeXuatGiaHanHopDong(maHopDong, soNgayGiaHan)`
- `22: KiemTraXungDotDonKeTiep(maThietBi, ngayBatDauMoi)`
- `23: PheDuyetGiaHanVaPhanKyNo(maYeuCau)`
- `24: NghiemThuVaThamDinhHuHai(maThietBi, tinhTrang)`
- `25: QuyetToanCanTruCoc(maHopDong, phiDenBu, noThue)`
- `26: LapPhieuChiHoanCocDu(maHopDong, soTienHoan)`

---

## 7. QUY CHUẨN CÚ PHÁP PETAL & CHỈ DẪN KỸ THUẬT CHO IBM RATIONAL ROSE

Để đảm bảo tệp `.mdl` nạp thành công 100% trên IBM Rational Rose 2003 / 98:

### 7.1. Cấu trúc Header & Quid Taxonomy
```petal
(object Petal
    version 	47
    _written 	"Rose 8.0.0303.1400"
    charSet 	0)
```
- **Quid Taxonomy (16-Hex Phân cấp)**: `[Domain: 6001][Category: 0001..0008][Counter: 8 Hex]`
  - `60010001xxxxxxxx`: Actors & Workers
  - `60010002xxxxxxxx`: Business & System Use Cases
  - `60010003xxxxxxxx`: Associations & Relations
  - `60010004xxxxxxxx`: Diagrams (Use Case, Activity, Sequence, Class)
  - `60010005xxxxxxxx`: Classes (BCE & 3-Tier Design)
  - `60010006xxxxxxxx`: Operations & Methods
  - `60010007xxxxxxxx`: Attributes & Properties
  - `60010008xxxxxxxx`: Interactions & Messages

### 7.2. Hai quy tắc cú pháp bất khả kháng
1. **Trong `AssociationViewNew`**: Bắt buộc sử dụng `roleview_list (list RoleViews` (Tuyệt đối không dùng `RoleViewList`).
2. **Trong `process_structure`**: Bắt buộc sử dụng `ProcsNDevs (list (object Process_Diagram ...))` (Tuyệt đối không dùng `Procs (list Processes))`).

### 7.3. Lệnh kiểm tra xác thực cú pháp tự động
```powershell
python D:\DoAnCuNhan\Rose_Diagrams\validate_petal.py D:\DoAnCuNhan\Rose_Diagrams\RentalSystem_Master.mdl
```
Tiêu chí nghiệm thu: **0 ERROR(S)**, trạng thái `[PASS]`.
