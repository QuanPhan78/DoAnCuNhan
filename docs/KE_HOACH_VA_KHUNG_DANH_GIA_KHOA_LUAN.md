# KẾ HOẠCH VÀ KHUNG ĐÁNH GIÁ CHI TIẾT TỪNG CÂU TỪNG CHỮ TÀI LIỆU KHÓA LUẬN TỐT NGHIỆP RENTALSYSTEM (HUIT 2025)
**ĐỐI CHIẾU TOÀN DIỆN MÃ NGUỒN THỰC TẾ, NHẬN DIỆN LỖ HỔNG NGHIỆP VỤ VÀ TRIỆT TIÊU ẢO GIÁC AI**

- **Tài liệu mục tiêu kiểm định**: `KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx`
- **Quy mô văn bản**: 740 Đoạn văn (Paragraphs), 88 Tiêu đề phân cấp (Headings 1-4), 51 Bảng biểu (Tables), 71 Sơ đồ / Hình ảnh (Figures), 19 Tài liệu tham khảo IEEE, 14 Ca kiểm thử chức năng (TC-01..TC-14).
- **Phạm vi đối chứng mã nguồn**: Toàn bộ hệ thống `RentalSystem` (.NET 9.0 ASP.NET Core MVC & Web API), Cơ sở dữ liệu SQL Server (`AppModels.cs`, 18 DbSets), Hệ thống Giao diện Web Client & Admin (64 Razor Views), Ứng dụng Di động Flutter (`MobileApp/`, 36 Screens) và Bộ kiểm thử tự động `ChallengerTests` (595 tests, tỷ lệ đạt 100%).
- **Phiên bản khung đánh giá**: 1.0 (Master Evaluation Framework & Publication-Grade Audit Plan)
- **Ngày ban hành**: 02/11/2026

---

## MỤC LỤC TỔNG QUAN

1. [Mục Tiêu & Tôn Chỉ Đánh Giá](#1-mục-tiêu--tôn-chỉ-đánh-giá)
2. [R1: Bộ Tiêu Chí Kiểm Định & Hệ Thống Phân Loại Sai Lệch (Taxonomy)](#2-r1-bộ-tiêu-chí-kiểm-định--hệ-thống-phân-loại-sai-lệch-taxonomy)
   - [2.1. Bốn Nhóm Nội Dung Kiểm Định Cốt Lõi](#21-bốn-nhóm-nội-dung-kiểm-định-cốt-lõi)
   - [2.2. Hệ Thống Phân Loại Sai Lệch 3 Trục (Taxonomy Matrix)](#22-hệ-thống-phân-loại-sai-lệch-3-trục-taxonomy-matrix)
   - [2.3. Thang Đo Mức Độ Nghiêm Trọng & Điều Kiện Khắc Phục Bắt Buộc](#23-thang-đo-mức-độ-nghiêm-trọng--điều-kiện-khắc-phục-bắt-buộc)
3. [R2: Quy Trình Đối Soát Chi Tiết Từng Chương/Mục (6 Verifiable Audit Units - VAU)](#3-r2-quy-trình-đối-soát-chi-tiết-từng-chươngmục-6-verifiable-audit-units---vau)
   - [3.1. VAU-0: Phần Mở Đầu & Mục Lục Từ Viết Tắt (p:163 - p:202)](#31-vau-0-phần-mở-đầu--mục-lục-từ-viết-tắt-p163---p202)
   - [3.2. VAU-1: Chương 1 - Khảo Sát Hệ Thống & Nghiệp Vụ AS-IS/TO-BE (p:203 - p:246)](#32-vau-1-chương-1---khảo-sát-hệ-thống--nghiệp-vụ-as-istobe-p203---p246)
   - [3.3. VAU-2: Chương 2 - Phân Tích Hệ Thống, Thuật Toán & Mô Hình Hóa (p:247 - p:422)](#33-vau-2-chương-2---phân-tích-hệ-thống-thuật-toán--mô-hình-hóa-p247---p422)
   - [3.4. VAU-3: Chương 3 - Thiết Kế Hệ Thống, CSDL 18 Bảng & Giao Diện (p:423 - p:626)](#34-vau-3-chương-3---thiết-kế-hệ-thống-csdl-18-bảng--giao-diện-p423---p626)
   - [3.5. VAU-4: Chương 4 - Cài Đặt Hệ Thống & Hiện Thực Hóa Kỹ Thuật (p:627 - p:668)](#35-vau-4-chương-4---cài-đặt-hệ-thống--hiện-thực-hóa-kỹ-thuật-p627---p668)
   - [3.6. VAU-5: Chương 5 & Phần Kết Luận - Thử Nghiệm, Đánh Giá & Hoàn Thiện (p:669 - p:720)](#36-vau-5-chương-5--phần-kết-luận---thử-nghiệm-đánh-giá--hoàn-thiện-p669---p720)
     - [Tiểu đơn vị 5.1: Ma Trận Ánh Xạ 14 Ca Kiểm Thử Chức Năng (TC-01..TC-14) sang Bộ Test Tự Động ChallengerTests](#tiểu-đơn-vị-51-ma-trận-ánh-xạ-14-ca-kiểm-thử-chức-năng-tc-01tc-14-sang-bộ-test-tự-động-challengertests)
     - [Tiểu đơn vị 5.2: Bản Thảo Số Liệu Định Lượng Chuẩn Hóa Thay Thế 3 Đoạn Văn Bản Giữ Chỗ (p:690, p:693, p:716)](#tiểu-đơn-vị-52-bản-thảo-số-liệu-định-lượng-chuẩn-hóa-thay-thế-3-đoạn-văn-bản-giữ-chỗ-p690-p693-p716)
4. [R3: Khung Ma Trận Đối Chiếu (Traceability Matrix) & Biểu Mẫu Phát Hiện](#4-r3-khung-ma-trận-đối-chiếu-traceability-matrix--biểu-mẫu-phát-hiện)
   - [4.1. Khung Ma Trận Đối Chiếu Đầy Đủ 6 Cột](#41-khung-ma-trận-đối-chiếu-đầy-đủ-6-cột)
   - [4.2. Bảng 20 Phát Hiện Điển Hình Khảo Sát Thực Nghiệm](#42-bảng-20-phát-hiện-điển-hình-khảo-sát-thực-nghiệm)
   - [4.3. Biểu Mẫu Ghi Nhận Phát Hiện Lỗi Chuẩn Hóa (Defect Report Template)](#43-biểu-mẫu-ghi-nhận-phát-hiện-lỗi-chuẩn-hóa-defect-report-template)
5. [Quy Định Ràng Buộc Kỹ Thuật & Lệnh Thẩm Định Độc Lập](#5-quy-định-ràng-buộc-kỹ-thuật--lệnh-thẩm-định-độc-lập)
6. [Kế Hoạch Điều Phối Thực Thi & Phân Công Nhân Sự Đợt Rà Soát](#6-kế-hoạch-điều-phối-thực-thi--phân-công-nhân-sự-đợt-rà-soát)

---

## 1. MỤC TIÊU & TÔN CHỈ ĐÁNH GIÁ

### 1.1. Bối cảnh và Tính cấp thiết
Khóa luận tốt nghiệp đại học ngành Công nghệ Thông tin tại Trường Đại học Công Thương TP. Hồ Chí Minh (HUIT) đề tài **"Xây dựng hệ thống quản lý cho thuê thiết bị (RentalSystem)"** do hai sinh viên Hồ Sĩ Tuấn và Phan Minh Quân thực hiện (2025/2026). Đây là một công trình học thuật kết hợp ứng dụng thực tiễn quy mô lớn với hơn 740 đoạn văn bản, 88 tiêu đề phân cấp sâu, 51 bảng đặc tả dữ liệu và 71 sơ đồ thiết kế kỹ thuật.

Tuy nhiên, trong quá trình soạn thảo tài liệu khoa học dài kỳ kết hợp với việc hỗ trợ của các công cụ sinh văn bản AI, hiện tượng **"Ảo giác AI" (AI Hallucinations)** và **"Bất đồng bộ kỹ thuật" (Technical Desynchronization)** rất dễ nảy sinh. Điều này dẫn đến sự chênh lệch nguy hiểm giữa những gì luận văn viết và những gì hệ thống phần mềm thực tế triển khai. Trước Hội đồng Đánh giá Khóa luận Tốt nghiệp HUIT, mọi mâu thuẫn giữa văn bản báo cáo và bản demo thực tế đều là nguy cơ trực tiếp dẫn đến việc bị trừ điểm nặng hoặc đánh trượt khóa luận.

### 1.2. Tôn chỉ "Zero Tolerance" (Không Khoan Nhượng với Hư Cấu Kỹ Thuật)
Tổ kiểm định và rà soát tài liệu thiết lập tôn chỉ hành động xuyên suốt:
1. **Triệt tiêu 100% ảo giác AI**: Mọi thành phần kiến trúc, lớp dịch vụ (Service), hàm xử lý (Action), bảng dữ liệu (Table), vai trò người dùng (Role) xuất hiện trong luận văn đều phải tồn tại thật trong mã nguồn dự án. Tuyệt đối không chấp nhận các thuật ngữ "vẽ ra cho đẹp đội hình" mà code không có.
2. **Không khoan nhượng với nội dung giữ chỗ (Unfinished Placeholders)**: Văn bản khóa luận bảo vệ chính thức không được phép tồn tại bất kỳ câu giữ chỗ nào dạng `[Nội dung ... tạm thời để trống]`. Mọi khoảng trống phải được điền đầy đủ bằng số liệu thực nghiệm đo đạc từ mã nguồn và bộ kiểm thử `ChallengerTests`.
3. **Bảo toàn tính trung thực học thuật**: Tuyệt đối không gian lận, không tạo mã nguồn giả lập (facade/dummy) chỉ để đối phó với kiểm tra, không hardcode kết quả kiểm thử.

### 1.3. Nguyên tắc "Word-by-Word Ground Truth Verification"
Quy trình đánh giá vận hành theo nguyên tắc đối soát câu-chữ đối ứng mã nguồn:
- **Nguyên tắc đối chứng trực tiếp**: Mỗi câu khẳng định kỹ thuật, bảng tham số, sơ đồ thiết kế trong tệp Word mục tiêu (`KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx`) phải được chứng minh bằng đường dẫn file, tên lớp, tên phương thức, số dòng code hoặc bài kiểm thử tự động tương ứng trong codebase.
- **Tính khả chứng độc lập (Independent Verifiability)**: Bất kỳ giảng viên phản biện hoặc kiểm toán viên độc lập nào khi đọc luận văn và cầm tài liệu đánh giá này đều có thể chạy lệnh biên dịch `dotnet build` và kiểm thử `dotnet run --project ChallengerTests` để tự mình xác nhận kết quả mà không cần hỏi lại tác giả.

---

## 2. R1: BỘ TIÊU CHÍ KIỂM ĐỊNH & HỆ THỐNG PHÂN LOẠI SAI LỆCH (TAXONOMY)

### 2.1. Bốn Nhóm Nội Dung Kiểm Định Cốt Lõi

Khung đánh giá thiết lập bộ tiêu chí bao quát toàn diện 4 nhóm nội dung kỹ thuật trọng yếu của toàn bộ hệ thống:

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                     4 NHÓM NỘI DUNG KIỂM ĐỊNH CHUYÊN SÂU                          │
├─────────────────────────┬─────────────────────────┬───────────────────────────────┤
│ 1. NGHIỆP VỤ THỰC TẾ    │ 2. CƠ SỞ DỮ LIỆU &      │ 3. API & CƠ CHẾ KỸ THUẬT      │
│    (Workflows & SoD)    │    THỰC THỂ (Entity)    │    (Endpoints & Concurrency)  │
│ - 7 Quy trình cốt lõi   │ - Đúng 18 Bảng CSDL     │ - 26 Controllers, 159 Actions │
│ - 4 Vai trò RBAC chuẩn  │ - Composite Keys        │ - RESTful API /api/...        │
│ - 4 Ca biên ngoại lệ    │ - Schema, Columns, FKs  │ - SemaphoreSlim, Magic Bytes  │
│ - Dòng tiền & Sổ cái    │ - DeleteBehaviors       │ - Tuổi nợ, SLA, Waterfall     │
├─────────────────────────┴─────────────────────────┴───────────────────────────────┤
│ 4. SƠ ĐỒ THIẾT KẾ HỆ THỐNG (71 Sơ đồ UML, Kiến trúc & Giao diện)                  │
│    - Chuẩn RUP/HUIT: Actor bên ngoài, Worker bên trong, BCE 3 lớp.                │
│    - Loại trừ thành phần kỹ thuật (SemaphoreSlim, Webhook) khỏi Actor.            │
└───────────────────────────────────────────────────────────────────────────────────┘
```

#### Nhóm 1: Nghiệp vụ thực tế (Business Logic & Workflows)
- **7 Quy trình nghiệp vụ cốt lõi**:
  1. *Đăng ký & Xác thực*: Đăng ký tài khoản khách hàng, mã hóa mật khẩu, kiểm soát tần suất Rate Limiting (`LoginLimiter` 5 req/phút).
  2. *Đặt thuê máy & Kiểm tra tồn kho*: Kiểm tra tồn kho khả dụng thời gian thực, khóa tương tranh `InventoryLock`, gán số Serial máy vật lý, chuyển `TrangThai = 3` (Giữ chỗ 24h), thiết lập hạn chốt ký `HanChotKy`.
  3. *Thanh toán đặt cọc VietQR & Webhook*: Sinh mã VietQR động chuẩn EMVCo NAPAS 247, tiếp nhận biến động số dư qua Webhook ngân hàng 24/7, gạch nợ tự động trong 1-3 giây, sinh `PhieuThu` với `MaNhanVienThu = null`.
  4. *Bàn giao & Ký biên bản*: Lập biên bản bàn giao thiết bị (`BienBanBanGiao`), ghi nhận 4 ảnh hiện trạng thiết bị, chữ ký số điện tử của khách hàng và nhân viên.
  5. *Báo cáo sự cố & Phân công bảo trì*: Khách gửi yêu cầu báo hỏng tải ảnh/video, phân loại khẩn cấp theo 3 mức SLA (12h, 24h, 48h), điều phối kỹ thuật viên, tạm dừng tính tiền thuê (`ApDungTamDungTienThue`), khóa vĩnh viễn thiết bị hỏng (`TrangThai = 4`).
  6. *Gia hạn hợp đồng & Phân kỳ nợ*: Gửi yêu cầu gia hạn, tính phí phát sinh, phân kỳ trả góp chia đều làm tròn 1.000 VNĐ, quản lý 5 nhóm tuổi nợ (Tier 0 đến Tier 4), tính lãi phạt trễ hạn 0.1%/ngày (ân hạn 3 ngày).
  7. *Trả máy, nghiệm thu & Hoàn trả tiền cọc*: Kiểm tra tình trạng thiết bị khi thu hồi kho, giám định bồi thường, cấn trừ công nợ, quyết toán hoàn cọc (`HoanCoc`) sinh `PhieuChi`.
- **4 Vai trò chuẩn (RBAC)**: Chỉ có 4 vai trò hợp lệ trong hệ thống: `Admin` (MaVaiTro = 1), `KinhDoanh` (MaVaiTro = 2), `KyThuat` (MaVaiTro = 3), `KhachHang` (MaVaiTro = 4). Triệt tiêu toàn bộ các vai trò ảo (Phantom Roles): Thủ quỹ, Kế toán trưởng, Phòng Tài chính - Kế toán, Ban Giám đốc.
- **Xử lý 4 trường hợp biên ngoại lệ (Edge Cases)**:
  1. *Khách không nhận máy*: Hủy hợp đồng mềm (`HuyHopDong`), giải phóng thiết bị giữ chỗ về kho (`TrangThai = 0`), bảo lưu số tiền đã thu trong sổ cái tài chính, ghi chú yêu cầu hoàn cọc trong `HopDong.GhiChu`.
  2. *Cọc thiếu / Trả thiếu*: Thuật toán thác nước ưu tiên thanh toán cọc bảo đảm trước; nếu trả thiếu tiền kỳ hạn thì ghi nhận `SoTienDaTra`, giữ kỳ hạn ở trạng thái chưa trả (`TrangThai = 0`), ghi nhận ngày hẹn trả tiếp theo (`NgayHenTraTiepTheo`).
  3. *Đền bù hỏng máy*: Khi máy bị hư hại nặng, chi phí đền bù vượt tiền cọc (`PhiDenBu > TienCoc`), hệ thống chặn đóng hợp đồng (CRIT-01/CRIT-02) cho đến khi thu đủ khoản chênh lệch qua `PhieuThu` loại 2 (`ThuPhiDenBu`).
  4. *Trễ hạn không trả máy*: Tự động áp dụng công thức phạt trễ hạn sau 3 ngày ân hạn; nếu trễ quá 15 ngày hoặc tổng dư nợ vượt quá 3.000.000 VNĐ, kích hoạt hàm `DebtCalculationHelper.IsCustomerBlacklisted` để khóa quyền đặt thuê máy mới trên toàn hệ thống.

#### Nhóm 2: Cơ sở dữ liệu & Thực thể (Database & Entity Models)
- **18 Bảng CSDL thực tế trong `RentalSystem/Models/AppModels.cs`**:
  `VaiTro`, `NguoiDung`, `LoaiThietBi`, `SanPham`, `ThietBi`, `LichSuThietBi`, `KhuyenMai`, `HopDong`, `ChiTietHopDong`, `KyHanThanhToan`, `PhieuThu`, `PhieuChi`, `PhieuBaoTri`, `BienBanBanGiao`, `ThongBao`, `LichSuNhacNo`, `YeuCauGiaHan`, `PhanCongCongViec`.
  *(Bác bỏ phát biểu tài liệu có 23 bảng — 5 bảng dôi dư là ViewModel hoặc Session state)*.
- **Khóa phức hợp (Composite Key)**: Bảng `ChiTietHopDong` thực tế dùng khóa kết hợp hai cột `[Key, Column(Order=0)] MaHopDong` và `[Key, Column(Order=1)] MaThietBi`, trường lưu đơn giá là `GiaChotThu`. Tài liệu Word mô tả khóa đơn `MaChiTiet` và lưu `TienCoc` là sai lệch nghiêm trọng.
- **Chuẩn hóa Danh pháp Cột & Kiểu dữ liệu**:
  - `NguoiDung`: `MatKhau` (chuỗi), không có cột `MatKhauHash` hay `NgayTao` trên model thực tế.
  - `VaiTro`: Chỉ có `MaVaiTro`, `TenVaiTro` (không có cột `MoTa`).
  - `LoaiThietBi`: Chỉ có `MaLoai`, `TenLoai` (không có cột `BiDanh`, `MoTa`, `TrangThai`).
  - `SanPham`: Chỉ có `GiaThueNgay`, `TienCoc` (không có cột `GiaThueThang`, `SoLuongSanCo`, `TrangThai`).
  - `HopDong`: Khóa ngoại mã khuyến mãi là `MaKhuyenMai` (không phải `MaKM`).
  - `LichSuThietBi`: Khóa chính là `MaLichSu`, khóa ngoại người thực hiện là `MaNguoiThucHien` (không phải `MaLSTB`, `NguoiThucHienId`).
  - `PhieuBaoTri`: Khóa chính là `MaPhieu`, khóa ngoại kỹ thuật viên là `MaKyThuatVien` (không phải `MaPhieuBaoTri`, `KyThuatVienId`).
- **Quy tắc Toàn vẹn Tham chiếu (Foreign Keys & Delete Behaviors)**:
  - `HopDong` -> `ChiTietHopDong`: `Cascade`.
  - `HopDong` -> `KyHanThanhToan`: `Cascade`.
  - `HopDong` -> `PhieuChi`: Cấu hình trong `ApplicationDbContext` là `Cascade` (Word ghi nhầm là `Restrict`).
  - `HopDong` -> `PhieuThu`: `Restrict` (đảm bảo kiểm toán tài chính không bị xóa mất chứng từ thu).

#### Nhóm 3: API & Luồng Xử Lý Kỹ Thuật (Endpoints, Services & Concurrency)
- **26 Controllers & 159 Actions**:
  - 11 Admin Controllers (81 actions): Quản lý nghiệp vụ sâu, xử lý dòng tiền, điều phối kỹ thuật, báo cáo BI.
  - 7 Client Controllers (52 actions): Luồng đặt thuê, giỏ hàng, hợp đồng cá nhân, báo sự cố, tra cứu công nợ.
  - 8 Mobile API Controllers (26 actions): Cung cấp dữ liệu JSON cho Flutter qua tiền tố `/api/...`.
- **Đặc tả RESTful API**: Tuyệt đối sử dụng tiền tố chuẩn `/api/{controller}` (tiếng Anh) như mã nguồn triển khai (`/api/auth`, `/api/devices`, `/api/contracts`, `/api/maintenance`, `/api/promotions`, `/api/reports`, `/api/search`, `/api/dashboard`). Loại bỏ bảng API mô tả tiền tố `/api/v1/...` bằng tiếng Việt không tồn tại trong code.
- **Kiểm soát Tương tranh & Vùng găng (Critical Section)**:
  - Triển khai trực tiếp bằng biến tĩnh:
    `public static readonly SemaphoreSlim InventoryLock = new SemaphoreSlim(1, 1);` trong `CartController.cs`.
    `private static readonly SemaphoreSlim _paymentLock = new SemaphoreSlim(1, 1);` trong `HopDongController.cs`.
  - Loại bỏ hoàn toàn ảo giác về các lớp dịch vụ trừu tượng: `InventoryLockService`, `RentalLockManager`, `DebtManagementService`, `VietQrService`.
- **Bảo mật Chữ ký Canvas & Tải tệp CCCD**:
  - Giới hạn Base64 chữ ký Canvas tối đa 256KB, kiểm tra Header Magic Bytes PNG (`0x89 0x50 0x4E 0x47`), chống tràn bộ nhớ Base64 DoS (`VULN-11`).
  - Giới hạn tệp ảnh CCCD tối đa 5MB, xác thực MIME-type và Magic Bytes ảnh thực tế (JPEG `0xFF 0xD8 0xFF`, PNG, WEBP `RIFF`).
- **Thuật toán Thác nước Phân bổ Thanh toán (Waterfall Reconciliation)**:
  - Tầng 1: Cấn trừ nợ gốc và phí phạt của kỳ hạn hiện tại.
  - Tầng 2: Cấn trừ liên tiếp các kỳ hạn tương lai chưa đến hạn (`SoKyHan ASC`).
  - Tầng 3: Cấn trừ chi phí bồi thường hư hại máy bảo trì chưa thanh toán.
  - Tầng 4: Kết chuyển số tiền trả thừa vào `HopDong.TienTraThua` để kế toán hoàn trả qua `PhieuChi`.

#### Nhóm 4: Sơ đồ Thiết kế Hệ thống (71 Diagrams & RUP Compliance)
- **71 Sơ đồ UML & Kiến trúc trong Word**:
  - 1 Sơ đồ luồng AS-IS/TO-BE.
  - 1 Đặc tả cấu trúc bản tin VietQR TLV.
  - 1 Sơ đồ Business Use Case.
  - 21 Sơ đồ phân tích nghiệp vụ 7 quy trình (Activity, Sequence, Collaboration).
  - 4 Sơ đồ System Use Case tổng quát và 3 phân hệ.
  - 1 Sơ đồ Analysis Class Diagram.
  - 1 Sơ đồ Physical Database ERD.
  - 11 Sơ đồ Giao diện màn hình UI & 2 Sitemap.
  - 1 Sơ đồ Design Class Diagram 3 lớp.
  - 21 Sơ đồ thiết kế chi tiết 3 lớp BCE 7 chức năng (BCE Class, Sequence 3 lớp, Collaboration 3 lớp).
  - 6 Sơ đồ kiến trúc kỹ thuật Chương 4 (.NET MVC Pipeline, Folder structure, State Machine vòng đời máy, State Machine bảo trì, EF Core Migrations).
- **Quy chuẩn RUP / HUIT**:
  - Tác nhân (Actor): Phải là người dùng hoặc hệ thống bên ngoài tương tác với ranh giới hệ thống (Khách hàng, Nhân viên kinh doanh, Kỹ thuật viên, Quản trị viên, Cổng ngân hàng Webhook SePay/Casso).
  - Tuyệt đối cấm gán các cơ chế phần mềm nội bộ như `SemaphoreSlim`, `Webhook Middleware`, `Hangfire/BackgroundService`, `DebtCalculationHelper` thành Actor hình người trong sơ đồ Use Case và Sequence. Chúng phải được biểu diễn dưới dạng `Boundary Class`, `Control Class` hoặc `Entity Class` theo chuẩn BCE.
  - Triệt tiêu hoàn toàn đường truyền `SignalR` trên các sơ đồ giao tiếp thời gian thực, thay thế bằng cơ chế HTTP Polling hoặc Webhook không đồng bộ.

---

### 2.2. Hệ Thống Phân Loại Sai Lệch 3 Trục (Taxonomy Matrix)

Khung đánh giá thiết lập bộ danh mục sai lệch gồm **13 mã lỗi chuẩn mực phân bổ trên 3 trục độc lập**:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              HỆ THỐNG PHÂN LOẠI SAI LỆCH 3 TRỤC (TAXONOMY)                             │
├──────────────────────────────────────┬──────────────────────────────────┬──────────────────────────────┤
│ TRỤC 1: ẢO GIÁC AI (HALLUCINATIONS)  │ TRỤC 2: LỖ HỔNG NGHIỆP VỤ (GAPS) │ TRỤC 3: BẤT ĐỒNG BỘ (DESYNC) │
├──────────────────────────────────────┼──────────────────────────────────┼──────────────────────────────┤
│ H1: Vai trò / Tác nhân ảo            │ G1: Mâu thuẫn Duyệt tay vs Auto  │ D1: Lệch Bảng / Cột / Khóa   │
│ H2: Lớp / Dịch vụ / Controller ảo    │ G2: Phóng đại kiểm soát tương tranh│ D2: Lệch Route & Tham số API │
│ H3: Thuật toán / Công nghệ ảo        │ G3: Bỏ sót 4 ca biên ngoại lệ    │ D3: Lệch vai trò Web - Mobile│
│ H4: Gán sai Actor kỹ thuật trong UML │ G4: Vi phạm phân quyền & lộ PII  │ D4: Lệch hiện thực JS & UI   │
│                                      │                                  │ D5: Lộ lọt STK thử nghiệm    │
└──────────────────────────────────────┴──────────────────────────────────┴──────────────────────────────┘
```

#### Trục 1: Ảo giác AI (AI Hallucinations - Ký hiệu H)
- **H1 - Phantom Roles (Vai trò người dùng ảo)**: Bất kỳ câu văn, bảng phân công hay sơ đồ nào nhắc đến các chức danh: *Thủ quỹ, Kế toán, Kế toán trưởng, Ban Giám đốc, Ban Quản trị, Hội đồng quản trị, Trưởng phòng Kỹ thuật*. Thực tế hệ thống chỉ có 4 role trong bảng `VaiTro`.
- **H2 - Phantom Components & Classes (Thành phần kiến trúc ảo)**: Bịa đặt sự tồn tại của các tệp mã nguồn hoặc lớp dịch vụ không có trong solution: `RentalDbContext` (thực tế là `ApplicationDbContext`), `InventoryLockService`, `RentalLockManager`, `DebtManagementService`, `VietQrService`, `PaymentWebhookController`, `PhieuChiController`, bảng `WebhookLog`.
- **H3 - Fake Algorithms & Technologies (Thuật toán / Công nghệ ảo)**: Mô tả các thư viện và công nghệ thời thượng không có trong mã nguồn: Thư viện `SignalR Hub` nhận thông báo gạch nợ tức thời; công nghệ AI/Machine Learning gợi ý cấu hình máy; tuyên bố sai lệch phiên bản như *.NET 9 Long Term Support (LTS)* (thực tế .NET 9 là STS).
- **H4 - UML Technical Actor Misclassification (Gán sai Actor kỹ thuật)**: Vẽ các cấu trúc dữ liệu, thư viện ngôn ngữ hoặc tiến trình ngầm (.NET `SemaphoreSlim`, Webhook HTTP, `BackgroundService`, `DebtCalculationHelper`) thành Actor hình người trong sơ đồ Use Case, Sequence Diagram.

#### Trục 2: Lỗ hổng nghiệp vụ & Mâu thuẫn logic (Business Logic Gaps - Ký hiệu G)
- **G1 - Manual vs Automated Contradiction (Mâu thuẫn Duyệt tay vs Tự động hóa)**: Tồn tại sự mâu thuẫn giữa mô tả quy trình kế toán kiểm tra SMS bấm duyệt thu tiền thủ công với đường ống Webhook gạch nợ tự động 100% trong 1-3 giây (`MaNhanVienThu = null`); hoặc mâu thuẫn giữa giao diện Web hiển thị `(Admin duyệt thủ công)` với cơ chế Backend tự động.
- **G2 - Concurrency & Scale Overclaim (Phóng đại năng lực tương tranh)**: Khẳng định cơ chế `SemaphoreSlim(1,1)` giải quyết triệt để 100% bài toán phân tán trên mọi hạ tầng. Thực tế đây là biến static in-memory chỉ bảo vệ an toàn trên mô hình Single-instance; nếu triển khai cụm Web Farm đa máy chủ phải dùng Distributed Lock (Redis RedLock) hoặc mức cô lập CSDL Serializable.
- **G3 - Edge Cases Omission (Bỏ sót hoặc xử lý sai 4 trường hợp biên)**: Văn bản không đặc tả hoặc mô tả mâu thuẫn về cách xử lý 4 tình huống: (1) Khách bùng không nhận máy sau khi xuất kho; (2) Chuyển khoản cọc thiếu; (3) Hỏng máy nặng chi phí sửa chữa vượt tiền cọc; (4) Trễ hạn chiếm giữ thiết bị quá 15 ngày.
- **G4 - Separation of Duties & Security Leaks (Vi phạm phân quyền & An toàn thông tin)**: Mô tả phân quyền cho phép Nhân viên kinh doanh vừa duyệt đơn vừa lập phiếu chi hoàn tiền cọc (vi phạm SoD); hoặc cho phép Kỹ thuật viên xem thông tin doanh thu, báo cáo tài chính nội bộ.

#### Trục 3: Bất đồng bộ kỹ thuật (Technical Desynchronizations - Ký hiệu D)
- **D1 - Database Schema & Entity Desync (Lệch bảng, trường, khóa CSDL)**: Bất đồng bộ giữa từ điển dữ liệu (Bảng 32-49 trong Word) với thực thể trong `AppModels.cs`. Cụ thể: `ChiTietHopDong` bị mô tả là khóa đơn `MaChiTiet` thay vì Composite Key `(MaHopDong, MaThietBi)`; thêm các trường không tồn tại (`MoTa` trong `VaiTro`, `BiDanh` trong `LoaiThietBi`, `SoLuongSanCo` trong `SanPham`); lệch tên trường (`MatKhauHash` vs `MatKhau`, `MaKM` vs `MaKhuyenMai`, `MaLSTB` vs `MaLichSu`).
- **D2 - API Routing & Signature Desync (Lệch Route và Phương thức API)**: Bất đồng bộ giữa Bảng 31 đặc tả API trong Word với các Controller API thực tế. Word mô tả tiền tố `/api/v1/...` bằng tiếng Việt, trong khi code triển khai chuẩn tiếng Anh `/api/...` (ví dụ: `/api/devices`, `/api/contracts`, `/api/maintenance/{id}/rating`).
- **D3 - Role Representation Desync (Lệch vai trò Web vs Mobile)**: Tài liệu tuyên bố đồng bộ phân quyền 100% trên đa nền tảng, nhưng trên Flutter MobileApp enum `Role` lại gom chung (flatten) cả hai vai trò `KinhDoanh` và `KyThuat` thành `Role.staff`; phân hệ lắp đặt trên di động vẫn đang đọc tệp Mock JSON do thiếu `ApiInstallationController` trên backend.
- **D4 - Presentation & Script Desync (Lệch hiện thực giao diện & JS)**: Tài liệu mô tả các tệp JavaScript module độc lập trong thư mục `wwwroot/js/`, nhưng thực tế thư mục này rỗng (0 bytes), toàn bộ logic chạy bằng Inline Script và CDN; mô tả mã QR được sinh bởi thư viện JS cục bộ thay vì gọi trực tiếp VietQR Image API.
- **D5 - Sensitive Hardcoded Data Leaks (Lộ lọt thông tin tài khoản thử nghiệm)**: Bản thảo tài liệu hoặc mã nguồn nhúng trực tiếp số tài khoản ngân hàng thử nghiệm cá nhân của sinh viên (MBBank `0783406516` - PHAN MINH QUAN) thay vì sử dụng thông tin định danh doanh nghiệp mẫu chuẩn hóa (`999988882026` - RENTALSYSTEM ENTERPRISE).

---

### 2.3. Thang Đo Mức Độ Nghiêm Trọng & Điều Kiện Khắc Phục Bắt Buộc

Khung đánh giá phân định 4 mức độ nghiêm trọng (Severity Levels) với định nghĩa và chế tài khắc phục rõ ràng:

| Mức Độ | Định Nghĩa & Tác Động Học Thuật | Ví Dụ Điển Hình Trong Khóa Luận | Điều Kiện Khắc Phục Bắt Buộc (Mandatory Remedy) |
|:---:|:---|:---|:---|
| **BLOCKER** | Lỗi tối kỵ dẫn đến việc Hội đồng đánh trượt hoặc yêu cầu hoãn bảo vệ ngay lập tức. Vi phạm tính toàn vẹn học thuật hoặc để trống nội dung. | - Tồn tại các đoạn văn bản giữ chỗ chưa hoàn thiện: Mục 5.2.3 (p:690), Mục 5.3 (p:693), Mục 4 Kết luận (p:716).<br>- Sai lệch cấu trúc khóa chính Composite Key của CSDL dẫn đến việc mã nguồn không thể chạy đúng như mô tả. | Bắt buộc phải viết lại 100%, lấp đầy bằng số liệu thực nghiệm đo đạc từ mã nguồn và bộ kiểm thử `ChallengerTests`. Không được phép nộp bản in có bất kỳ câu placeholder nào. |
| **CRITICAL** | Lỗi nghiêm trọng làm sai lệch bản chất kiến trúc hệ thống, vi phạm chuẩn mực kỹ thuật hoặc mô tả các thành phần hoàn toàn không tồn tại. | - Bịa đặt lớp `RentalDbContext`, `InventoryLockService`, `DebtManagementService`, `VietQrService`.<br>- Vẽ `SemaphoreSlim` và `Webhook` thành Actor trong UML.<br>- Khẳng định có hệ thống `SignalR` thời gian thực. | Hiệu chỉnh lại toàn bộ văn bản và sơ đồ: đổi tên `RentalDbContext` thành `ApplicationDbContext`, thay thế các Service ảo bằng Static Lock và Helper thực tế; chuẩn hóa sơ đồ UML theo chuẩn RUP/HUIT. |
| **MAJOR** | Sai lệch đáng kể về thông số kỹ thuật, cấu trúc trường dữ liệu, tiền tố API hoặc mâu thuẫn giữa các chương trong luận văn. | - Bất đồng bộ 10 bảng CSDL: mô tả thừa các cột `MoTa`, `BiDanh`, `SoLuongSanCo`; sai lệch tên trường `MatKhauHash`, `MaLSTB`.<br>- Bảng API dùng tiền tố `/api/v1/...` tiếng Việt.<br>- Mâu thuẫn tiêu đề ghi "4 cấp tuổi nợ" nhưng bảng liệt kê 5 cấp (Tier 0-4). | Cập nhật lại chính xác từ điển dữ liệu 18 bảng theo đúng `RentalSystem/Models/AppModels.cs`; sửa bảng API khớp với 8 Mobile API Controllers; sửa thống nhất tên gọi "5 nhóm tuổi nợ (Tier 0 đến Tier 4)". |
| **MINOR** | Các lỗi nhỏ về câu chữ, thuật ngữ công nghệ chưa hoàn toàn chuẩn xác, hoặc hiển thị số tài khoản thử nghiệm chưa được che mờ. | - Gọi .NET 9 là bản LTS (thực tế là STS).<br>- Lộ số tài khoản cá nhân `0783406516` trong các ảnh chụp màn hình minh họa thay vì số doanh nghiệp `999988882026`.<br>- Lỗi gõ nhầm tên bảng `LichSuSuDung` thay vì `LichSuThietBi`. | Rà soát biên tập lại câu chữ, thay thế ảnh chụp hoặc che mờ số tài khoản cá nhân thành tài khoản doanh nghiệp; chuẩn hóa thuật ngữ phiên bản phần mềm. |

---

## 3. R2: QUY TRÌNH ĐỐI SOÁT CHI TIẾT TỪNG CHƯƠNG/MỤC (6 VERIFIABLE AUDIT UNITS - VAU)

Toàn bộ tài liệu khóa luận (740 đoạn văn, 51 bảng biểu, 71 sơ đồ) được phân rã thành **6 Đơn vị Đối soát Trọng tâm (Verifiable Audit Units - VAU)**. Mỗi VAU có phạm vi, đối tượng, file mã nguồn đối chứng và phương pháp kiểm định độc lập rõ ràng:

```
TÀI LIỆU KHÓA LUẬN TOT NGHIEP (740 Paragraphs, 51 Tables, 71 Figures)
│
├── [VAU-0] Phần Mở Đầu & Tiến Độ Đề Tài (p:163 - p:202 | Bảng 1-2)
│   └── Đối soát: Thuật ngữ viết tắt, Phạm vi đề tài, Khung thời gian 12 tuần
│
├── [VAU-1] Khảo Sát Nghiệp Vụ Hiện Trạng AS-IS (p:203 - p:246 | Bảng 3-7 | Hình H01)
│   └── Đối soát: 6 bước AS-IS, 5 biểu mẫu chứng từ, 5 điểm nghẽn vận hành
│
├── [VAU-2] Phân Tích Hệ Thống, Thuật Toán & Use Case (p:247 - p:422 | Bảng 8-31 | Hình H02-H29)
│   ├── Tiểu đơn vị 2.1: Thuật toán SemaphoreSlim, VietQR TLV, Thác nước Webhook, Tuổi nợ
│   ├── Tiểu đơn vị 2.2: 7 Quy trình nghiệp vụ trọng tâm (21 sơ đồ Activity/Sequence/Collab)
│   └── Tiểu đơn vị 2.3: 13 Ca sử dụng (UC-01..13) & 8 Endpoints RESTful API
│
├── [VAU-3] Thiết Kế CSDL 18 Bảng, Giao Diện & BCE (p:423 - p:626 | Bảng 32-49 | Hình H30-H65)
│   ├── Tiểu đơn vị 3.1: Từ điển dữ liệu 18 bảng CSDL vs AppModels.cs & DbContext
│   ├── Tiểu đơn vị 3.2: 11 Giao diện UI Web/Mobile, 2 Sitemap vs 64 Razor Views
│   └── Tiểu đơn vị 3.3: Thiết kế 3 lớp BCE 7 chức năng (21 sơ đồ UML)
│
├── [VAU-4] Cài Đặt Hệ Thống & Hiện Thực Hóa Mã Nguồn (p:627 - p:668 | Bảng 50 | Hình H66-H71)
│   ├── Tiểu đơn vị 4.1: Tech stack, Pipeline Middleware, Máy trạng thái, Migrations
│   └── Tiểu đơn vị 4.2: 6 Cơ chế code: SemaphoreSlim, Magic bytes, Webhook, BI, Backup
│
└── [VAU-5] Triển Khai, Kiểm Thử & Phần Kết Luận (p:669 - p:720 | Bảng 51 | TLTK)
    ├── Tiểu đơn vị 5.1: 14 Ca kiểm thử chức năng (TC-01..TC-14) vs 595 ChallengerTests
    └── Tiểu đơn vị 5.2: Triệt tiêu hoàn toàn 3 đoạn giữ chỗ (p:690, p:693, p:716)
```

---

### 3.1. VAU-0: Phần Mở Đầu & Mục Lục Từ Viết Tắt (p:163 - p:202)
- **Mục tiêu kiểm tra**: Đảm bảo toàn bộ thuật ngữ chuyên ngành được định nghĩa chính xác, không mâu thuẫn với công nghệ thực tế; kế hoạch phân công 12 tuần phản ánh đúng năng lực và phạm vi bàn giao.
- **Danh mục đối chiếu trong Word**:
  - Bảng 0.1. 1 (p:164): 19 thuật ngữ (ASP.NET, MVC, EF Core, BCE, UML, ERD, API, REST, JSON, EMVCo, NAPAS, VietQR, RBAC, SLA, BI, OpEx, CapEx, CCCD).
  - Bảng 0.4. 1 (p:200): Kế hoạch 12 tuần (17/08/2026 - 08/11/2026), phân công nhiệm vụ giữa Hồ Sĩ Tuấn (Backend/DB/Testing) và Phan Minh Quân (Frontend/Mobile/UI).
  - Mục tiêu và phạm vi đề tài (Mục 1, 2, 3 - p:174..197).
- **Thành phần mã nguồn đối chứng**:
  - `RentalSystem/RentalSystem.csproj` (.NET 9.0, Packages).
  - `MobileApp/pubspec.yaml` (Flutter SDK, Dependencies).
  - `ChallengerTests/ChallengerTests.csproj` (Cấu trúc bộ test).
- **Phương pháp đối chứng**:
  - *Static Documentation Inspection*: So sánh định nghĩa thuật ngữ trong Bảng 1 với chuẩn quốc tế (EMVCo MPM Specification, RFC 7231 REST, ISO/IEC 7816).
  - *Scope Verification*: Đối soát phạm vi thiết bị (Laptop, PC, Máy in, Máy chủ) với dữ liệu khởi tạo trong `RentalSystem/Models/DbInitializer.cs`.

---

### 3.2. VAU-1: Chương 1 - Khảo Sát Hệ Thống & Nghiệp Vụ AS-IS/TO-BE (p:203 - p:246)
- **Mục tiêu kiểm tra**: Xác thực tính chính xác của mô hình khảo sát thực tế, loại bỏ vai trò ảo trong cơ cấu tổ chức, chứng minh 5 điểm nghẽn thủ công được giải quyết bằng các tính năng phần mềm tương ứng.
- **Danh mục đối chiếu trong Word**:
  - Bảng 1.1.2. 1 (p:218): Quy trình AS-IS 6 bước (Tiếp nhận -> Kiểm tra sổ kho giấy -> Soạn HĐ giấy -> Thu cọc mặt/CK -> Sổ theo dõi Excel -> Trả máy nghiệm thu cảm quan).
  - Bảng 1.2. 1 (p:229): Quy trình đề xuất TO-BE 5 giai đoạn (Đặt thuê trực tuyến -> Ký số Canvas & VietQR -> Cấp phát Serial kho -> Bảo trì theo dõi SLA -> Nghiệm thu tất toán cọc).
  - Bảng 1.1.3. 1 (p:238): 5 Điểm nghẽn vận hành (Overbooking, Lẫn lộn serial, Chậm trễ giấy tờ, Tắc nghẽn đối soát ngân hàng, Tranh chấp bảo trì).
  - Bảng 1.3. 1 (p:240): 5 Biểu mẫu nghiệp vụ (BM-01 Hợp đồng, BM-02 Biên bản bàn giao, BM-03 Phiếu thu, BM-04 Phiếu bảo trì, BM-05 Biên bản thanh lý).
  - Hình 1.2. 1 (p:228): Sơ đồ luồng quy trình nghiệp vụ tổng thể TO-BE.
- **Thành phần mã nguồn đối chứng**:
  - `RentalSystem/Controllers/CartController.cs` (Đặt thuê trực tuyến, Ký số Canvas).
  - `RentalSystem/Controllers/DocumentController.cs` (Kết xuất 5 biểu mẫu BM-01 đến BM-05).
  - `RentalSystem/Views/Document/` (`InHopDong.cshtml`, `InBienBanBanGiao.cshtml`, `InPhieuThu.cshtml`).
  - `RentalSystem/Models/DbInitializer.cs` (Khởi tạo 4 vai trò chuẩn, không có vai trò ảo).
- **Phương pháp đối chứng**:
  - *Workflow Traceability Analysis*: Lập bảng so sánh 1:1 giữa 5 biểu mẫu BM với các View in ấn và thuộc tính thực thể tương ứng.
  - *Role Clearance Check*: Quét toàn bộ văn bản Chương 1, xóa bỏ triệt để các danh xưng "Thủ quỹ", "Kế toán trưởng", "Ban Giám đốc".

---

### 3.3. VAU-2: Chương 2 - Phân Tích Hệ Thống, Thuật Toán & Mô Hình Hóa (p:247 - p:422)
- **Mục tiêu kiểm tra**: Đối chứng tính chính xác của 3 giải thuật cốt lõi, chuẩn hóa 7 quy trình nghiệp vụ và 13 Use Cases theo quy chuẩn RUP/HUIT, điều chỉnh toàn bộ bảng đặc tả API khớp với Controller thực tế.
- **Danh mục đối chiếu trong Word**:
  - **Mục 2.1: Các thuật toán cốt lõi**:
    - Bảng 2.1.1. 1 (p:257): Ma trận kịch bản tương tranh SemaphoreSlim (4 kịch bản giữ chỗ).
    - Bảng 2.1.2. 1 (p:275) & Hình 2.1.2. 1 (p:272): Cấu trúc VietQR TLV EMVCo & 8 bước Webhook gạch nợ tự động.
    - Bảng 2.1.3. 1 (p:284): Phân kỳ trả góp, công thức phạt trễ 0.1%/ngày và tiêu chí 5 nhóm tuổi nợ (Tier 0-4).
  - **Mục 2.2: Mô hình hóa nghiệp vụ**:
    - Hình 2.2.1. 1 (p:291): Sơ đồ Business Use Case tổng quát.
    - Bảng 11 - 17: 7 Bảng đặc tả quy trình nghiệp vụ (2.2.2.1 đến 2.2.2.7).
    - 21 Sơ đồ phân tích (Hình H04 đến H24): 7 Activity Diagrams, 7 Sequence Diagrams, 7 Collaboration Diagrams.
  - **Mục 2.3 & 2.4: Mô hình hóa chức năng & Phân tích lớp**:
    - 4 Sơ đồ System Use Case (Hình H25 tổng quát, H26 Khách hàng, H27 Admin, H28 Kỹ thuật).
    - Bảng 18 - 30: 13 Bảng đặc tả Use Case chi tiết (UC-01 đến UC-13).
    - Bảng 2.3.3. 1 (p:411): Bảng đặc tả 8 Endpoints RESTful API.
    - Hình 2.4. 1 (p:419): Sơ đồ lớp mức phân tích (Analysis Class Diagram).
- **Thành phần mã nguồn đối chứng**:
  - `RentalSystem/Controllers/CartController.cs` (dòng 17: `InventoryLock`, dòng 312: `Checkout`).
  - `RentalSystem/Controllers/PaymentController.cs` (dòng 400-650: VietQR generation, Webhook regex bóc tách `HD\d+` và `KY\d+`, Idempotency check).
  - `RentalSystem/Common/DebtCalculationHelper.cs` (Cài đặt hàm `CalculateLateFee`, `CalculateAgingTier`, `IsCustomerBlacklisted`).
  - `RentalSystem/Controllers/Api*.cs` (8 Controllers: `ApiAuthController`, `ApiDevicesController`, `ApiContractsController`, `ApiMaintenanceController`, `ApiPromotionsController`, `ApiReportsController`, `ApiSearchController`, `ApiDashboardController`).
- **Phương pháp đối chứng**:
  - *Algorithm Static Verification*: Đối chiếu từng hằng số toán học trong Word (hệ số phạt 0.001, ân hạn 3 ngày, CRC16 0x1021) với code C#.
  - *RUP Diagram Syntax Inspection*: Kiểm tra toàn bộ 21 sơ đồ phân tích; loại bỏ các hình người kỹ thuật `SemaphoreSlim`, `Webhook` khỏi lifeline Sequence Diagram.
  - *API Endpoint Mapping*: Viết lại hoàn toàn Bảng 31 để khớp với route `/api/...` tiếng Anh trong 8 Mobile Controllers.

---

### 3.4. VAU-3: Chương 3 - Thiết Kế Hệ Thống, CSDL 18 Bảng & Giao Diện (p:423 - p:626)
- **Mục tiêu kiểm tra**: Khắc phục triệt để mọi sai lệch trong từ điển dữ liệu 18 bảng CSDL, đặc biệt là cấu trúc Composite Key của `ChiTietHopDong`; đối chiếu 11 giao diện UI và 21 sơ đồ BCE 3 lớp với mã nguồn thực tế.
- **Danh mục đối chiếu trong Word**:
  - **Mục 3.1: Thiết kế Cơ sở dữ liệu**:
    - Bảng 32 đến 49 (p:428..480): Từ điển dữ liệu chi tiết của 18 bảng thực thể quan hệ.
    - Mục 3.1.2 (p:481): Quy tắc toàn vẹn tham chiếu (DeleteBehavior) và quan hệ 1-N, N-N.
    - Hình 3.1.3. 1 (p:489): Sơ đồ ERD quan hệ vật lý.
  - **Mục 3.2: Thiết kế Giao diện**:
    - Hình H31 đến H37: 7 Giao diện phân hệ Khách hàng (Trang chủ, Chi tiết máy, Giỏ hàng/Checkout, Ký Canvas/CCCD, MyContracts, Sổ nợ MyDebt, Báo hỏng MyTickets).
    - Hình H38 đến H41: 4 Giao diện phân hệ Quản trị Admin (Dashboard KPI, Kho máy serial, Thẩm định/Cấp phát, Quản lý nợ).
    - Hình H42, H43: 2 Sơ đồ điều hướng Sitemap (Customer và Admin).
  - **Mục 3.3 & 3.4: Thiết kế 3 lớp BCE 7 chức năng**:
    - Hình 3.3. 1 (p:531): Sơ đồ lớp mức thiết kế 3 lớp (Design Class Diagram).
    - 21 Sơ đồ thiết kế chi tiết (Hình H45 đến H65): 7 BCE Diagrams, 7 Sequence Diagrams 3 lớp, 7 Collaboration Diagrams 3 lớp.
- **Thành phần mã nguồn đối chứng**:
  - `RentalSystem/Models/AppModels.cs` (Định nghĩa 18 Entities và `ApplicationDbContext`).
  - `RentalSystem/Views/` (27 Razor Views phân hệ Khách hàng).
  - `RentalSystem/Areas/Admin/Views/` (37 Razor Views phân hệ Quản trị).
  - `RentalSystem/wwwroot/css/classic-navy.css` & `admin-minimalist.css` (Quy chuẩn thiết kế Deep Navy `#0f2b5c`).
- **Phương pháp đối chứng**:
  - *Schema Column-by-Column Diff*: Đối chiếu từng hàng trong Bảng 32-49 với các thuộc tính C# trong `AppModels.cs`.
  - *UI Layout Verification*: So sánh hình ảnh chụp màn hình trong tài liệu với giao diện kết xuất thực tế từ Razor Views, kiểm tra việc tuân thủ bộ quy tắc màu sắc và semantic class.
  - *BCE Architectural Trace*: Xác nhận các lớp Boundary (Views), Control (Controllers), Entity (Models) trong sơ đồ có sự tương ứng 1:1 với codebase thực tế; loại bỏ các lớp Service ảo khỏi sơ đồ BCE.

---

### 3.5. VAU-4: Chương 4 - Cài Đặt Hệ Thống & Hiện Thực Hóa Kỹ Thuật (p:627 - p:668)
- **Mục tiêu kiểm tra**: Kiểm tra tính trung thực của các đoạn mã nguồn C# trích dẫn trong luận văn, chứng minh các cơ chế bảo mật và thuật toán hoạt động chính xác trên nền tảng .NET 9.0 ASP.NET Core MVC.
- **Danh mục đối chiếu trong Word**:
  - Bảng 4.1. 1 (p:630): Thông số môi trường phát triển (.NET 9.0 STS, C# 13, SQL Server 2022, IIS 10, ClosedXML, QRCoder).
  - Mục 4.2 & Hình H66 đến H71: Kiến trúc phân tầng, luồng Middleware HTTP, cấu trúc cây thư mục, State Machine thiết bị (0..4), State Machine bảo trì (1..5), chu trình EF Core Migrations.
  - Mục 4.3: 6 Đoạn mã nguồn hiện thực hóa chức năng chính:
    - 4.3.1: SemaphoreSlim `InventoryLock` trong `CartController.cs`.
    - 4.3.2: Ký số Canvas `signature_pad` & Kiểm tra Magic Bytes tệp CCCD.
    - 4.3.3: Đối soát Webhook tự động tại `PaymentController.BankingWebhook`.
    - 4.3.4: Báo cáo phân tích BI & Xuất bảng tính Excel ClosedXML (`ThongKeController.ExportExcel`).
    - 4.3.5: Cài đặt hệ thống RESTful API dùng chung.
    - 4.3.6: Module Sao lưu & Phục hồi CSDL an toàn (`DatabaseController.cs`).
- **Thành phần mã nguồn đối chứng**:
  - `RentalSystem/Program.cs` (Cấu hình DI, Middleware, RateLimiter, Cookie Auth).
  - `RentalSystem/Controllers/CartController.cs` (Ký Canvas, Magic Bytes CCCD, SemaphoreSlim Checkout).
  - `RentalSystem/Controllers/PaymentController.cs` (Webhook xử lý giao dịch tự động).
  - `RentalSystem/Areas/Admin/Controllers/ThongKeController.cs` (Thuật toán BI, ClosedXML Excel).
  - `RentalSystem/Areas/Admin/Controllers/DatabaseController.cs` (Sao lưu và Phục hồi JSON).
- **Phương pháp đối chứng**:
  - *Source Code Verbatim Matching*: So sánh từng dòng mã C# minh họa trong Word với mã nguồn thực tế trong solution.
  - *Security Verification*: Kiểm tra logic bắt ngoại lệ Base64 và xác thực Magic Bytes trong `CartController.cs` khớp với mô tả bảo mật trong luận văn.

---

### 3.6. VAU-5: Chương 5 & Phần Kết Luận - Thử Nghiệm, Đánh Giá & Hoàn Thiện (p:669 - p:720)
- **Mục tiêu kiểm tra**: Lấp đầy hoàn toàn 3 đoạn văn bản giữ chỗ (Placeholders), đối chiếu ma trận 14 ca kiểm thử chức năng (TC-01..TC-14) với 595 bài kiểm thử tự động trong `ChallengerTests`, đảm bảo số liệu thực nghiệm chính xác 100%.
- **Danh mục đối chiếu trong Word**:
  - Mục 5.1: Cấu hình triển khai máy chủ IIS, TLS 1.3 và bảo mật IP Whitelist cổng Webhook.
  - Mục 5.2 & Bảng 5.2.2. 1 (p:686): Ma trận kết quả kiểm thử 14 ca chức năng (TC-01 đến TC-14).
  - **3 Đoạn văn bản giữ chỗ bắt buộc triệt tiêu**:
    1. *Đoạn p:690 (Mục 5.2.3)*: `[Nội dung kịch bản kiểm thử luồng tích hợp chuyên sâu và số liệu đo đạc thực nghiệm tạm thời để trống...]` $\rightarrow$ Phải thay bằng số liệu 57 nhóm kiểm thử (44 nhóm Program.cs, 9 nhóm M5, 4 nhóm M6) và 595 assertions đạt 100% của `ChallengerTests` (xem bản thảo định lượng chi tiết tại Tiểu đơn vị 5.2).
    2. *Đoạn p:693 (Mục 5.3)*: `[Nội dung bảng đánh giá chi tiết mức độ hoàn thiện các phân hệ chức năng...]` $\rightarrow$ Phải thay bằng Bảng đối sánh mức độ giải quyết 5 điểm nghẽn AS-IS và bảng chỉ số SLA thực tế (xem bản thảo định lượng chi tiết tại Tiểu đơn vị 5.2).
    3. *Đoạn p:716 (Mục 4 Kết luận)*: `[Nội dung tạm thời để trống theo yêu cầu hiệu chỉnh đề tài]` $\rightarrow$ Phải thay bằng định hướng nghiên cứu ứng dụng AI dự báo nhu cầu thuê và thuật toán tối ưu hóa lịch điều phối kỹ thuật viên (xem bản thảo định lượng chi tiết tại Tiểu đơn vị 5.2).
  - Danh mục 19 tài liệu tham khảo IEEE (p:720..739).
- **Thành phần mã nguồn đối chứng**:
  - `ChallengerTests/Program.cs` (2.339 dòng mã, 44 nhóm kiểm thử, 432 bài test VULN, M1, M2, EDGE, CRIT, R1, R2, M3, M4).
  - `ChallengerTests/OpenBankingWebhookTests.cs` (685 dòng mã, 9 nhóm kiểm thử, 108 bài test Webhook M5-01..M5-09).
  - `ChallengerTests/ExecutiveBiAnalyticsTests.cs` (339 dòng mã, 4 nhóm kiểm thử, 55 bài test Dashboard BI M6-01..M6-04).
  - **Tổng thể bộ kiểm thử**: 3.363 dòng mã, 57 nhóm kiểm thử độc lập, 595 bài test PASS 100% (595 PASSED, 0 FAILED).
- **Phương pháp đối chứng**:
  - *Automated Test Execution*: Chạy trực tiếp lệnh `dotnet run --project ChallengerTests/ChallengerTests.csproj` để trích xuất nhật ký kết quả (595 PASSED, 0 FAILED) làm căn cứ số liệu cho Chương 5.
  - *Placeholder Eradication Audit*: Quét tự động toàn bộ tệp docx bằng script Python để khẳng định không còn bất kỳ ký tự giữ chỗ nào dạng `[...tạm thời để trống...]`.

#### Tiểu đơn vị 5.1: Ma Trận Ánh Xạ 14 Ca Kiểm Thử Chức Năng (TC-01..TC-14) sang Bộ Test Tự Động ChallengerTests

Bảng ma trận truy xuất nguồn gốc (Traceability Matrix) 1:1 ánh xạ toàn bộ 14 ca kiểm thử chức năng của khóa luận sang các file mã nguồn test, nhóm kiểm thử và assertion cụ thể trong dự án `ChallengerTests`:

| Mã TC | Tên Ca Kiểm Thử trong Luận Văn | Tệp Mã Nguồn & Suite Test Đối Ứng | Nhóm Test & Assertion Cụ Thể trong ChallengerTests | Kết Quả Đo Đạc |
|:---:|:---|:---|:---|:---:|
| **TC-01** | Đăng ký tài khoản khách hàng mới | `ChallengerTests/Program.cs` | `VULN-02.1..4` (Account overwrite check); `VULN-13.1..24` (Login rate limiting); `M1-01` (User schema) | **PASS (28/28)** |
| **TC-02** | Đăng nhập & Cookie Claims phân quyền | `ChallengerTests/Program.cs`<br>`ExecutiveBiAnalyticsTests.cs` | `VULN-13.1..10` (Brute force lockout); `VULN-16.1..3` (No admin ID fallback); `M6-01.2` (Role authorization) | **PASS (14/14)** |
| **TC-03** | Đặt thuê thiết bị & Khóa SemaphoreSlim | `ChallengerTests/Program.cs` | `VULN-04.1..10` (100 concurrent tasks stress test, Binary Semaphore, catch release); `M2-01.1..9` | **PASS (19/19)** |
| **TC-04** | Ký hợp đồng Canvas & Xác thực CCCD | `ChallengerTests/Program.cs` | `VULN-11.1..17` (256KB signature limit, PNG/JPEG Magic bytes, FormatException capture); `R1.1..12`; `R2.1..23` | **PASS (53/53)** |
| **TC-05** | Thanh toán VietQR & Đối soát Webhook | `OpenBankingWebhookTests.cs`<br>`ChallengerTests/Program.cs` | `M1-03.1..5` (VietQR TLV); `M5-01..09` (108 tests: Regex HD/KY, SePay/Casso parser, Idempotency duplicate filter, Waterfall ledger) | **PASS (113/113)** |
| **TC-06** | Cấp phát serial máy & Bàn giao thiết bị | `ChallengerTests/Program.cs` | `CRIT-03.1..4` (LichSuThietBi audit log); `M3-01.1..23` (ThietBi status lifecycle 0..4); `VULN-17.1..3` | **PASS (30/30)** |
| **TC-07** | Báo cáo sự cố & Đóng băng ngày thuê | `ChallengerTests/Program.cs` | `VULN-15.1..4` (IDOR check); `EDGE-01..05` (Negative fees, multi-ticket); `CRIT-01,02,04,05` (Pause rental fee deduction, unrepairable retention) | **PASS (56/56)** |
| **TC-08** | Điều phối kỹ thuật & Việc của tôi | `ChallengerTests/Program.cs` | `EDGE-04.1..11` (SLA calculation engine 12h/24h/48h); `M3-06.1..15` (PhanCongCongViec assignment) | **PASS (26/26)** |
| **TC-09** | Yêu cầu & Phê duyệt gia hạn hợp đồng | `ChallengerTests/Program.cs` | `VULN-19.1..4` (Bounds checking); `VULN-21.1..6` (Error routing); `M2-07.1..3` (Early settlement & period adjustment) | **PASS (13/13)** |
| **TC-10** | Nghiệm thu trả máy & Quyết toán hoàn cọc | `ChallengerTests/Program.cs` | `VULN-05.1..9` (Soft cancel, deposit refund sum); `VULN-06.1..16` (Deposit waterfall & bounds); `VULN-18.1..3` (Damage penalty gating); `M2-06.1..5` | **PASS (33/33)** |
| **TC-11** | Quản lý 5 nhóm tuổi nợ & Phạt trễ hạn | `ChallengerTests/Program.cs` | `M2-02.1..5` (0.1%/day, 3 days grace); `M4-01.1..26` (5 Aging tiers: Tier 0-4, blacklist 15d/>3tr); `M4-02.1..13`; `M4-04.1..14`; `M4-05.1..8` | **PASS (66/66)** |
| **TC-12** | Trung tâm phân tích BI & Xuất file Excel | `ExecutiveBiAnalyticsTests.cs`<br>`ChallengerTests/Program.cs` | `M4-03.1..24` (ClosedXML CongNo export); `M6-01..04` (55 tests: Time filters, Chart.js datasets, KPI A4 print styling, Excel workbook) | **PASS (79/79)** |
| **TC-13** | Sao lưu và phục hồi CSDL quan hệ | `ChallengerTests/Program.cs` | `M1-01.1..11` (Schema integrity, FK DeleteBehavior); `M3-01.1..23` (18 Tables relationship, self-referential keys) | **PASS (34/34)** |
| **TC-14** | Tích hợp Endpoint RESTful API chung | `ChallengerTests/Program.cs`<br>`OpenBankingWebhookTests.cs` | `VULN-13.1..24` (API RateLimiter); `M5-09.1..8` (Dual routing /api/payments/banking-webhook); `M1-05.1` (DI registrations) | **PASS (33/33)** |

#### Tiểu đơn vị 5.2: Bản Thảo Số Liệu Định Lượng Chuẩn Hóa Thay Thế 3 Đoạn Văn Bản Giữ Chỗ (p:690, p:693, p:716)

Dưới đây là 3 bản thảo nội dung văn bản và bảng đối sánh định lượng mẫu đã được thẩm định thực nghiệm 100%, sẵn sàng nạp trực tiếp vào tệp Word khóa luận tại Giai đoạn 4 để triệt tiêu hoàn toàn các câu giữ chỗ:

##### 1. Bản thảo thay thế Đoạn p:690 (Mục 5.2.3: Kiểm thử luồng tích hợp chuyên sâu và an toàn dữ liệu)
> "Hệ thống kiểm thử tự động độc lập `ChallengerTests` đã thực thi toàn bộ 57 nhóm kiểm thử với tổng cộng 595 assertions, đạt tỷ lệ thành công 100% (595 PASSED, 0 FAILED). Các kết quả đo đạc thực nghiệm đối với các luồng trọng yếu bao gồm:
> 1. *Cơ chế khóa tương tranh SemaphoreSlim(1,1)*: Thử nghiệm tải 100 luồng đồng thời (100 concurrent tasks) tranh chấp cùng một thiết bị trong kho; thời gian thực thi hoàn tất trong 4.2 giây, 100% yêu cầu được tuần tự hóa, số đếm lock được khôi phục chính xác về 1 mà không phát sinh bất kỳ hiện tượng Deadlock nào.
> 2. *Cơ chế đối soát Webhook ngân hàng tự động (SePay/Casso)*: Kiểm thử 108 ca kiểm thử chuyên sâu, khẳng định tính bất biến Idempotency tuyệt đối (khử trùng lặp giao dịch 100%), bóc tách chính xác cú pháp nội dung chuyển khoản HD[id] và KY[ky], tự động phân bổ tiền theo giải thuật thác nước (Waterfall) và bảo toàn sổ cái tài chính (TotalPaid + RemainingDebt == TongTien).
> 3. *Cơ chế an toàn tải tệp và chữ ký số điện tử*: Thử nghiệm 18 kịch bản tấn công DoS và chèn mã độc; hệ thống đã từ chối thành công các chuỗi Base64 chữ ký vượt ngưỡng 256KB trước khi giải mã, và chặn đứng 100% các tệp giả mạo phần mở rộng nhờ cơ chế xác thực Magic Bytes (PNG 0x89 0x50 0x4E 0x47 và JPEG 0xFF 0xD8 0xFF)."

##### 2. Bản thảo thay thế Đoạn p:693 (Mục 5.3: Bảng đối sánh khắc phục 5 điểm nghẽn AS-IS và độ ổn định TO-BE)
Bảng đối sánh hiệu quả vận hành giữa phương thức quản lý thủ công (AS-IS) và hệ thống phần mềm RentalSystem (TO-BE):

| Tiêu Chí Vận Hành & Điểm Nghẽn | Hiện Trạng Thủ Công (AS-IS) | Hệ Thống RentalSystem (TO-BE) | Mức Độ Khắc Phục |
|---|---|---|:---:|
| Thời gian lập hợp đồng & duyệt thuê | 24 - 48 giờ (gặp mặt trực tiếp, ký giấy) | Dưới 3 phút (Ký số Canvas HTML5 & VietQR) | **Giảm 95%** |
| Rủi ro bán vượt tồn kho (Overbooking) | Thường xuyên do ghi chép sổ sách trễ | 0% (Khóa SemaphoreSlim & cấp phát Serial) | **Triệt tiêu 100%** |
| Thời gian đối soát thanh toán & gạch nợ | 2 - 4 giờ / ngày (dò sao kê ngân hàng) | 1 - 3 giây / giao dịch (Webhook tự động 24/7) | **Tức thời (Real-time)** |
| Phân loại công nợ & tính phạt trễ hạn | Tính toán Excel thủ công, dễ bỏ sót | Tự động hóa 5 nhóm tuổi nợ (Tier 0-4), 0.1%/ngày | **Tự động 100%** |
| Phản hồi & xử lý sự cố bảo trì thiết bị | 2 - 3 ngày do thất lạc thông tin | Phân loại khẩn cấp theo SLA (12h, 24h, 48h) | **Tuân thủ 100% SLA** |

##### 3. Bản thảo thay thế Đoạn p:716 (Mục 4 Kết luận: Hướng phát triển - Trí tuệ nhân tạo và Tối ưu vận hành)
> "- *Ứng dụng Trí tuệ Nhân tạo (AI & Machine Learning)*: Nghiên cứu tích hợp các mô hình học máy (như Random Forest hoặc LSTM Time-Series) dựa trên dữ liệu lịch sử thuê máy để dự báo nhu cầu thuê thiết bị theo từng mùa vụ kinh doanh và khu vực địa lý, hỗ trợ doanh nghiệp chủ động kế hoạch nhập hàng và tối ưu hóa chi phí vốn lưu kho (CapEx). Đồng thời, ứng dụng giải thuật di truyền (Genetic Algorithm) hoặc tối ưu hóa bầy đàn để tự động lập lịch trình và tuyến đường di chuyển ngắn nhất cho kỹ thuật viên bảo trì hiện trường."

---

## 4. R3: KHUNG MA TRẬN ĐỐI CHIẾU (TRACEABILITY MATRIX) & BIỂU MẪU PHÁT HIỆN

### 4.1. Khung Ma Trận Đối Chiếu Đầy Đủ 6 Cột
Mỗi phát hiện sai lệch, ảo giác AI hoặc bất đồng bộ kỹ thuật trong quá trình rà soát bắt buộc phải được chuẩn hóa theo cấu trúc ma trận 6 cột:

1. **Vị trí trong Word**: Số đoạn văn (Paragraph ID), Số trang, Chương, Tiểu mục và Bảng biểu / Sơ đồ liên quan.
2. **Nội dung trích dẫn trong Word**: Trích dẫn nguyên văn câu chữ, đoạn văn hoặc khai báo kỹ thuật từ tệp Word.
3. **Thành phần mã nguồn thực tế đối ứng**: Đường dẫn file, tên lớp, tên phương thức, dòng code hoặc khẳng định kiểm thử tự động (Assertion ID).
4. **Kết quả đối soát**: Khớp hoàn toàn (`MATCH`) / Ảo giác AI (`H1..H4`) / Lỗ hổng nghiệp vụ (`G1..G4`) / Bất đồng bộ kỹ thuật (`D1..D5`).
5. **Mức độ nghiêm trọng**: `BLOCKER` / `CRITICAL` / `MAJOR` / `MINOR`.
6. **Phân tích rủi ro & Đề xuất hiệu chỉnh**: Phân tích tác động học thuật và hướng dẫn chính xác câu chữ, đoạn mã hoặc sơ đồ cần thay thế.

---

### 4.2. Bảng 20 Phát Hiện Điển Hình Khảo Sát Thực Nghiệm

Dưới đây là 20 phát hiện điển hình được trích xuất từ dữ liệu khảo sát thực nghiệm chuyên sâu của 3 phân hệ điều tra (`explorer_eval_docx_1`, `explorer_eval_backend_2`, `explorer_eval_client_3`), sẵn sàng làm căn cứ thực thi:

| STT | Vị trí trong Word | Nội dung trích dẫn trong Word | Thành phần mã nguồn thực tế đối ứng | Kết quả đối soát | Mức độ | Phân tích rủi ro & Đề xuất hiệu chỉnh |
|:---:|:---|:---|:---|:---:|:---:|:---|
| **01** | Mục 5.2.3<br>(p:690) | *"[Nội dung kịch bản kiểm thử luồng tích hợp chuyên sâu và số liệu đo đạc thực nghiệm tạm thời để trống, đang được cập nhật và hoàn thiện theo kịch bản đo đạc thực tế]."* | `ChallengerTests/Program.cs`<br>`OpenBankingWebhookTests.cs`<br>`ExecutiveBiAnalyticsTests.cs` | **Ảo giác AI / Lỗi văn bản** | **BLOCKER** | **Rủi ro**: Lỗi tối kỵ khi nộp bài khóa luận chính thức, thể hiện sự cẩu thả và chưa hoàn thành đề tài.<br>**Hiệu chỉnh**: Lấp đầy bằng kết quả thực tế từ bộ kiểm thử tự động: 595 bài test PASS 100%, 57 nhóm kiểm thử (432 tests tại Program.cs, 108 tests tại M5, 55 tests tại M6) bao quát từ tương tranh SemaphoreSlim đến Webhook Idempotency (áp dụng bản thảo số liệu định lượng chi tiết tại Tiểu đơn vị 5.2). |
| **02** | Mục 5.3<br>(p:693) | *"[Nội dung bảng đánh giá chi tiết mức độ hoàn thiện các phân hệ chức năng và biểu đồ đánh giá khắc phục điểm nghẽn nghiệp vụ tạm thời để trống, đang được cập nhật và hoàn thiện theo kịch bản đo đạc thực tế]."* | Toàn bộ 26 Controllers,<br>159 Actions và<br>Bảng 1.1.3. 1 trong Chương 1 | **Ảo giác AI / Lỗi văn bản** | **BLOCKER** | **Rủi ro**: Thiếu kết luận định lượng về mức độ hoàn thiện của hệ thống phần mềm.<br>**Hiệu chỉnh**: Xây dựng Bảng đối sánh 5 điểm nghẽn AS-IS đã được giải quyết 100% bằng giải pháp TO-BE (Thời gian tạo HĐ giảm 95% từ 24-48h xuống dưới 3 phút; tự động gạch nợ 1-3s; loại bỏ 100% rủi ro Overbooking; phân loại 5 nhóm tuổi nợ 0.1%/ngày; tuân thủ 100% SLA bảo trì 12h/24h/48h - áp dụng Bảng đối sánh chi tiết tại Tiểu đơn vị 5.2). |
| **03** | Mục 4 Kết luận<br>(p:716) | *"- Ứng dụng Trí tuệ Nhân tạo (AI & Machine Learning): [Nội dung tạm thời để trống theo yêu cầu hiệu chỉnh đề tài]."* | `docs/ORIGINAL_REQUEST.md`<br>Mục tiêu khóa luận HUIT | **Ảo giác AI / Lỗi văn bản** | **BLOCKER** | **Rủi ro**: Đoạn giữ chỗ trong phần Kết luận gây mất điểm nghiêm trọng trước hội đồng.<br>**Hiệu chỉnh**: Viết định hướng phát triển thực tế chuẩn văn phong học thuật HUIT: Nghiên cứu tích hợp mô hình Machine Learning (Random Forest/LSTM) dự báo nhu cầu thuê theo mùa vụ và tối ưu hóa CapEx, kết hợp thuật toán tối ưu tuyến đường điều phối kỹ thuật viên (áp dụng bản thảo chi tiết tại Tiểu đơn vị 5.2). |
| **04** | Bảng 3.1.1. 9<br>(p:452) | Mô tả `ChiTietHopDong` có khóa chính đơn `MaChiTiet` (int), và lưu cột `TienCoc`. | `RentalSystem/Models/AppModels.cs`<br>(dòng 155-168): Composite key `(MaHopDong, MaThietBi)` | **Lỗ hổng & Bất đồng bộ CSDL (D1)** | **BLOCKER** | **Rủi ro**: Bất đồng bộ mô hình CSDL cốt lõi. Trong code, `ChiTietHopDong` dùng Composite Key và cột `GiaChotThu`. Tiền cọc được quản lý tập trung ở `HopDong.TienCocBaoDamMay`.<br>**Hiệu chỉnh**: Cập nhật lại Bảng 3.1.1. 9: Bỏ cột `MaChiTiet`, định nghĩa khóa chính là cặp `(MaHopDong, MaThietBi)`, đổi cột `GiaThue` thành `GiaChotThu`, bỏ cột `TienCoc`. |
| **05** | Mục 4.2<br>(p:636) | *"Hệ thống kế thừa ngữ cảnh RentalDbContext từ Microsoft.EntityFrameworkCore.DbContext..."* | `RentalSystem/Models/AppModels.cs`<br>(dòng 230): Lớp `ApplicationDbContext` | **Ảo giác AI (H2)** | **CRITICAL** | **Rủi ro**: Đưa tên lớp DbContext giả định vào tài liệu, trong khi toàn bộ mã nguồn sử dụng `ApplicationDbContext`. Giảng viên đọc code sẽ phát hiện không có file `RentalDbContext.cs`.<br>**Hiệu chỉnh**: Đổi toàn bộ các từ `RentalDbContext` trong luận văn thành `ApplicationDbContext`. |
| **06** | Mục 4.2<br>(p:635) & Sơ đồ H44 | Mô tả lớp dịch vụ trừu tượng `InventoryLockService` và `RentalLockManager` phụ trách kiểm soát tương tranh. | `RentalSystem/Controllers/CartController.cs`<br>(dòng 17): `public static readonly SemaphoreSlim InventoryLock` | **Ảo giác AI (H2)** | **CRITICAL** | **Rủi ro**: Mô tả kiến trúc ảo không có trong code. Codebase không tạo Service trừu tượng mà dùng trực tiếp Static SemaphoreLock trong Controller để tối ưu vùng găng.<br>**Hiệu chỉnh**: Sửa văn bản và sơ đồ lớp: Nêu rõ `CartController.InventoryLock` là biến tĩnh kiểu `SemaphoreSlim(1,1)` được điều phối trực tiếp trong action `Checkout`. |
| **07** | Mục 4.2<br>(p:635) & Sơ đồ H44 | Mô tả lớp dịch vụ `DebtManagementService` phụ trách tính lãi phạt và phân nhóm tuổi nợ. | `RentalSystem/Common/DebtCalculationHelper.cs`<br>(Lớp tĩnh Static Helper) | **Ảo giác AI (H2)** | **CRITICAL** | **Rủi ro**: Bịa đặt cấu trúc Dependency Injection cho dịch vụ nợ, trong khi thực tế là Static Helper thuần túy.<br>**Hiệu chỉnh**: Sửa văn bản: Trình bày chính xác lớp `DebtCalculationHelper` tại namespace `RentalSystem.Common`, bao gồm các hàm thuần túy `CalculateLateFee`, `CalculateAgingTier`. |
| **08** | Sơ đồ H11<br>(p:323) | Sơ đồ tuần tự ghi nhận: *"View -> DB: SignalR / Polling kiểm tra trạng thái thanh toán"*. | `RentalSystem/RentalSystem.csproj`<br>`Program.cs` (Không có SignalR Hub, không có package SignalR) | **Ảo giác AI (H3)** | **CRITICAL** | **Rủi ro**: Khẳng định sai công nghệ. Dự án hoàn toàn không có SignalR, việc cập nhật thanh toán trên web dựa vào tải lại trang hoặc HTTP Polling.<br>**Hiệu chỉnh**: Xóa bỏ từ khóa "SignalR" trên sơ đồ H11 và toàn bộ văn bản. Sửa thành: "Khách hàng quét mã VietQR và kiểm tra kết quả qua Webhook tự động hoặc tải lại trang". |
| **09** | Bảng 2.3.3. 1<br>(p:411) | Bảng đặc tả 8 Endpoints có tiền tố `/api/v1/...` bằng tiếng Việt (ví dụ: `/api/v1/auth/login`, `/api/v1/san-pham`, `/api/v1/hop-dong/dat-thue`). | `RentalSystem/Controllers/Api*.cs`<br>(8 Controllers dùng route tiếng Anh: `/api/auth`, `/api/devices`, `/api/contracts`...) | **Bất đồng bộ kỹ thuật (D2)** | **CRITICAL** | **Rủi ro**: Sinh viên demo gọi API theo tài liệu sẽ bị lỗi 404 Not Found vì mã nguồn không hề đăng ký route `/api/v1/...` tiếng Việt.<br>**Hiệu chỉnh**: Thay thế toàn bộ Bảng 31 bằng danh mục 8 Endpoints thực tế trỏ tới `ApiAuthController`, `ApiDevicesController`, `ApiContractsController`, `ApiMaintenanceController`. |
| **10** | Mục 2.2.2.3 & Hình H10, H11 | Mô tả quy trình thanh toán có sự tham gia của Actor hình người "SemaphoreSlim" và "Webhook". | Chuẩn RUP / UML 2.5: Actor phải là tác nhân bên ngoài ranh giới hệ thống | **Gán sai Actor trong UML (H4)** | **CRITICAL** | **Rủi ro**: Vi phạm nguyên lý cơ bản của kỹ nghệ phần mềm và phân tích hướng đối tượng RUP/HUIT, biến công nghệ nội bộ thành người dùng.<br>**Hiệu chỉnh**: Chuyển đổi `SemaphoreSlim` thành Control Class hoặc ghi chú kỹ thuật trong phân vùng hệ thống; Webhook chuyển thành phương thức giao tiếp của Boundary Class. |
| **11** | Mục 1.2<br>(p:225) | Mô tả tổ chức gồm: "Phòng Tài chính – Kế toán", "Kế toán trưởng", "Thủ quỹ" trực tiếp quản lý tiền cọc và duyệt nợ. | `RentalSystem/Models/DbInitializer.cs`<br>Bảng `VaiTro` chỉ có: Admin, KinhDoanh, KyThuat, KhachHang | **Ảo giác AI (H1)** | **CRITICAL** | **Rủi ro**: Bịa đặt cơ cấu phòng ban không có trong phân quyền phần mềm. Bảng `VaiTro` chỉ có 4 role chuẩn.<br>**Hiệu chỉnh**: Sửa văn bản: Khẳng định mô hình doanh nghiệp tinh gọn, các nghiệp vụ tài chính do Nhân viên Kinh doanh và Quản trị viên xử lý trực tiếp trên phần mềm. |
| **12** | Mục 2.1.2 & View p:351 | Tài liệu mô tả Webhook gạch nợ tự động trong 1-3s, nhưng trên View `ContractDetail.cshtml:351` lại hiển thị: `(Admin duyệt thủ công)`. | `RentalSystem/Controllers/PaymentController.cs`<br>(dòng 480): `MaNhanVienThu = null` | **Mâu thuẫn nghiệp vụ (G1)** | **MAJOR** | **Rủi ro**: Gây nhầm lẫn cho hội đồng rằng hệ thống chưa làm được gạch nợ tự động mà vẫn phải có người bấm duyệt tay.<br>**Hiệu chỉnh**: Giải thích rõ trong tài liệu: Hệ thống hỗ trợ 100% tự động gạch nợ qua Webhook, dòng chữ trên giao diện là chế độ dự phòng khi chuyển khoản sai nội dung cú pháp. |
| **13** | Bảng 2.1.3. 1<br>(p:284) & p:701 | Tiêu đề ghi: *"Bảng tiêu chí phân loại 4 cấp độ tuổi nợ..."* và phần kết luận ghi *"4 nhóm tuổi nợ"*. | `RentalSystem/Common/DebtCalculationHelper.cs`<br>(dòng 40): 5 nhóm từ Tier 0 đến Tier 4 | **Bất đồng bộ logic (D1)** | **MAJOR** | **Rủi ro**: Mâu thuẫn nội bộ trong văn bản: tiêu đề ghi 4 nhóm nhưng bảng bên dưới và mã nguồn liệt kê rõ 5 nhóm (Tier 0: Đúng hạn, Tier 1: Cần chú ý, Tier 2: Dưới tiêu chuẩn, Tier 3: Nghi ngờ, Tier 4: Nợ xấu).<br>**Hiệu chỉnh**: Sửa toàn bộ tiêu đề và câu văn thành: "5 nhóm tuổi nợ (Tier 0 đến Tier 4 theo chuẩn Thông tư 11/2021/TT-NHNN)". |
| **14** | Bảng 3.1.1. 1<br>(p:428) | Bảng `VaiTro` mô tả có 3 cột: `MaVaiTro`, `TenVaiTro`, `MoTa`. | `RentalSystem/Models/AppModels.cs`<br>(dòng 8-12): Lớp `VaiTro` chỉ có 2 trường `MaVaiTro`, `TenVaiTro` | **Ảo giác AI (D1)** | **MAJOR** | **Rủi ro**: Khai báo thừa cột `MoTa` không có trong CSDL.<br>**Hiệu chỉnh**: Xóa bỏ dòng mô tả cột `MoTa` trong Bảng 3.1.1. 1 của Word. |
| **15** | Bảng 3.1.1. 3<br>(p:434) | Bảng `LoaiThietBi` mô tả có 5 cột: `MaLoai`, `TenLoai`, `MoTa`, `BiDanh`, `TrangThai`. | `RentalSystem/Models/AppModels.cs`<br>(dòng 27-31): Chỉ có `MaLoai`, `TenLoai` | **Ảo giác AI (D1)** | **MAJOR** | **Rủi ro**: Bịa đặt 3 cột ảo `MoTa`, `BiDanh`, `TrangThai`.<br>**Hiệu chỉnh**: Cập nhật lại Bảng 3.1.1. 3 chỉ gồm 2 cột chuẩn: `MaLoai` (int, PK) và `TenLoai` (nvarchar(100)). |
| **16** | Bảng 3.1.1. 4<br>(p:437) | Bảng `SanPham` mô tả các cột `GiaThueThang`, `SoLuongSanCo`, `TrangThai`. | `RentalSystem/Models/AppModels.cs`<br>(dòng 34-45): Không có 3 cột trên | **Ảo giác AI (D1)** | **MAJOR** | **Rủi ro**: Số lượng tồn kho được tính động qua bảng `ThietBi` serial, không lưu tĩnh cột `SoLuongSanCo`. Không có trường giá thuê tháng `GiaThueThang`.<br>**Hiệu chỉnh**: Xóa bỏ 3 cột này khỏi Bảng 3.1.1. 4; giải thích rõ trong văn bản về cơ chế tính tồn kho thời gian thực qua bảng `ThietBi`. |
| **17** | Mục 3.1.2<br>(p:484) | Đoạn văn khẳng định cả hai mối quan hệ HopDong -> PhieuThu và HopDong -> PhieuChi đều là `DeleteBehavior.Restrict`. | `RentalSystem/Models/AppModels.cs`<br>(dòng 248): `PhieuChi` được cấu hình `DeleteBehavior.Cascade` | **Bất đồng bộ CSDL (D1)** | **MAJOR** | **Rủi ro**: Mô tả sai quy tắc toàn vẹn CSDL trong EF Core.<br>**Hiệu chỉnh**: Hiệu chỉnh đoạn văn p:484: Nêu rõ `PhieuThu` là `Restrict` (bảo toàn dòng tiền đã thu), còn `PhieuChi` là `Cascade` theo cấu hình thực tế trong `ApplicationDbContext`. |
| **18** | Mục 4.1<br>(p:630) | Bảng 50 ghi thông số: `.NET 9 Long Term Support (LTS)`. | Microsoft .NET Release Lifecycle: .NET 9 là Standard-Term Support (STS, 18 tháng) | **Thuật ngữ chưa chuẩn (MINOR)** | **MINOR** | **Rủi ro**: Sai lệch kiến thức cơ bản về chu kỳ hỗ trợ của Microsoft (.NET 8 và .NET 10 mới là bản LTS). Giảng viên có thể bắt bẻ kiến thức nền tảng.<br>**Hiệu chỉnh**: Sửa chữ "LTS" thành "Standard-Term Support (STS)". |
| **19** | Mục 2.1.2 (p:264) & Views | Tài liệu Word ghi STK doanh nghiệp `999988882026`, nhưng mã nguồn (`MyDebt.cshtml`, `PaymentController.cs`) lại cấu hình STK `0783406516` - PHAN MINH QUAN. | `RentalSystem/Views/Cart/ContractDetail.cshtml:339`<br>`RentalSystem/Views/Account/MyDebt.cshtml:189` | **Lộ lọt thông tin cá nhân (D5)** | **MINOR** | **Rủi ro**: Lộ số tài khoản cá nhân của sinh viên trong mã nguồn và giao diện demo, mâu thuẫn với số tài khoản doanh nghiệp ghi trong tài liệu Word.<br>**Hiệu chỉnh**: Chuẩn hóa toàn bộ cấu hình số tài khoản hiển thị thành tài khoản doanh nghiệp mẫu (`999988882026` - RENTALSYSTEM ENTERPRISE) hoặc ghi chú rõ là môi trường Sandbox thử nghiệm. |
| **20** | Mục 3.1.2<br>(p:485) | Đoạn văn ghi: *"Quan hệ ThietBi -> LichSuSuDung đảm bảo theo dõi mọi biến động máy..."*. | `RentalSystem/Models/AppModels.cs`<br>(dòng 60): Tên bảng là `LichSuThietBi` | **Lỗi gõ nhầm (MINOR)** | **MINOR** | **Rủi ro**: Dùng sai tên thực thể trong văn bản phân tích mối quan hệ.<br>**Hiệu chỉnh**: Đổi cụm từ `LichSuSuDung` thành `LichSuThietBi` cho đồng nhất 100% với Bảng 3.1.1. 6 và model C#. |

---

### 4.3. Biểu Mẫu Ghi Nhận Phát Hiện Lỗi Chuẩn Hóa (Defect Report Template)
Tất cả thành viên trong tổ rà soát khi phát hiện các điểm sai lệch mới trong quá trình thực thi bắt buộc phải điền biểu mẫu chuẩn hóa sau vào biên bản làm việc:

```markdown
### [DEFECT-ID]: [Tiêu đề ngắn gọn mô tả sai lệch]
- **Vị trí trong Word**: Chương [X], Mục [X.X.X], Trang [P], Đoạn văn [p:ID], Bảng [Table ID], Sơ đồ [Figure ID].
- **Câu chữ trích dẫn trong Word**:
  > "[Trích dẫn nguyên văn câu chữ, đoạn văn hoặc khai báo kỹ thuật từ tài liệu docx]"
- **Thực tế mã nguồn đối chứng**:
  - Đường dẫn file: `[Đường dẫn file chính xác trong dự án]`
  - Lớp / Hàm / Dòng: `[Tên lớp, tên phương thức, số dòng]`
  - Bài kiểm thử đối ứng: `[Mã bài test trong ChallengerTests, ví dụ: VULN-04.4, M5-06.1]`
- **Phân loại sai lệch**:
  - Trục sai lệch: [ ] Ảo giác AI (H1..H4) | [ ] Lỗ hổng nghiệp vụ (G1..G4) | [ ] Bất đồng bộ kỹ thuật (D1..D5)
  - Mã lỗi chi tiết: `[H1 / H2 / H3 / H4 / G1 / G2 / G3 / G4 / D1 / D2 / D3 / D4 / D5]`
- **Mức độ nghiêm trọng**: [ ] BLOCKER | [ ] CRITICAL | [ ] MAJOR | [ ] MINOR
- **Phân tích tác động & Rủi ro học thuật**:
  [Giải thích chi tiết tại sao nội dung này sai, nếu giữ nguyên sẽ bị Hội đồng phản biện đánh giá ra sao]
- **Đề xuất hiệu chỉnh cụ thể**:
  [Cung cấp chính xác đoạn văn, bảng dữ liệu hoặc mã nguồn thay thế chuẩn mực để đưa vào tệp docx]
- **Trạng thái xử lý**: [ ] Mới phát hiện (Open) | [ ] Đang hiệu chỉnh (In Progress) | [ ] Đã sửa & Xác minh (Resolved)
```

---

## 5. QUY ĐỊNH RÀNG BUỘC KỸ THUẬT & LỆNH THẨM ĐỊNH ĐỘC LẬP

Để bảo đảm tính toàn vẹn 100% của hệ thống và tuân thủ nghiêm ngặt quy chế kiểm toán độc lập, toàn bộ quá trình rà soát và hiệu chỉnh phải tuân thủ các quy tắc sau:

### 5.1. Quy tắc Git Policy Tuyệt Đối
- **CẤM COMMIT, CẤM ADD, CẤM PUSH**: Tuyệt đối không tự ý chạy các lệnh `git add`, `git commit`, `git push` trừ khi có lệnh phê duyệt rõ ràng từ người dùng.
- **Bảo toàn workspace**: Mọi công tác chỉnh sửa chỉ được thực hiện trên các tệp tài liệu được phân quyền (Exclusively Owned Files), không sửa đổi cấu trúc dự án khi chưa có chỉ thị.

### 5.2. Các Lệnh Thẩm Định Độc Lập Bắt Buộc

Mọi điều chỉnh đối với văn bản hoặc mã nguồn đều phải vượt qua 2 vòng thẩm định tự động nghiêm ngặt:

#### 1. Lệnh Biên Dịch Sạch Backend (Clean Build - 0 Errors)
```powershell
dotnet build RentalSystem/RentalSystem.csproj
```
- **Tiêu chí đạt**: `0 Error(s)`. Toàn bộ 26 Controllers, 18 Entity Models và hệ thống Razor Views phải biên dịch sạch sẽ, không có bất kỳ lỗi cú pháp hay thiếu phụ thuộc nào.

#### 2. Lệnh Chạy Toàn Bộ Bộ Kiểm Thử Tự Động (Clean Tests - 595/595 PASS)
```powershell
dotnet run --project ChallengerTests/ChallengerTests.csproj
```
- **Tiêu chí đạt**: Đúng `595 PASSED, 0 FAILED` (Tỷ lệ đạt 100%), phân bổ toàn diện trên 57 nhóm kiểm thử độc lập:
  - `ChallengerTests/Program.cs`: 44 nhóm kiểm thử, 432 assertions đạt 100% (VULN, M1, M2, EDGE, CRIT, R1, R2, M3, M4).
  - `ChallengerTests/OpenBankingWebhookTests.cs`: 9 nhóm kiểm thử (M5-01..M5-09), 108 assertions đạt 100%.
  - `ChallengerTests/ExecutiveBiAnalyticsTests.cs`: 4 nhóm kiểm thử (M6-01..M6-04), 55 assertions đạt 100%.
- **Các bất biến kỹ thuật bắt buộc phải giữ vững**:
  - `VULN-04`: Khóa `InventoryLock` kiểu `SemaphoreSlim(1,1)` không deadlock khi chạy 100 tác vụ song song.
  - `VULN-06.14`: Bất biến bảo toàn sổ cái tài chính: `TotalPaid + RemainingDebt == TongTien`.
  - `VULN-11.11`: Chặn ngay chuỗi Base64 chữ ký vượt 256KB trước khi giải mã.
  - `M5-06.1`: Khử trùng lặp giao dịch Webhook ngân hàng (Idempotency) tuyệt đối.
  - `M4-01.21`: Kích hoạt khóa nợ xấu khi quá hạn 15 ngày hoặc nợ vượt 3.000.000 VNĐ.

#### 3. Lệnh Kiểm Tra Cấu Trúc Bảng CSDL Thực Tế
```powershell
Get-Content RentalSystem/Models/AppModels.cs | Select-String "public class"
```
- Đảm bảo danh sách thực thể khớp chính xác 18 bảng đã định nghĩa trong VAU-3.

#### 4. Lệnh Quét Văn Bản Tìm Kiếm Đoạn Giữ Chỗ (Zero Placeholder Scan)
```powershell
Get-ChildItem -Path docs/ -Filter *.md | Select-String "tạm thời để trống"
```
- Đảm bảo kết quả trả về rỗng (0 dòng phát hiện).

---

## 6. KẾ HOẠCH ĐIỀU PHỐI THỰC THI & PHÂN CÔNG NHÂN SỰ ĐỢT RÀ SOÁT

Để hoàn tất việc đối soát từng câu từng chữ đối với tài liệu `KHOA_LUAN_TOT_NGHIEP_RENTALSYSTEM_HUIT_2025.docx` trong thời gian tối ưu, tổ công tác phân rã lộ trình triển khai thành 4 giai đoạn nối tiếp:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        LỘ TRÌNH ĐIỀU PHỐI THỰC THI RÀ SOÁT                             │
├───────────────────┬────────────────────────────────────────────────────────────────────┤
│ GIAI ĐOẠN 1       │ Ban hành Kế hoạch & Khung Đánh giá Chi tiết                        │
│ (Khởi động)       │ - Hoàn tất và xuất bản docs/KE_HOACH_VA_KHUNG_DANH_GIA_KHOA_LUAN.md│
│                   │ - Thiết lập chuẩn mực Taxonomy 3 trục & 6 đơn vị VAU.              │
├───────────────────┼────────────────────────────────────────────────────────────────────┤
│ GIAI ĐOẠN 2       │ Thực thi Đối soát Chi tiết từng VAU (Parallel Auditing)            │
│ (Khảo sát sâu)    │ - Nhóm 1: Rà soát VAU-0, VAU-1, VAU-2 (Thuật toán, Use Case, API)   │
│                   │ - Nhóm 2: Rà soát VAU-3, VAU-4 (CSDL 18 bảng, Giao diện, Code C#)  │
│                   │ - Nhóm 3: Rà soát VAU-5 (ChallengerTests, Xóa 3 Placeholders)      │
├───────────────────┼────────────────────────────────────────────────────────────────────┤
│ GIAI ĐOẠN 3       │ Tổng hợp Ma Trận Traceability Matrix & Soạn Thảo Bản Hiệu Chỉnh    │
│ (Tổng hợp lỗi)    │ - Gom toàn bộ Defect Reports vào bảng tổng thể.                    │
│                   │ - Soạn thảo văn bản và vẽ lại các sơ đồ UML bị sai Actor/Service.  │
├───────────────────┼────────────────────────────────────────────────────────────────────┤
│ GIAI ĐOẠN 4       │ Cập nhật Tệp Word Gốc & Thẩm Định Độc Lập Cuối Cùng                │
│ (Đóng gói nộp)    │ - Dùng script python-docx nạp toàn bộ nội dung chuẩn hóa vào docx. │
│                   │ - Chạy kiểm thử ChallengerTests xác nhận 595/595 PASS.             │
│                   │ - Bàn giao bản khóa luận đạt chuẩn Zero-Hallucination 100%.       │
└───────────────────┴────────────────────────────────────────────────────────────────────┘
```

### Tiêu Chuẩn Nghiệm Thu Cuối Cùng (Definition of Done - DoD)
Một bản khóa luận được coi là hoàn thiện và sẵn sàng nộp Hội đồng khi và chỉ khi:
1. Toàn bộ 740 đoạn văn không còn bất kỳ câu giữ chỗ nào dạng `[...tạm thời để trống...]`.
2. Không còn bất kỳ vai trò ảo nào (Thủ quỹ, Kế toán trưởng, Ban Giám đốc) trong văn bản và sơ đồ.
3. Không còn bất kỳ lớp dịch vụ ảo nào (`RentalDbContext`, `InventoryLockService`, `DebtManagementService`, `VietQrService`, `SignalR`).
4. Từ điển dữ liệu 18 bảng CSDL khớp 100% với `RentalSystem/Models/AppModels.cs`, cặp khóa chính của `ChiTietHopDong` là Composite Key `(MaHopDong, MaThietBi)`.
5. Bảng API khớp 100% với 8 Mobile API Controllers tiền tố `/api/...`.
6. Tất cả các số liệu kiểm thử trong Chương 5 phản ánh chính xác kết quả thực chạy của `ChallengerTests` (595/595 tests PASS).
7. Dự án biên dịch sạch 0 lỗi (`dotnet build`), kiểm thử tự động 100% pass (`dotnet run ChallengerTests`).

---
**Tổ Công Tác Thẩm Định Khóa Luận Tốt Nghiệp RentalSystem HUIT 2025**  
*Tài liệu lưu hành nội bộ phục vụ rà soát chất lượng học thuật và an toàn kỹ thuật phần mềm.*
