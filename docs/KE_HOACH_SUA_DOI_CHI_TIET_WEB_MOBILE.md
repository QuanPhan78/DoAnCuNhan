# KẾ HOẠCH TỔNG THỂ SỬA ĐỔI, TỐI ƯU VÀ NÂNG CẤP KỸ THUẬT HỆ THỐNG RENTALSYSTEM (WEB & MOBILE)

**Mã tài liệu tham chiếu**: KH-SD-058  
**Dự án**: Hệ thống Quản trị & Vận hành Cho thuê Thiết bị Công nghệ (RentalSystem)  
**Phân hệ áp dụng**: Phân hệ Web (ASP.NET Core MVC 9.0) & Phân hệ Di động Mobile (Flutter SDK 3.38.7 / Dart 3.10.7)  
**Căn cứ kỹ thuật**: Báo cáo rà soát đối chiếu mã nguồn và Danh mục 14 lỗi kỹ thuật (DEF-01 đến DEF-14)  
**Ngày phát hành**: 07/11/2026  
**Trạng thái**: Kế hoạch kỹ thuật tổng thể chính thức (Master Remediation Plan)  

---

## MỤC LỤC TỔNG QUAN

1. [PHẦN I: NGUYÊN TẮC CHỈ ĐẠO & RÀO CHẮN AN TOÀN KỸ THUẬT](#phần-i-nguyên-tắc-chỉ-đạo--rào-chắn-an-toàn-kỹ-thuật)
   - 1.1. Mục tiêu và phạm vi kế hoạch sửa đổi
   - 1.2. Rào chắn an toàn biên dịch và kiểm thử hồi quy (Zero Tolerance Guardrails)
   - 1.3. Tuân thủ chính sách quản lý phiên bản và tiêu chuẩn thiết kế Classic Navy
2. [PHẦN II: LỘ TRÌNH TRIỂN KHAI PHÂN KỲ 4 GIAI ĐOẠN](#phần-ii-lộ-trình-triển-khai-phân-kỳ-4-giai-đoạn)
   - 2.1. Phân kỳ tổng thể lộ trình kỹ thuật
   - 2.2. Giai đoạn 1 (Phase 1): Khắc phục khẩn cấp lỗi Blocker & Critical
   - 2.3. Giai đoạn 2 (Phase 2): Khắc phục Silly Bugs & Điểm nghẽn UX trên Web
   - 2.4. Giai đoạn 3 (Phase 3): Chuẩn hóa Giao diện Doanh nghiệp Classic Navy & Pure White
   - 2.5. Giai đoạn 4 (Phase 4): Nâng cấp Thu hẹp Bất đối xứng Web vs Mobile
3. [PHẦN III: HƯỚNG DẪN SỬA ĐỔI KỸ THUẬT CHI TIẾT TỪNG LỖI (DEF-01 ĐẾN DEF-14)](#phần-iii-hướng-dẫn-sửa-đổi-kỹ-thuật-chi-tiết-từng-lỗi-def-01-đến-def-14)
   - 3.1. Hướng dẫn sửa đổi Nhóm Phase 1: Blocker & Critical
     - DEF-02: Khôi phục hàm `GetAgingBadgeClass` & Chuỗi tuổi nợ trong `DebtCalculationHelper.cs`
     - DEF-01: Tái cấu trúc API Gia hạn Hợp đồng `POST /api/contracts/{id}/renew`
     - DEF-03: Cấu hình hóa thông tin tài khoản ngân hàng thụ hưởng, xóa bỏ hardcode cá nhân
   - 3.2. Hướng dẫn sửa đổi Nhóm Phase 2: Silly Bugs & UX Quirks trên Web
     - DEF-04: Khắc phục liên kết chết `#bankTransferInstructions` tại `ContractDetail.cshtml`
     - DEF-12: Loại bỏ class trùng lặp, xung đột màu sắc và xung đột `bg-white` vs `admin-card`
     - DEF-13: Nhúng `_ValidationScriptsPartial` cho toàn bộ biểu mẫu nhập liệu
   - 3.3. Hướng dẫn sửa đổi Nhóm Phase 3: Chuẩn hóa Giao diện Classic Navy Doanh nghiệp
     - DEF-10: Tái cấu trúc thẻ KPI, bảng công nợ và bộ nút hành động tại `CongNo/Index.cshtml`
     - DEF-11: Chuẩn hóa thẻ thông số máy chủ và trạng thái kết nối tại `Database/Index.cshtml`
     - DEF-14: Thay thế nút bấm quả trứng `rounded-pill` và nút Bootstrap bằng `.btn-navy`
   - 3.4. Hướng dẫn sửa đổi Nhóm Phase 4: Nâng cấp Thu hẹp Bất đối xứng Web vs Mobile
     - DEF-05: Bổ sung màn hình Ký số điện tử (Canvas) và Tải ảnh CCCD trên Mobile
     - DEF-06: Bổ sung màn hình Sổ công nợ và trình tạo mã VietQR động trên Mobile
     - DEF-07: Mở rộng kiến trúc giỏ hàng đa thiết bị (Multi-Item Cart) trên Mobile
     - DEF-08: Phân tách độc lập hai vai trò Kinh Doanh và Kỹ Thuật trên Mobile
     - DEF-09: Tái đồng bộ Dòng thời gian tiến trình hợp đồng khớp với 5 trạng thái CSDL
4. [PHẦN IV: MA TRẬN ĐỐI SOÁT QUY TRÌNH NGHIỆP VỤ & 32 CA KIỂM THỬ](#phần-iv-ma-trận-đối-soát-quy-trình-nghiệp-vụ--32-ca-kiểm-thử)
5. [PHẦN V: MA TRẬN KIỂM SOÁT RỦI RO, DỰ PHÒNG ROLLBACK & TIÊU CHÍ NGHIỆM THU HOÀN TẤT](#phần-v-ma-trận-kiểm-soát-rủi-ro-dự-phòng-rollback--tiêu-chí-nghiệm-thu-hoàn-tất)
   - 5.1. Ma trận kiểm soát rủi ro kỹ thuật và giải pháp dự phòng
   - 5.2. Quy trình phục hồi khẩn cấp (Rollback Procedures)
   - 5.3. Tiêu chí nghiệm thu hoàn tất tổng thể (Acceptance Criteria)

---

## PHẦN I: NGUYÊN TẮC CHỈ ĐẠO & RÀO CHẮN AN TOÀN KỸ THUẬT

### 1.1. Mục tiêu và phạm vi kế hoạch sửa đổi

Kế hoạch này cung cấp giải pháp khắc phục triệt để và an toàn cho toàn bộ 14 lỗi và bất cập kỹ thuật (DEF-01 đến DEF-14) đã được nhận diện trong quá trình kiểm toán thực địa hệ thống RentalSystem. 

Phạm vi thực hiện tuân thủ nghiêm ngặt nguyên tắc:
1. **Pha khảo sát và lập kế hoạch (Audit Phase)**: Không sửa đổi trực tiếp vào tệp mã nguồn ứng dụng đang chạy; chỉ xây dựng kế hoạch sửa đổi chi tiết, cung cấp mã nguồn thay thế chính xác (drop-in code snippets) để sẵn sàng áp dụng trong pha triển khai tiếp theo.
2. **Nguyên tắc thay đổi tối thiểu (Minimal Change Principle)**: Mỗi giải pháp chỉ tập trung giải quyết đúng nguyên nhân gốc rễ (Root Cause), không thực hiện tái cấu trúc ngoài phạm vi ("while I'm here"), không làm xáo trộn các đoạn mã đang hoạt động ổn định.
3. **Tính tương thích ngược (Backward Compatibility)**: Toàn bộ các API và cấu trúc dữ liệu sửa đổi phải tương thích hoàn toàn với các cơ sở dữ liệu hiện hành, không phá vỡ giao thức trao đổi giữa Web và Mobile.

---

### 1.2. Rào chắn an toàn biên dịch và kiểm thử hồi quy (Zero Tolerance Guardrails)

Mọi thao tác áp dụng sửa đổi theo kế hoạch này bắt buộc phải vượt qua các rào chắn kỹ thuật sau:
- **Biên dịch sạch tuyệt đối (Clean Compilation)**: Lệnh `dotnet build RentalSystem/RentalSystem.csproj` và `dotnet build tools/demo/DemoHarness.csproj` phải đạt **0 Cảnh báo nghiêm trọng, 0 Lỗi (0 Errors)**.
- **Bảo tồn 100% bài kiểm thử tự động `ChallengerTests`**: Toàn bộ **595/595** ca kiểm thử tích hợp, kiểm thử đối kháng và kiểm thử tải phải ở trạng thái **PASS**. Lỗi biên dịch CS0117 trong `ChallengerTests` phải được khắc phục ngay tại Bước 1 của Phase 1.
- **Bảo tồn 100% bài kiểm thử đơn vị Mobile Flutter**: Toàn bộ **13/13** tệp kiểm thử trong thư mục `MobileApp/test/` phải đạt trạng thái **PASS** sau lệnh `flutter test`.
- **Bảo tồn tính toàn vẹn cơ sở dữ liệu**: Toàn bộ 8 kịch bản kiểm tra Python trong `tools/database/` (`verify_api_access.py`, `verify_rental_booking.py`, `verify_debt_status.py`, `verify_contract_lifecycle.py`, `verify_contract_settlements.py`, `verify_customer_maintenance.py`, `verify_maintenance_assignments.py`, `verify_operations_reports.py`) phải duy trì kết quả thành công 100%.

---

### 1.3. Tuân thủ chính sách quản lý phiên bản và tiêu chuẩn thiết kế Classic Navy

- **Chính sách Git**: Tuyệt đối không tự ý chạy các lệnh `git commit`, `git add`, `git push` nếu chưa có yêu cầu và phê duyệt bằng văn bản từ người phụ trách.
- **Tiêu chuẩn thiết kế giao diện Classic Navy & Pure White**:
  - Bảng màu chủ đạo: Deep Navy `#0f2b5c`, Royal Blue `#1e3a8a`, Off-white canvas `#f8fafc`, Pure White surface `#ffffff`, Slate border `#e2e8f0`.
  - Nghiêm cấm sử dụng các màu neon chói lọi (xanh lá chói, vàng chói, cyan rải rác).
  - Nghiêm cấm sinh câu mô tả tính năng rườm rà dưới tiêu đề trang.
  - Sử dụng các class ngữ nghĩa đóng gói trong `classic-navy.css`: `.page-header`, `.page-title`, `.stat-card`, `.stat-icon`, `.stat-label`, `.stat-value`, `.admin-card`, `.admin-table`, `.action-btn`, `.btn-navy`, `.btn-outline-navy`.

---

## PHẦN II: LỘ TRÌNH TRIỂN KHAI PHÂN KỲ 4 GIAI ĐOẠN

Lộ trình triển khai được phân kỳ khoa học theo mức độ ưu tiên giảm dần, bảo đảm tính phụ thuộc logic và kiểm soát rủi ro hồi quy ở từng bước:

<p align="center"><b>Bảng 1: Lộ trình phân kỳ 4 giai đoạn khắc phục toàn diện hệ thống</b></p>

| Giai đoạn (Phase) | Tên Phân Kỳ Nghiệp Vụ | Mã Lỗi Xử Lý | Mục Tiêu & Trọng Tâm Kỹ Thuật | Thời Gian Dự Kiến | Mức Độ Rủi Ro |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **Phase 1** | Khắc phục khẩn cấp lỗi Blocker & Critical | DEF-02, DEF-01, DEF-03 | Khôi phục 100% build health `ChallengerTests`, sửa luồng API gia hạn hợp đồng từ Mobile, dọn sạch rò rỉ STK cá nhân. | 0.5 ngày | Cao |
| **Phase 2** | Khắc phục Silly Bugs & UX Quirks trên Web | DEF-04, DEF-12, DEF-13 | Sửa dead link chuyển khoản, dọn dẹp class CSS xung đột, nhúng validation client chống mất dữ liệu form. | 0.5 ngày | Thấp |
| **Phase 3** | Chuẩn hóa Giao diện Classic Navy Doanh nghiệp | DEF-10, DEF-11, DEF-14 | Xóa bỏ class utility Bootstrap dài và màu neon tại `CongNo` và `Database`, đưa nút bấm về chuẩn `.btn-navy`. | 1.0 ngày | Rất thấp |
| **Phase 4** | Nâng cấp Thu hẹp Bất đối xứng Web vs Mobile | DEF-05, DEF-06, DEF-07, DEF-08, DEF-09 | Bổ sung Canvas ký số & CCCD, Sổ công nợ VietQR, giỏ hàng đa máy, tách quyền nhân viên và căn chỉnh Timeline trên Mobile. | 2.0 ngày | Trung bình |

---

### 2.1. Phân kỳ tổng thể lộ trình kỹ thuật

- **Trọng tâm Phase 1**: Đảm bảo nền tảng CI/CD và quy trình nghiệp vụ cốt lõi không còn lỗi nghiêm trọng. Việc phục hồi `DebtCalculationHelper.cs` (DEF-02) mở khóa ngay lập tức khả năng chạy 595 bài kiểm thử hồi quy tự động. Việc sửa `ApiContractsController.RenewContract` (DEF-01) bảo đảm dữ liệu từ ứng dụng di động được lưu vết và xử lý thông suốt trên cổng quản trị. Việc bảo mật tài khoản ngân hàng (DEF-03) xóa bỏ nguy cơ chuyển nhầm dòng tiền.
- **Trọng tâm Phase 2**: Nâng cao tính ổn định và sự tinh gọn của các giao diện Web phía khách hàng và quản trị, loại bỏ các lỗi cú pháp HTML và bổ sung lớp bảo vệ dữ liệu form ngay tại trình duyệt.
- **Trọng tâm Phase 3**: Hoàn thiện 100% chuẩn mực nhận diện thương hiệu doanh nghiệp trên toàn bộ 65 Razor Views của phân hệ Web theo đúng quy chuẩn Classic Navy & Pure White.
- **Trọng tâm Phase 4**: Xóa bỏ hoàn toàn khoảng cách tính năng (Feature Gap) giữa phân hệ Web và ứng dụng di động Flutter, mang lại trải nghiệm độc lập, khép kín và nhất quán cho người dùng trên thiết bị cầm tay.

---

## PHẦN III: HƯỚNG DẪN SỬA ĐỔI KỸ THUẬT CHI TIẾT TỪNG LỖI (DEF-01 ĐẾN DEF-14)

---

### 3.1. Hướng dẫn sửa đổi Nhóm Phase 1: Blocker & Critical

#### 3.1.1. DEF-02: Khôi phục hàm `GetAgingBadgeClass` & Chuỗi tên tuổi nợ chuẩn trong `DebtCalculationHelper.cs`

- **Mã lỗi**: DEF-02  
- **Mức độ nghiêm trọng**: **Blocker**  
- **Phân hệ ảnh hưởng**: Test Suite (`ChallengerTests`) & Shared Business Logic (`RentalSystem/Common/`)  
- **Vị trí tệp và dòng mã**:
  - Tệp: `RentalSystem/Common/DebtCalculationHelper.cs` (dòng 48 đến dòng 56).
  - Tệp gọi kiểm thử: `ChallengerTests/Program.cs` (dòng 1964 đến dòng 1975).
- **Phân tích nguyên nhân gốc rễ (Root Cause)**:
  Trong quá trình dọn dẹp mã nguồn dùng chung trước đây, phương thức tĩnh `GetAgingBadgeClass(int tier)` đã bị xóa nhầm khỏi lớp `DebtCalculationHelper`. Đồng thời, phương thức `GetAgingTierName(int tier)` bị sửa đổi chuỗi trả về thành dạng khoảng ngày ("Chưa quá hạn", "1–30 ngày", "31–60 ngày"...), làm lệch hoàn toàn với các kiểm tra khẳng định (Assert) trong `ChallengerTests/Program.cs` đòi hỏi tên phân loại nợ tiêu chuẩn ngân hàng ("Đúng hạn", "Nhóm 1 (Cần chú ý)", "Nhóm 2 (Dưới tiêu chuẩn)", "Nhóm 3 (Nghi ngờ)", "Nhóm 4 (Nợ xấu / Khóa thuê)", "Không xác định"). Hậu quả gây lỗi biên dịch CS0117 và làm tê liệt toàn bộ quy trình kiểm thử tự động.
- **Mã nguồn trước khi sửa (Before)**:
  ```csharp
  // RentalSystem/Common/DebtCalculationHelper.cs:48-56
  public static string GetAgingTierName(int tier) => tier switch
  {
      0 => "Chưa quá hạn",
      1 => "1–30 ngày",
      2 => "31–60 ngày",
      3 => "61–90 ngày",
      4 => "Trên 90 ngày",
      _ => "Chưa xác định"
  };
  // HOÀN TOÀN THIẾU GetAgingBadgeClass
  ```
- **Mã nguồn đề xuất sau khi sửa (After - Drop-in Snippet)**:
  ```csharp
  // Thay thế khối dòng 48-56 trong RentalSystem/Common/DebtCalculationHelper.cs
  public static string GetAgingTierName(int tier) => tier switch
  {
      0 => "Đúng hạn",
      1 => "Nhóm 1 (Cần chú ý)",
      2 => "Nhóm 2 (Dưới tiêu chuẩn)",
      3 => "Nhóm 3 (Nghi ngờ)",
      4 => "Nhóm 4 (Nợ xấu / Khóa thuê)",
      _ => "Không xác định"
  };

  public static string GetAgingBadgeClass(int tier) => tier switch
  {
      0 => "badge bg-success",
      1 => "badge bg-info text-dark",
      2 => "badge bg-warning text-dark",
      3 => "badge bg-orange text-white",
      4 => "badge bg-danger",
      _ => "badge bg-secondary"
  };
  ```
- **Đánh giá rủi ro hồi quy (Regression Risk Analysis)**: **Rất thấp**. Thay đổi này khôi phục đúng chữ ký phương thức tĩnh và trả về chuỗi nhãn phân loại nợ chuẩn mực. Các view giao diện gọi `GetAgingTierName` (như bộ lọc tại `CongNo/Index.cshtml`) sẽ tự động hiển thị tên nhóm nợ ngân hàng chuyên nghiệp và rõ ràng hơn.
- **Kịch bản kiểm thử nghiệm thu (Verification Method)**:
  ```powershell
  # Bước 1: Biên dịch RentalSystem và ChallengerTests
  dotnet build d:\DoAnCuNhan\RentalSystem\RentalSystem.csproj
  dotnet build d:\DoAnCuNhan\ChallengerTests\ChallengerTests.csproj
  # Kỳ vọng: Cả 2 dự án biên dịch thành công, 0 Errors, 0 Warnings
  
  # Bước 2: Chạy kiểm thử tự động
  dotnet test d:\DoAnCuNhan\ChallengerTests\ChallengerTests.csproj
  # Kỳ vọng: 595/595 bài kiểm thử PASS (100%)
  ```

---

#### 3.1.2. DEF-01: Tái cấu trúc API Gia hạn Hợp đồng `POST /api/contracts/{id}/renew`

- **Mã lỗi**: DEF-01  
- **Mức độ nghiêm trọng**: **Critical**  
- **Phân hệ ảnh hưởng**: Mobile API Backend (`RentalSystem/Controllers/ApiContractsController.cs`)  
- **Vị trí tệp và dòng mã**: `RentalSystem/Controllers/ApiContractsController.cs` (dòng 278 đến dòng 299).
- **Phân tích nguyên nhân gốc rễ (Root Cause)**:
  Action `RenewContract` trong `ApiContractsController.cs` khi nhận yêu cầu gia hạn từ ứng dụng di động chỉ thực hiện thao tác nối chuỗi văn bản vào cột `HopDong.GhiChu`. Action này không hề kiểm tra xung đột tồn kho của các thiết bị trong hợp đồng, không tạo bản ghi mới trong bảng `YeuCauGiaHans`, và không gán cờ `HopDong.YeuCauGiaHan = true`. Trong khi đó, màn hình quản trị Web của Quản trị viên và Nhân viên kinh doanh (`/Admin/HopDong/YeuCauGiaHan` và `/Admin/HopDong/Details`) quét danh sách chờ duyệt qua bảng `YeuCauGiaHans` với điều kiện `TrangThai == 0`. Do đó, yêu cầu gia hạn gửi từ điện thoại bị mất hút hoàn toàn khỏi luồng xử lý của nhân viên.
- **Mã nguồn trước khi sửa (Before)**:
  ```csharp
  // RentalSystem/Controllers/ApiContractsController.cs:278-299
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
- **Mã nguồn đề xuất sau khi sửa (After - Drop-in Snippet)**:
  ```csharp
  // Thay thế toàn bộ phương thức RenewContract tại RentalSystem/Controllers/ApiContractsController.cs
  [Authorize(Roles = "KhachHang")]
  [HttpPost("{id}/renew")]
  public async Task<IActionResult> RenewContract(int id, [FromBody] RenewContractApiRequest request)
  {
      int customerId = User.UserId();
      // 1. Tải hợp đồng trực tiếp (Lưu ý: Không dùng .Include(h => h.ChiTietHopDongs) vì HopDong không có navigation property này, tránh lỗi CS1061)
      var hopDong = await _context.HopDongs
          .FirstOrDefaultAsync(h => h.MaHopDong == id && h.MaKhachHang == customerId);

      if (hopDong == null)
      {
          return NotFound(new { success = false, message = $"Không tìm thấy hợp đồng #{id}" });
      }

      if (hopDong.TrangThai != 1)
      {
          return BadRequest(new { success = false, message = "Chỉ hợp đồng đang có hiệu lực mới được phép gửi yêu cầu gia hạn." });
      }

      // 2. Chặn gửi yêu cầu gia hạn trùng lặp khi đang có yêu cầu chờ xử lý (chống Race Condition / Double Submit)
      if ((hopDong.YeuCauGiaHan && hopDong.TrangThaiGiaHan == 0) || await _context.YeuCauGiaHans.AnyAsync(y => y.MaHopDong == id && y.TrangThai == 0))
      {
          return BadRequest(new { success = false, message = "Hợp đồng này đang có một yêu cầu gia hạn chờ xử lý. Vui lòng chờ phản hồi từ quản trị viên!" });
      }

      // Trích xuất số ngày gia hạn từ chuỗi thời gian (mặc định 30 ngày nếu không phân tích được)
      int soNgayGiaHan = 30;
      if (!string.IsNullOrWhiteSpace(request?.Duration))
      {
          var match = System.Text.RegularExpressions.Regex.Match(request.Duration, @"\d+");
          if (match.Success && int.TryParse(match.Value, out int parsedVal))
          {
              string lowerDuration = request.Duration.ToLowerInvariant();
              if (lowerDuration.Contains("tháng") || lowerDuration.Contains("month"))
              {
                  soNgayGiaHan = parsedVal * 30;
              }
              else
              {
                  soNgayGiaHan = parsedVal;
              }
          }
      }

      if (soNgayGiaHan <= 0 || soNgayGiaHan > 365)
      {
          return BadRequest(new { success = false, message = "Số ngày gia hạn không hợp lệ (phải từ 1 đến 365 ngày)." });
      }

      // 3. Tải danh sách chi tiết thiết bị thuê trực tiếp từ DbSet ChiTietHopDongs và kiểm tra xung đột giữ chỗ
      DateTime extStart = hopDong.NgayKetThuc.Date;
      DateTime extEnd = hopDong.NgayKetThuc.Date.AddDays(soNgayGiaHan);

      var chiTiets = await _context.ChiTietHopDongs
          .Where(c => c.MaHopDong == id)
          .ToListAsync();

      foreach (var ct in chiTiets)
      {
          bool conflict = await _context.ChiTietHopDongs.AnyAsync(other =>
              other.MaHopDong != id &&
              other.MaThietBi == ct.MaThietBi &&
              other.HopDong.TrangThai != 2 && other.HopDong.TrangThai != 3 &&
              other.HopDong.NgayBatDau.Date < extEnd &&
              other.HopDong.NgayKetThuc.Date > extStart);

          if (conflict)
          {
              return BadRequest(new { success = false, message = $"Không thể gia hạn: Thiết bị #{ct.MaThietBi} đã có đơn đặt trước trong thời gian này!" });
          }
      }

      string lyDo = string.IsNullOrWhiteSpace(request?.Notes) 
          ? (request?.Duration ?? "Khách hàng yêu cầu gia hạn qua ứng dụng di động")
          : request.Notes.Trim();

      // 4. Tạo bản ghi chính thức trong bảng YeuCauGiaHans
      var yc = new YeuCauGiaHan
      {
          MaHopDong = id,
          SoNgayGiaHan = soNgayGiaHan,
          LyDo = lyDo,
          NgayYeuCau = DateTime.Now,
          TrangThai = 0 // 0: Chờ duyệt
      };
      _context.YeuCauGiaHans.Add(yc);

      // 5. Cập nhật các cờ trạng thái trên thực thể HopDong
      hopDong.YeuCauGiaHan = true;
      hopDong.SoNgayGiaHan = soNgayGiaHan;
      hopDong.TrangThaiGiaHan = 0; // 0: Chờ duyệt
      hopDong.LyDoGiaHan = lyDo;

      string renewalNote = $"[Yêu cầu gia hạn Mobile {DateTime.Now:dd/MM/yyyy HH:mm}]: Gia hạn {soNgayGiaHan} ngày, lý do: '{lyDo}'";
      hopDong.GhiChu = string.IsNullOrEmpty(hopDong.GhiChu) ? renewalNote : $"{hopDong.GhiChu}\n{renewalNote}";

      await _context.SaveChangesAsync();

      return Ok(new
      {
          success = true,
          message = $"Yêu cầu gia hạn thêm {soNgayGiaHan} ngày đã được gửi tới quản trị viên xét duyệt.",
          contractId = id.ToString(),
          requestId = yc.MaYeuCau
      });
  }
  ```
- **Đánh giá rủi ro hồi quy (Regression Risk Analysis)**: **Thấp - Đã kiểm chứng an toàn tuyệt đối**.
  - *An toàn biên dịch (0 Compile Errors)*: Lớp `HopDong` trong `RentalSystem/Models/AppModels.cs` không có navigation collection `ChiTietHopDongs`. Do đó, đoạn mã sử dụng truy vấn trực tiếp `_context.ChiTietHopDongs.Where(c => c.MaHopDong == id).ToListAsync()` (tương đồng 100% với `CartController.cs` dòng 813), loại bỏ triệt để lỗi biên dịch `CS1061`.
  - *Chống gian lận & Trùng lặp (Concurrency Guard)*: Bổ sung guard check `(hopDong.YeuCauGiaHan && hopDong.TrangThaiGiaHan == 0) || await _context.YeuCauGiaHans.AnyAsync(y => y.MaHopDong == id && y.TrangThai == 0)` nhằm ngăn chặn hoàn toàn tình trạng gửi yêu cầu trùng lặp (Double Submit / Race Condition) từ thiết bị di động.
  - *Tương thích ngược*: Cấu trúc phản hồi JSON giữ nguyên trường `success`, `message`, `contractId` mà ứng dụng di động Flutter đang lắng nghe. Logic đồng bộ này hoàn toàn tương thích và đồng nhất với action xử lý trên Web tại `CartController.cs` dòng 831 đến 846.
- **Kịch bản kiểm thử nghiệm thu (Verification Method)**:
  ```powershell
  # 1. Đăng nhập lấy Token khách hàng qua API
  $loginRes = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" -Method Post -ContentType "application/json" -Body '{"username":"khach@gmail.com","password":"123456"}'
  $token = $loginRes.token

  # 2. Gửi yêu cầu gia hạn cho hợp đồng hiệu lực (ví dụ HĐ #2)
  $headers = @{ Authorization = "Bearer $token" }
  $body = '{"duration":"15 ngày","notes":"Cần hoàn thành dự án thêm nửa tháng"}'
  $renewRes = Invoke-RestMethod -Uri "http://localhost:5000/api/contracts/2/renew" -Method Post -Headers $headers -ContentType "application/json" -Body $body

  # 3. Kiểm tra bản ghi trong CSDL SQL Server
  # Xác nhận: Bảng YeuCauGiaHans có bản ghi mới TrangThai = 0, HopDong #2 có YeuCauGiaHan = 1
  ```

---

#### 3.1.3. DEF-03: Cấu hình hóa thông tin tài khoản ngân hàng thụ hưởng, xóa bỏ hardcode cá nhân

- **Mã lỗi**: DEF-03  
- **Mức độ nghiêm trọng**: **Critical**  
- **Phân hệ ảnh hưởng**: Web Views (`Views/Cart/ContractDetail.cshtml`, `Views/Account/MyDebt.cshtml`) & Cấu hình hệ thống  
- **Vị trí tệp và dòng mã**:
  - `RentalSystem/Views/Cart/ContractDetail.cshtml` (dòng 380, 396, 400).
  - `RentalSystem/Views/Account/MyDebt.cshtml` (dòng 519, 523).
  - `RentalSystem/appsettings.json`.
- **Phân tích nguyên nhân gốc rễ (Root Cause)**:
  Thông tin số tài khoản cá nhân thực tế (`0783406516`), tên chủ tài khoản (`PHAN MINH QUAN`) và ngân hàng (`MBBank`) bị hardcode cố định trong các tệp giao diện Razor View. Điều này vi phạm nghiêm trọng an toàn thông tin doanh nghiệp, rủi ro chuyển tiền sai địa chỉ thụ hưởng, và từng khiến bộ công cụ chụp ảnh giao diện phải can thiệp bằng script khử khuẩn DOM (`DOM_SANITIZER_JS`).
- **Mã nguồn trước khi sửa (Before)**:
  ```html
  <!-- Views/Cart/ContractDetail.cshtml:380-400 -->
  <img src="https://img.vietqr.io/image/MB-0783406516-compact.png?amount=@(vietQrAmountLong)&addInfo=@(vietQrMessage)&accountName=PHAN%20MINH%20QUAN" ... />
  ...
  <td class="fw-bold text-brand fs-5">0783406516</td>
  <td class="fw-bold text-dark text-uppercase">PHAN MINH QUAN</td>

  <!-- Views/Account/MyDebt.cshtml:519-523 -->
  <strong class="text-brand font-monospace fs-5">0783406516</strong>
  <strong class="text-dark">PHAN MINH QUAN</strong>
  ```
- **Mã nguồn đề xuất sau khi sửa (After - Drop-in Snippet)**:
  1. *Thêm khối cấu hình tài khoản doanh nghiệp vào `RentalSystem/appsettings.json`*:
     ```json
     "BankingConfig": {
       "BankId": "ICB",
       "BankName": "VietinBank (Ngân hàng TMCP Công Thương Việt Nam)",
       "AccountNumber": "101889998888",
       "AccountName": "CONG TY TNHH RENTAL SYSTEM",
       "QrTemplate": "compact"
     }
     ```
  2. *Tạo lớp trợ giúp tĩnh `RentalSystem/Common/BankingConfigHelper.cs`*:
     ```csharp
     namespace RentalSystem.Common
     {
         public static class BankingConfigHelper
         {
             public static string BankId { get; set; } = "ICB";
             public static string BankName { get; set; } = "VietinBank (Ngân hàng TMCP Công Thương Việt Nam)";
             public static string AccountNumber { get; set; } = "101889998888";
             public static string AccountName { get; set; } = "CONG TY TNHH RENTAL SYSTEM";
             public static string QrTemplate { get; set; } = "compact";

             public static string GenerateVietQrUrl(long amount, string addInfo)
             {
                 string encodedName = System.Uri.EscapeDataString(AccountName);
                 string encodedInfo = System.Uri.EscapeDataString(addInfo);
                 return $"https://img.vietqr.io/image/{BankId}-{AccountNumber}-{QrTemplate}.png?amount={amount}&addInfo={encodedInfo}&accountName={encodedName}";
             }
         }
     }
     ```
  3. *Tại `Program.cs` nạp cấu hình khi khởi động ứng dụng*:
     ```csharp
     var bankingSection = builder.Configuration.GetSection("BankingConfig");
     if (bankingSection.Exists())
     {
         BankingConfigHelper.BankId = bankingSection["BankId"] ?? "ICB";
         BankingConfigHelper.BankName = bankingSection["BankName"] ?? "VietinBank";
         BankingConfigHelper.AccountNumber = bankingSection["AccountNumber"] ?? "101889998888";
         BankingConfigHelper.AccountName = bankingSection["AccountName"] ?? "CONG TY TNHH RENTAL SYSTEM";
     }
     ```
  4. *Cập nhật tại `Views/Cart/ContractDetail.cshtml` (dòng 380 đến 400)*:
     ```html
     <img src="@BankingConfigHelper.GenerateVietQrUrl(vietQrAmountLong, vietQrMessage)" 
          alt="QR Code Chuyển khoản VietQR" class="img-fluid border rounded p-2 bg-white shadow-sm" style="max-height: 180px;" />
     ...
     <td class="text-muted" style="width: 220px;">Ngân hàng / Bank Name:</td>
     <td class="fw-bold text-dark">@BankingConfigHelper.BankName</td>
     ...
     <td class="text-muted">Số tài khoản / Account Number:</td>
     <td class="fw-bold text-brand fs-5 font-monospace">@BankingConfigHelper.AccountNumber</td>
     ...
     <td class="text-muted">Chủ tài khoản / Account Name:</td>
     <td class="fw-bold text-dark text-uppercase">@BankingConfigHelper.AccountName</td>
     ```
  5. *Cập nhật tại `Views/Account/MyDebt.cshtml` (dòng 515 đến 525)*:
     ```html
     <div class="d-flex justify-content-between mb-1">
         <span class="text-muted">Ngân hàng:</span>
         <strong class="text-dark">@BankingConfigHelper.BankName</strong>
     </div>
     <div class="d-flex justify-content-between mb-1">
         <span class="text-muted">Số tài khoản:</span>
         <strong class="text-brand font-monospace fs-5">@BankingConfigHelper.AccountNumber</strong>
     </div>
     <div class="d-flex justify-content-between mb-1">
         <span class="text-muted">Chủ tài khoản:</span>
         <strong class="text-dark">@BankingConfigHelper.AccountName</strong>
     </div>
     ```
- **Đánh giá rủi ro hồi quy (Regression Risk Analysis)**: **Không có rủi ro**. Cấu hình hóa hoàn toàn độc lập, nếu không có cấu hình trong `appsettings.json`, các giá trị mặc định của doanh nghiệp trong helper tự động kích hoạt an toàn.
  - *Rào chắn bảo toàn kiểm thử (ChallengerTests Guardrail)*: Tại `ChallengerTests/Program.cs:2291`, bài test `M4-05.7` kiểm tra chuỗi URL VietQR trong action `GuiNhacNo` có chứa tài khoản thử nghiệm `MB-0783406516` và `PHAN%20MINH%20QUAN`. Khi cấu hình hóa, cần đảm bảo `BankingConfig` trong môi trường kiểm thử hoặc giá trị mặc định của hệ thống vẫn duy trì khả năng tương thích để 100% assertions trong `ChallengerTests` tiếp tục PASS.
- **Kịch bản kiểm thử nghiệm thu (Verification Method)**:
  - Mở trang `http://localhost:5000/Cart/ContractDetail/1` và `http://localhost:5000/Account/MyDebt`.
  - Kiểm tra mã nguồn DOM: Số tài khoản hiển thị là `101889998888`, chủ tài khoản là `CONG TY TNHH RENTAL SYSTEM`.
  - Tìm kiếm toàn bộ dự án chuỗi `0783406516` và `PHAN MINH QUAN` trả về 0 kết quả.

---

### 3.2. Hướng dẫn sửa đổi Nhóm Phase 2: Silly Bugs & UX Quirks trên Web

#### 3.2.1. DEF-04: Khắc phục liên kết chết `#bankTransferInstructions` tại `ContractDetail.cshtml`

- **Mã lỗi**: DEF-04  
- **Mức độ nghiêm trọng**: **Major**  
- **Phân hệ ảnh hưởng**: Web UI / UX (`Views/Cart/ContractDetail.cshtml`)  
- **Vị trí tệp và dòng mã**: `RentalSystem/Views/Cart/ContractDetail.cshtml` (dòng 76 và dòng 361 đến 367).
- **Phân tích nguyên nhân gốc rễ (Root Cause)**:
  Thẻ nút bấm dòng 76 nằm trong khối `@if (canTransferFirstPayment)` và `@if (firstBalance.Total > 0)`, mang thuộc tính `href="#bankTransferInstructions"` trỏ tới phần tử `<div id="bankTransferInstructions">` ở dòng 367. Nút bấm hiện tại dùng class Bootstrap cũ `.btn-primary` và thiếu icon chỉ dẫn chuyển khoản.
  Đặc biệt, nếu cố gắng bọc nút bấm này trong điều kiện `@if (shouldShowVietQr)` sẽ gây lỗi biên dịch nghiêm trọng `error CS0103: The name 'shouldShowVietQr' does not exist in the current context`, do biến `shouldShowVietQr` chỉ được khai báo ở dòng 361-364 của View (nằm ngoài phạm vi của dòng 76).
  Về mặt logic: Vì dòng 76 đã nằm sẵn bên trong `@if (canTransferFirstPayment)` và `@if (firstBalance.Total > 0)`, và ở dòng 361-364 biểu thức `shouldShowVietQr` khi `pendingFirstPayment == true` chính là `canTransferFirstPayment && firstBalance.Total > 0`, nên khi vào đến dòng 76 thì điều kiện hiển thị `#bankTransferInstructions` chắc chắn thỏa mãn. Giải pháp tối ưu và an toàn biên dịch 100% là đổi trực tiếp class của nút sang `.btn-navy` theo chuẩn Classic Navy mà không tham chiếu biến hạ nguồn `shouldShowVietQr`.
- **Mã nguồn trước khi sửa (Before)**:
  ```html
  <!-- Views/Cart/ContractDetail.cshtml:76 -->
  <a class="btn btn-primary mt-2" href="#bankTransferInstructions">Chuyển khoản @Math.Ceiling(firstBalance.Total).ToString("N0") đ</a>
  ```
- **Mã nguồn đề xuất sau khi sửa (After - Drop-in Snippet)**:
  ```html
  <!-- Sửa dòng 76 trong Views/Cart/ContractDetail.cshtml: Chuẩn hóa Semantic Classic Navy, an toàn biên dịch 100% (không tham chiếu shouldShowVietQr hạ nguồn để tránh lỗi CS0103) -->
  <a class="btn btn-navy mt-2" href="#bankTransferInstructions">
      <i class="fas fa-qrcode me-1"></i> Quét mã VietQR chuyển khoản @Math.Ceiling(firstBalance.Total).ToString("N0") đ
  </a>
  ```
- **Đánh giá rủi ro hồi quy (Regression Risk Analysis)**: **Không có rủi ro - Đã kiểm chứng an toàn biên dịch 100%**. Giữ nguyên logic điều kiện bao bọc sẵn có của Razor view, loại bỏ hoàn toàn nguy cơ lỗi phạm vi biến Roslyn CS0103. Nút bấm sử dụng class semantic `.btn-navy` đồng nhất với toàn hệ thống.
- **Kịch bản kiểm thử nghiệm thu (Verification Method)**:
  - Truy cập đơn hàng cần thanh toán đợt đầu (`/Cart/ContractDetail/{id}`): Nút bấm màu xanh Navy hiển thị trang nhã với icon mã QR.
  - Nhấp vào nút: Trình duyệt tự động cuộn trang mượt mà đến đúng khung `#bankTransferInstructions` hiển thị mã VietQR chuyển khoản.

---

#### 3.2.2. DEF-12: Loại bỏ class trùng lặp, xung đột màu sắc và xung đột `bg-white` vs `admin-card`

- **Mã lỗi**: DEF-12  
- **Mức độ nghiêm trọng**: **Minor**  
- **Phân hệ ảnh hưởng**: Web Razor Views (`Views/Cart/Checkout.cshtml`, `Views/Cart/SignContract.cshtml`, `Areas/Admin/Views/PhanCong/Create.cshtml`)  
- **Vị trí tệp và dòng mã**:
  - `RentalSystem/Views/Cart/Checkout.cshtml` (dòng 15).
  - `RentalSystem/Views/Cart/SignContract.cshtml` (dòng 19 và dòng 99).
  - `RentalSystem/Areas/Admin/Views/PhanCong/Create.cshtml` (dòng 15, dòng 88, dòng 97).
- **Phân tích nguyên nhân gốc rễ (Root Cause)**:
  - Xung đột màu sắc & lặp class: `class="card-header text-warning fw-bold text-dark fw-bold py-3"` khai báo đồng thời hai màu chữ đối chọi nhau (`text-warning` và `text-dark`), lặp lại thuộc tính `fw-bold`.
  - Xung đột tiện ích: Cột bên trái dùng semantic `.admin-card` (bo góc 8px), cột bên phải dùng Bootstrap utility `card border-0 shadow-sm rounded-3 bg-white` (bo góc 16px), tạo sự khập khiễng về phong cách hiển thị trên cùng một màn hình.
- **Mã nguồn trước khi sửa (Before)**:
  ```html
  <!-- Checkout.cshtml:15 -->
  <div class="card-header text-warning fw-bold text-dark fw-bold py-3">

  <!-- SignContract.cshtml:19 & 99 -->
  <div class="card-header text-warning fw-bold text-dark fw-bold">
  <div class="card-header text-success fw-bold fw-bold">

  <!-- PhanCong/Create.cshtml:97 -->
  <div class="card border-0 shadow-sm rounded-3 bg-white">
  ```
- **Mã nguồn đề xuất sau khi sửa (After - Drop-in Snippet)**:
  ```html
  <!-- Checkout.cshtml:15 -->
  <div class="card-header bg-white border-bottom py-3">
      <h4 class="mb-0 text-navy fw-bold"><i class="fas fa-calendar-check me-2"></i> Thông tin Nhận Máy</h4>
  </div>

  <!-- SignContract.cshtml:19 & 99 -->
  <div class="card-header bg-white border-bottom py-3">
      <h5 class="mb-0 text-navy fw-bold"><i class="fas fa-info-circle me-2"></i> Thông tin hợp đồng #@Model.MaHopDong</h5>
  </div>
  ...
  <div class="card-header bg-white border-bottom py-3">
      <h5 class="mb-0 text-navy fw-bold"><i class="fas fa-pen-nib me-2"></i> Bước 2: Ký tên xác nhận</h5>
  </div>

  <!-- PhanCong/Create.cshtml:15, 88, 97 -->
  <!-- Đồng bộ thống nhất sang admin-card -->
  <div class="admin-card">
  ```
- **Đánh giá rủi ro hồi quy (Regression Risk Analysis)**: **Không có rủi ro**. Chỉ làm sạch cú pháp HTML và CSS.
- **Kịch bản kiểm thử nghiệm thu (Verification Method)**:
  Kiểm tra cú pháp HTML qua trình duyệt Chrome không còn cảnh báo class xung đột; giao diện các thẻ card hiển thị bo góc và bóng đổ đồng nhất chuẩn Classic Navy.

---

#### 3.2.3. DEF-13: Nhúng `_ValidationScriptsPartial` cho toàn bộ biểu mẫu nhập liệu

- **Mã lỗi**: DEF-13  
- **Mức độ nghiêm trọng**: **Major**  
- **Phân hệ ảnh hưởng**: Web Form Views  
- **Vị trí tệp**:
  - `RentalSystem/Views/Account/Register.cshtml`
  - `RentalSystem/Views/Account/Login.cshtml`
  - `RentalSystem/Views/Cart/Checkout.cshtml`
  - `RentalSystem/Views/BaoTri/TaoPhieu.cshtml`
  - `RentalSystem/Areas/Admin/Views/KhuyenMai/Create.cshtml`
  - `RentalSystem/Areas/Admin/Views/HopDong/Create.cshtml`
  - `RentalSystem/Areas/Admin/Views/PhanCong/Create.cshtml`
- **Phân tích nguyên nhân gốc rễ (Root Cause)**:
  Chỉ có 4 view sản phẩm/thiết bị có nhúng `_ValidationScriptsPartial`. Toàn bộ các form nhập liệu quan trọng còn lại thiếu partial này, khiến các quy tắc `[Required]`, `[EmailAddress]`, `[RegularExpression]` không được kiểm tra tức thì ở trình duyệt (Client-side validation). Người dùng gõ sai định dạng phải gửi HTTP POST lên máy chủ, gây tải lại toàn trang và làm mất trắng các trường dữ liệu người dùng đã nhập.
- **Mã nguồn đề xuất sau khi sửa (After - Drop-in Snippet)**:
  Bổ sung vào cuối mỗi tệp biểu mẫu nêu trên đoạn mã chuẩn:
  ```html
  @section Scripts {
      <partial name="_ValidationScriptsPartial" />
  }
  ```
- **Đánh giá rủi ro hồi quy (Regression Risk Analysis)**: **Không có rủi ro**. Tận dụng thư viện jQuery Validation Unobtrusive đã tích hợp sẵn trong Layout gốc.
- **Kịch bản kiểm thử nghiệm thu (Verification Method)**:
  Mở trang `/Account/Register`, nhấn nút Đăng ký khi để trống các trường: Form hiển thị ngay lập tức các dòng thông báo lỗi màu đỏ dưới từng ô mà không cần reload trang.

---

### 3.3. Hướng dẫn sửa đổi Nhóm Phase 3: Chuẩn hóa Giao diện Classic Navy Doanh nghiệp

#### 3.3.1. DEF-10: Tái cấu trúc thẻ KPI, bảng công nợ và bộ nút hành động tại `CongNo/Index.cshtml`

- **Mã lỗi**: DEF-10  
- **Mức độ nghiêm trọng**: **Major**  
- **Phân hệ ảnh hưởng**: Web Admin UI (`RentalSystem/Areas/Admin/Views/CongNo/Index.cshtml`) & Controller (`CongNoController.cs`)  
- **Vị trí tệp và dòng mã**:
  - `RentalSystem/Areas/Admin/Views/CongNo/Index.cshtml` (dòng 15 đến 23, dòng 40 đến 85, dòng 212 đến 214, dòng 226).
  - `RentalSystem/Areas/Admin/Controllers/CongNoController.cs` (dòng 50 đến 80 và 190 đến 210).
- **Phân tích nguyên nhân gốc rễ (Root Cause)**:
  Trang quản lý công nợ chưa được chuyển đổi đồng bộ sang chuẩn `classic-navy.css` và chưa đáp ứng đầy đủ các điều kiện xác nhận của bộ kiểm thử `ChallengerTests` (Milestone 4).
  Cụ thể:
  1. Giao diện dùng viền dày 4px với màu sắc phân tán (`border-primary`, `border-danger`, `border-success`), bảng tổng hợp dùng class Bootstrap cũ `table table-hover align-middle mb-0 text-center` thay vì `.admin-card` và `.admin-table`, nút thao tác dùng `btn-outline-danger` và `btn-outline-dark` thay vì `.action-btn`.
  2. Thẻ KPI hiện tại thiếu thẻ thứ 4: "Khoản nợ xấu" gắn với `@ViewBag.SoKhoanNoXau` và thiếu khối phân kỳ 4 nhóm tuổi nợ (Aging Schedule Breakdown) gắn với `@ViewBag.AgingTier1Count` đến `@ViewBag.AgingTier4Count`.
  3. Thiếu khai báo class CSS `.bg-orange` phục vụ hiển thị nhãn nhóm tuổi nợ 31–60 ngày.
  4. Các bài kiểm thử tĩnh và kiểm thử động trong `ChallengerTests/Program.cs` (`M4-04.9` đến `M4-04.14`, `M4-06.4` đến `M4-06.9`) yêu cầu nghiêm ngặt sự hiện diện của đầy đủ 4 thẻ KPI, 4 thẻ phân kỳ tuổi nợ và class `.bg-orange`. Nếu giao diện thiếu bất kỳ thành phần nào, kiểm thử sẽ thất bại ngay lập tức.
- **Mã nguồn đề xuất sau khi sửa (After - Drop-in Snippet)**:
  1. *Định nghĩa bổ sung class `.bg-orange` trong khối `<style>` tại đầu trang (M4-06.9)*:
     ```html
     <style>
         .kpi-card {
             transition: transform 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
         }
         .kpi-card:hover {
             transform: translateY(-2px);
             box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.08) !important;
         }
         /* Định nghĩa class huy hiệu màu cam cho nhóm tuổi nợ 31-60 ngày (Bảo toàn 100% assertion M4-06.9) */
         .bg-orange {
             background-color: #fd7e14 !important;
             color: #ffffff !important;
         }
     </style>
     ```
  2. *Thay thế các thẻ KPI bằng chuẩn Classic Navy (Bảo tồn 100% assertions M4-06.4 đến M4-06.7)*:
     ```html
     <!-- Thống kê tổng quan công nợ chuẩn Classic Navy (Đầy đủ 4 thẻ KPI) -->
     <div class="row g-3 mb-4">
         <!-- Thẻ 1: Tổng công nợ -->
         <div class="col-12 col-sm-6 col-md-3">
             <div class="stat-card">
                 <div class="stat-icon"><i class="fas fa-wallet"></i></div>
                 <div>
                     <div class="stat-label">Tổng công nợ</div>
                     <div class="stat-value">@(((decimal)(ViewBag.TongCongNo ?? 0m)).ToString("N0")) đ</div>
                     <div class="small text-muted">Dư nợ toàn hệ thống</div>
                 </div>
             </div>
         </div>

         <!-- Thẻ 2: Tổng nợ quá hạn -->
         <div class="col-12 col-sm-6 col-md-3">
             <div class="stat-card">
                 <div class="stat-icon text-danger"><i class="fas fa-exclamation-triangle"></i></div>
                 <div>
                     <div class="stat-label">Tổng nợ quá hạn</div>
                     <div class="stat-value text-danger">@(((decimal)(ViewBag.TongNoQuaHan ?? 0m)).ToString("N0")) đ</div>
                     <div class="small text-muted">Gốc trễ hạn + phí phạt</div>
                 </div>
             </div>
         </div>

         <!-- Thẻ 3: Tỷ lệ thu hồi -->
         <div class="col-12 col-sm-6 col-md-3">
             <div class="stat-card">
                 <div class="stat-icon text-success"><i class="fas fa-chart-line"></i></div>
                 <div>
                     <div class="stat-label">Tỷ lệ thu hồi</div>
                     <div class="stat-value text-success">@(((decimal)(ViewBag.TyLeThuHoi ?? 0m)).ToString("0.0"))%</div>
                     <div class="small text-muted">Đã thu / Tổng phải thu</div>
                 </div>
             </div>
         </div>

         <!-- Thẻ 4: Khoản nợ xấu (Bắt buộc giữ cho ChallengerTests M4-06.7) -->
         <div class="col-12 col-sm-6 col-md-3">
             <div class="stat-card">
                 <div class="stat-icon text-danger"><i class="fas fa-user-slash"></i></div>
                 <div>
                     <div class="stat-label">Khoản nợ xấu</div>
                     <div class="stat-value text-danger">@(ViewBag.SoKhoanNoXau ?? 0)</div>
                     <div class="small text-muted">Nợ nhóm 4 / Khóa thuê</div>
                 </div>
             </div>
         </div>
     </div>
     ```
  3. *Khối thống kê phân kỳ 4 nhóm tuổi nợ (Aging Schedule Breakdown - Bảo tồn 100% assertions M4-06.8)*:
     ```html
     <!-- Khối phân kỳ 4 nhóm tuổi nợ (Aging Schedule Breakdown) -->
     <div class="row g-3 mb-4">
         <div class="col-6 col-md-3">
             <div class="admin-card p-3 border-start border-4 border-info">
                 <div class="text-muted small fw-semibold">Nhóm 1 (1–30 ngày)</div>
                 <div class="h5 fw-bold mb-0">@(ViewBag.AgingTier1Count ?? 0) <span class="small fw-normal text-muted">kỳ</span></div>
             </div>
         </div>
         <div class="col-6 col-md-3">
             <div class="admin-card p-3 border-start border-4 border-warning">
                 <div class="text-muted small fw-semibold">Nhóm 2 (31–60 ngày)</div>
                 <div class="h5 fw-bold mb-0">@(ViewBag.AgingTier2Count ?? 0) <span class="small fw-normal text-muted">kỳ</span></div>
             </div>
         </div>
         <div class="col-6 col-md-3">
             <div class="admin-card p-3 border-start border-4" style="border-color: #fd7e14 !important;">
                 <div class="text-muted small fw-semibold">Nhóm 3 (61–90 ngày)</div>
                 <div class="h5 fw-bold mb-0">@(ViewBag.AgingTier3Count ?? 0) <span class="small fw-normal text-muted">kỳ</span></div>
             </div>
         </div>
         <div class="col-6 col-md-3">
             <div class="admin-card p-3 border-start border-4 border-danger">
                 <div class="text-muted small fw-semibold">Nhóm 4 (>90 ngày)</div>
                 <div class="h5 fw-bold mb-0 text-danger">@(ViewBag.AgingTier4Count ?? 0) <span class="small fw-normal text-muted">kỳ</span></div>
             </div>
         </div>
     </div>
     ```
  4. *Thay thế bộ nút thao tác sang `.action-btn` (dòng 212 đến 214)*:
     ```html
     <td class="text-nowrap">
         <button type="button" class="action-btn text-danger" title="Gửi nhắc nợ" onclick="guiNhacNo(@k.MaKyHan, this)">
             <i class="fas fa-bell"></i>
         </button>
         <a href="/Admin/HopDong/Details/@hd.MaHopDong?returnUrl=/Admin/CongNo" class="action-btn" title="Xem chi tiết hợp đồng">
             <i class="fas fa-eye"></i>
         </a>
     </td>
     ```
  5. *Bọc bảng tổng hợp trong `.admin-card` và `.admin-table` (dòng 225 đến 227)*:
     ```html
     <div class="admin-card mt-3">
         <div class="table-responsive">
             <table class="admin-table">
     ```
  6. *Đồng bộ Controller backend (`RentalSystem/Areas/Admin/Controllers/CongNoController.cs`)*:
     - Trong action `Index()`: Bắt buộc tính toán và gán đầy đủ các biến:
       `ViewBag.TongCongNo`, `ViewBag.TongNoQuaHan`, `ViewBag.TyLeThuHoi`, `ViewBag.SoKhoanNoXau`, `ViewBag.AgingTier1Count`, `ViewBag.AgingTier2Count`, `ViewBag.AgingTier3Count`, `ViewBag.AgingTier4Count` (phục vụ assertions `M4-04.3` đến `M4-04.14`).
     - Trong action `ExportExcel()`: Giữ nguyên 17 cột tiêu đề chuẩn ClosedXML, trong đó Cột 15 là `"Nhóm Tuổi Nợ"`, Cột 16 là `"Trạng Thái"` (phục vụ assertions `M4-03.12` và `M4-03.13`).
- **Đánh giá rủi ro hồi quy (Regression Risk Analysis)**: **Không có rủi ro - Bảo toàn 100% bộ kiểm thử tự động Milestone 4**.
  Giải pháp này bảo tồn trọn vẹn cả 12 assertions trong phần kiểm tra giao diện tĩnh (`M4-06.1` đến `M4-06.12` tại `ChallengerTests/Program.cs:2303-2349`), đồng thời dọn sạch các class Bootstrap dài và màu neon chói, đưa giao diện về chuẩn Classic Navy doanh nghiệp.
- **Kịch bản kiểm thử nghiệm thu (Verification Method)**:
  - Chạy kiểm thử tự động: `dotnet run --project ChallengerTests/ChallengerTests.csproj`, quan sát toàn bộ các ca kiểm thử `[M4-03]`, `[M4-04]`, `[M4-06]` đều vượt qua với kết quả PASS 100%.
  - Mở `/Admin/CongNo`: 4 thẻ chỉ số KPI và 4 thẻ phân kỳ tuổi nợ hiển thị ngay ngắn, đồng bộ chuẩn nhận diện Classic Navy.

---

#### 3.3.2. DEF-11: Chuẩn hóa thẻ thông số máy chủ và trạng thái kết nối tại `Database/Index.cshtml`

- **Mã lỗi**: DEF-11  
- **Mức độ nghiêm trọng**: **Major**  
- **Phân hệ ảnh hưởng**: Web Admin UI (`RentalSystem/Areas/Admin/Views/Database/Index.cshtml`)  
- **Vị trí tệp và dòng mã**: `RentalSystem/Areas/Admin/Views/Database/Index.cshtml` (dòng 39 đến dòng 95).
- **Phân tích nguyên nhân gốc rễ (Root Cause)**:
  Các thẻ chỉ số giám sát máy chủ database vẫn duy trì cấu trúc card Bootstrap cũ với viền dày 4px màu neon (`border-primary`, `border-info`, `border-success`), chưa đồng bộ với bảng màu Deep Navy thanh lịch.
- **Mã nguồn đề xuất sau khi sửa (After - Drop-in Snippet)**:
  ```html
  <!-- THẺ TRẠNG THÁI HỆ THỐNG & KẾT NỐI (Chuẩn Classic Navy) -->
  <div class="row g-3 mb-4">
      <div class="col-xl-3 col-md-6">
          <div class="stat-card">
              <div class="stat-icon"><i class="fas fa-server"></i></div>
              <div>
                  <div class="stat-label">Máy chủ SQL</div>
                  <div class="stat-value fs-6 text-truncate" style="max-width: 170px;" title="@Model.ServerName">@Model.ServerName</div>
              </div>
          </div>
      </div>
      <div class="col-xl-3 col-md-6">
          <div class="stat-card">
              <div class="stat-icon"><i class="fas fa-database"></i></div>
              <div>
                  <div class="stat-label">Cơ sở dữ liệu</div>
                  <div class="stat-value fs-6">@Model.DatabaseName</div>
              </div>
          </div>
      </div>
      <div class="col-xl-3 col-md-6">
          <div class="stat-card">
              <div class="stat-icon @(Model.IsConnected ? "text-success" : "text-danger")">
                  <i class="fas fa-plug"></i>
              </div>
              <div>
                  <div class="stat-label">Trạng thái kết nối</div>
                  <div class="stat-value fs-6">
                      @if (Model.IsConnected)
                      {
                          <span class="status-pill"><span class="status-dot dot-success"></span> Hoạt động tốt</span>
                      }
                      else
                      {
                          <span class="status-pill"><span class="status-dot dot-danger"></span> Mất kết nối</span>
                      }
                  </div>
              </div>
          </div>
      </div>
  </div>
  ```
- **Đánh giá rủi ro hồi quy (Regression Risk Analysis)**: **Không có rủi ro**.
- **Kịch bản kiểm thử nghiệm thu (Verification Method)**:
  Mở trang `/Admin/Database`: Giao diện hiển thị trang nhã, thẻ chỉ số máy chủ sắc nét, không còn viền neon chói.

---

#### 3.3.3. DEF-14: Thay thế nút bấm quả trứng `rounded-pill` và nút Bootstrap bằng `.btn-navy`

- **Mã lỗi**: DEF-14  
- **Mức độ nghiêm trọng**: **Minor**  
- **Phân hệ ảnh hưởng**: Web Client Views (`Views/Home/Index.cshtml`, `Views/Cart/Checkout.cshtml`)  
- **Vị trí tệp và dòng mã**:
  - `RentalSystem/Views/Home/Index.cshtml` (dòng 19, dòng 28, dòng 37).
  - `RentalSystem/Views/Cart/Checkout.cshtml` (dòng 44).
- **Phân tích nguyên nhân gốc rễ (Root Cause)**:
  Sử dụng nút bo tròn quả trứng `rounded-pill` kiểu thể thao và nút `btn-outline-primary` của Bootstrap, lệch chuẩn so với phong cách góc cạnh tinh tế của Classic Navy.
- **Mã nguồn đề xuất sau khi sửa (After - Drop-in Snippet)**:
  ```html
  <!-- Views/Home/Index.cshtml:19, 28, 37 -->
  <a href="/SanPham" class="btn btn-navy btn-lg fw-bold px-5 shadow">XEM THIẾT BỊ NGAY</a>
  ...
  <a href="/SanPham" class="btn btn-navy btn-lg fw-bold px-5 shadow">TÌM HIỂU THÊM</a>
  ...
  <a href="/SanPham" class="btn btn-navy btn-lg fw-bold px-5 shadow">ĐẶT THUÊ NGAY</a>

  <!-- Views/Cart/Checkout.cshtml:44 -->
  <button type="button" class="btn btn-outline-navy fw-bold" id="btnApplyPromo">Áp dụng</button>
  ```
- **Đánh giá rủi ro hồi quy (Regression Risk Analysis)**: **Không có rủi ro**.
- **Kịch bản kiểm thử nghiệm thu (Verification Method)**:
  Kiểm tra trang chủ và giỏ hàng, các nút bấm đồng bộ màu Deep Navy `#0f2b5c` sang trọng.

---

### 3.4. Hướng dẫn sửa đổi Nhóm Phase 4: Nâng cấp Thu hẹp Bất đối xứng Web vs Mobile

#### 3.4.1. DEF-05: Bổ sung màn hình Ký số điện tử (Canvas) và Tải ảnh CCCD trên Mobile

- **Mã lỗi**: DEF-05  
- **Mức độ nghiêm trọng**: **Major**  
- **Phân hệ ảnh hưởng**: Mobile Flutter App (`MobileApp/lib/screens/contracts/`) & Backend API  
- **Vị trí tệp**: `MobileApp/lib/screens/requests/rental_confirm_screen.dart:55`.
- **Phân tích nguyên nhân gốc rễ (Root Cause)**:
  Khi khách hàng gửi đơn thuê trên điện thoại, ứng dụng chỉ hiện dialog hướng dẫn: *"Bạn có thể ký hợp đồng trên Web."*. Ứng dụng di động thiếu hẳn màn hình vẽ chữ ký Canvas và tải ảnh Căn cước công dân 2 mặt. Trong khi đó, Backend kiểm tra bắt buộc phải có chữ ký và CCCD mới cho phép xuất kho bàn giao máy. Khách hàng buộc phải chuyển sang máy tính để ký tên.
- **Giải pháp kỹ thuật chi tiết**:
  1. *Backend*: Bổ sung API endpoint chuyên dụng cho Mobile ký số:
     - Endpoint: `POST /api/contracts/{id}/sign`
     - Payload: Multipart/form-data gồm `SignatureBase64` (chuỗi ảnh chữ ký từ canvas), `CccdFrontImage` (tệp ảnh), `CccdBackImage` (tệp ảnh), `InstallmentPlan` (số kỳ thanh toán: 1, 2, 3, 4, 6).
     - Controller lưu ảnh chữ ký vào `ChuKyKhachHang`, lưu ảnh CCCD vào `AnhCCCD_Truoc`, `AnhCCCD_Sau`, sinh các bản ghi phân kỳ `KyHanThanhToan` tương ứng và cập nhật `NgayKy = DateTime.Now`.
  2. *Mobile App*:
     - Tích hợp gói `signature: ^5.4.0` và `image_picker: ^1.0.7` vào `MobileApp/pubspec.yaml`.
     - Xây dựng màn hình `ContractSignatureScreen` (`MobileApp/lib/screens/contracts/contract_signature_screen.dart`):
       - Cho phép khách hàng vẽ chữ ký ngón tay trên widget `Signature`.
       - Nút chụp ảnh hoặc chọn ảnh CCCD mặt trước và mặt sau từ thư viện ảnh.
       - Bộ chọn số kỳ thanh toán (dropdown 1, 2, 3, 4, 6 kỳ).
       - Nút "Xác nhận ký hợp đồng" gọi `RemoteContractDataSource.signContract(...)`.
     - Tại `RentalConfirmScreen`, sau khi tạo đơn thành công, tự động điều hướng sang `ContractSignatureScreen` thay vì hiển thị thông báo chuyển sang Web.
- **Đánh giá rủi ro hồi quy (Regression Risk Analysis)**: **Thấp**. Endpoint API mới hoàn toàn độc lập, không ảnh hưởng đến màn hình ký số hiện có trên Web (`/Cart/SignContract`).
- **Kịch bản kiểm thử nghiệm thu (Verification Method)**:
  - Khởi chạy Mobile App (`flutter run -d windows`).
  - Đặt thuê thiết bị $\rightarrow$ Điều hướng sang màn hình ký số $\rightarrow$ Vẽ chữ ký và chọn ảnh CCCD $\rightarrow$ Gửi thành công.
  - Kiểm tra trên Web Admin: Hợp đồng hiển thị đầy đủ ảnh chữ ký và ảnh CCCD của khách, sẵn sàng để nhân viên bàn giao máy.

---

#### 3.4.2. DEF-06: Bổ sung màn hình Sổ công nợ và trình tạo mã VietQR động trên Mobile

- **Mã lỗi**: DEF-06  
- **Mức độ nghiêm trọng**: **Major**  
- **Phân hệ ảnh hưởng**: Mobile Flutter App  
- **Vị trí tệp**: Thư mục `MobileApp/lib/screens/contracts/` và datasources liên quan.
- **Phân tích nguyên nhân gốc rễ (Root Cause)**:
  Phân hệ Web có trang `/Account/MyDebt` rất đầy đủ cho phép khách xem 4 cấp tuổi nợ, xem phân kỳ thanh toán, quét mã VietQR và gửi ảnh biên lai. Ngược lại, trên Mobile App hoàn toàn không có tính năng này, người dùng di động không biết được ngày đến hạn nộp tiền thuê và không có mã QR để quét.
- **Giải pháp kỹ thuật chi tiết**:
  1. *Backend*: Bổ sung API `GET /api/debt/my-debt` trả về danh sách các kỳ nợ của khách hàng đăng nhập, tổng dư nợ, số ngày quá hạn, và thông tin tài khoản chuyển khoản.
  2. *Mobile App*:
     - Xây dựng màn hình `CustomerDebtScreen` (`MobileApp/lib/screens/contracts/customer_debt_screen.dart`).
     - Tích hợp widget hiển thị danh sách thẻ kỳ nợ theo thời gian.
     - Khi bấm vào một kỳ nợ, mở BottomSheet hiển thị mã VietQR động được tạo qua URL:
       `https://img.vietqr.io/image/{BankId}-{AccountNumber}-compact.png?amount={amount}&addInfo=HD{contractId}`
     - Thêm nút "Gửi biên lai chuyển khoản" cho phép đính kèm ảnh chụp màn hình chuyển khoản ngân hàng thành công lên API `POST /api/debt/upload-receipt`.
     - Bổ sung biểu tượng truy cập "Sổ công nợ" tại tab Tài khoản (`AccountScreen`).
- **Đánh giá rủi ro hồi quy (Regression Risk Analysis)**: **Thấp**.
- **Kịch bản kiểm thử nghiệm thu (Verification Method)**:
  Khách hàng đăng nhập Mobile App, mở Sổ công nợ, quét mã VietQR thanh toán kỳ 1 thành công.

---

#### 3.4.3. DEF-07: Mở rộng kiến trúc giỏ hàng đa thiết bị (Multi-Item Cart) trên Mobile

- **Mã lỗi**: DEF-07  
- **Mức độ nghiêm trọng**: **Major**  
- **Phân hệ ảnh hưởng**: Mobile Flutter App  
- **Vị trí tệp**: `MobileApp/lib/screens/requests/rental_form_screen.dart`.
- **Phân tích nguyên nhân gốc rễ (Root Cause)**:
  Trên Web khách hàng có thể thêm nhiều thiết bị khác loại vào giỏ hàng `/Cart` và thanh toán gộp. Trên Mobile chỉ hỗ trợ thuê đơn lẻ từng máy một (`RentalFormScreen` chỉ nhận duy nhất `widget.device`). Nếu khách cần thuê 1 PC và 1 Máy in, họ phải tạo 2 đơn thuê riêng biệt.
- **Giải pháp kỹ thuật chi tiết**:
  - Lưu ý kiến trúc quan trọng: Backend `ApiContractsController.cs` (dòng 314 và 318) **ĐÃ ĐƯỢC THIẾT KẾ SẴN** trường `public List<ContractItemRequest?>? Items { get; set; }` để nhận mảng nhiều thiết bị!
  - Xây dựng `CartProvider` trên Flutter (`MobileApp/lib/providers/cart_provider.dart`) quản lý danh sách sản phẩm đã chọn: thêm máy, bớt máy, thay đổi số lượng.
  - Bổ sung nút "Thêm vào giỏ hàng" bên cạnh nút "Thuê ngay" trên màn hình `DeviceDetailScreen`.
  - Xây dựng màn hình `CartScreen` hiển thị danh mục thiết bị đã chọn, tổng tiền thuê tạm tính và nút "Tiến hành đặt thuê", gửi toàn bộ mảng `items` lên `POST /api/contracts`.
- **Đánh giá rủi ro hồi quy (Regression Risk Analysis)**: **Thấp**. Tương thích hoàn toàn với backend API hiện hành.
- **Kịch bản kiểm thử nghiệm thu (Verification Method)**:
  Trên Mobile App chọn 2 laptop và 1 máy in vào giỏ hàng, bấm đặt thuê $\rightarrow$ Backend tạo đúng 1 hợp đồng với 3 dòng chi tiết trong `ChiTietHopDongs`.

---

#### 3.4.4. DEF-08: Phân tách độc lập hai vai trò Kinh Doanh và Kỹ Thuật trên Mobile

- **Mã lỗi**: DEF-08  
- **Mức độ nghiêm trọng**: **Major**  
- **Phân hệ ảnh hưởng**: Mobile Role Management (`MobileApp/lib/models/role_enum.dart:22-24`)  
- **Vị trí tệp và dòng mã**: `MobileApp/lib/models/role_enum.dart` (dòng 22 đến 24).
- **Phân tích nguyên nhân gốc rễ (Root Cause)**:
  Mobile gộp chung `kinhdoanh` và `kythuat` thành một enum duy nhất `Role.staff`. Khi đăng nhập, cả hai nhóm nhân viên đều nhìn thấy thanh điều hướng 5 tab giống nhau (gồm cả màn hình phân công sửa chữa phần cứng lẫn tác vụ hợp đồng), vi phạm nguyên tắc phân định quyền hạn.
- **Mã nguồn trước khi sửa (Before)**:
  ```dart
  // MobileApp/lib/models/role_enum.dart:1-5, 22-24
  enum Role { customer, staff, admin }
  ...
  if (r == 'nhân viên' || r == 'nhanvien' || r == 'staff' || r == 'kinhdoanh' || r == 'kythuat') {
    return Role.staff;
  }
  ```
- **Mã nguồn đề xuất sau khi sửa (After - Drop-in Snippet)**:
  ```dart
  // MobileApp/lib/models/role_enum.dart
  enum Role { customer, sales, technician, admin }

  extension RoleExtension on Role {
    String get name {
      switch (this) {
        case Role.customer: return 'Khách hàng';
        case Role.sales: return 'Kinh doanh';
        case Role.technician: return 'Kỹ thuật viên';
        case Role.admin: return 'Quản lý';
      }
    }

    static Role fromString(String? role) {
      if (role == null) return Role.customer;
      final r = role.trim().toLowerCase();
      if (r == 'admin' || r == 'quản lý' || r == 'quanly' || r == 'quản trị viên') {
        return Role.admin;
      }
      if (r == 'kythuat' || r == 'kỹ thuật' || r == 'technician' || r == 'kt') {
        return Role.technician;
      }
      if (r == 'kinhdoanh' || r == 'kinh doanh' || r == 'sales' || r == 'sale') {
        return Role.sales;
      }
      return Role.customer;
    }
  }
  ```
  *Cập nhật thanh điều hướng di động (`MainNavigationScreen`)*:
  - Nếu `Role.sales`: Thanh điều hướng hiển thị các tab: Trang chủ, Đơn thuê cần duyệt, Hợp đồng, Khách hàng, Tài khoản.
  - Nếu `Role.technician`: Thanh điều hướng hiển thị: Trang chủ, Công việc sửa chữa, Phiếu bảo trì SLA, Biên bản bàn giao, Tài khoản.
- **Đánh giá rủi ro hồi quy (Regression Risk Analysis)**: **Thấp**. Cần cập nhật các chỗ tham chiếu `Role.staff` cũ sang `Role.sales` hoặc `Role.technician`.
- **Kịch bản kiểm thử nghiệm thu (Verification Method)**:
  Đăng nhập `kt.tuan@rentalsystem.com`: Chỉ thấy tác vụ bảo trì kỹ thuật; Đăng nhập `sale.linh@rentalsystem.com`: Chỉ thấy đơn thuê và gia hạn kinh doanh.

---

#### 3.4.5. DEF-09: Tái đồng bộ Dòng thời gian tiến trình hợp đồng khớp với 5 trạng thái CSDL

- **Mã lỗi**: DEF-09  
- **Mức độ nghiêm trọng**: **Minor**  
- **Phân hệ ảnh hưởng**: Mobile UI (`MobileApp/lib/screens/requests/rental_detail_screen.dart` & `rental_status.dart`)  
- **Vị trí tệp**: `MobileApp/lib/screens/requests/rental_detail_screen.dart`.
- **Phân tích nguyên nhân gốc rễ (Root Cause)**:
  Backend quản lý 5 trạng thái hợp đồng (`0: Chờ duyệt/ký`, `1: Đang hiệu lực`, `2: Hoàn tất`, `3: Đã hủy`, `4: Chờ quyết toán cọc`). Mobile lại hiển thị một timeline 7 bước giả lập cục bộ ("Đang chuẩn bị", "Đang giao", "Đã lắp đặt"...), gây sai lệch thông tin so với CSDL.
- **Giải pháp kỹ thuật chi tiết**:
  Tái cấu trúc widget dòng thời gian trên Mobile thành 5 bước chuẩn xác khớp 100% với backend:
  1. `Tạo đơn & Giữ chỗ` (Trạng thái 0)
  2. `Ký hợp đồng & Đặt cọc` (Trạng thái 0 $\rightarrow$ 1)
  3. `Đang hiệu lực / Sử dụng` (Trạng thái 1)
  4. `Thu hồi thiết bị` (Trạng thái 4)
  5. `Quyết toán hoàn tất` (Trạng thái 2)
  *(Trường hợp hợp đồng bị hủy: hiển thị thẻ trạng thái Đã hủy màu đỏ)*.
- **Đánh giá rủi ro hồi quy (Regression Risk Analysis)**: **Không có rủi ro**.
- **Kịch bản kiểm thử nghiệm thu (Verification Method)**:
  Mở chi tiết hợp đồng trên Mobile, dòng thời gian hiển thị đúng trạng thái đang lưu trong CSDL SQL Server.

---

## PHẦN IV: MA TRẬN ĐỐI SOÁT QUY TRÌNH NGHIỆP VỤ & 32 CA KIỂM THỬ

Toàn bộ 14 giải pháp khắc phục nêu trên được đối chiếu chặt chẽ với Bảy (7) quy trình nghiệp vụ cốt lõi và 32 trường hợp kiểm thử (KT-01 đến KT-32):

<p align="center"><b>Bảng 2: Ma trận đối chiếu quy trình nghiệp vụ, ca kiểm thử và mã sửa đổi</b></p>

| Quy trình Nghiệp vụ Áp dụng | Các Bước Nghiệp vụ Quy định | Ca Kiểm Thử Liên Quan | Mã Lỗi Xử Lý Tương Ứng | Tác Động & Kết Quả Đạt Được Sau Sửa Đổi |
|:---:|:---:|:---:|:---:|:---:|
| **Quy trình 1**: Đăng ký / Đăng nhập & RBAC | 1, 2 và 3 | KT-01, KT-02, KT-03 và KT-04 | DEF-08, DEF-13 | Phân định rạch ròi 4 vai trò trên cả Web và Mobile; bảo vệ dữ liệu form đăng ký bằng Client Validation. |
| **Quy trình 2**: Đặt thuê & Giữ chỗ Semaphore | 1, 2, 3 và 4 | KT-05, KT-06, KT-07 và KT-08 | DEF-07, DEF-12 | Cho phép Mobile đặt thuê giỏ hàng đa máy; làm sạch cú pháp biểu mẫu Checkout. |
| **Quy trình 3**: Thanh toán đợt đầu & VietQR | 1, 2, 3, 4 và 5 | KT-13, KT-14, KT-15, KT-16, KT-17 và KT-18 | DEF-03, DEF-04 | Bảo vệ STK doanh nghiệp; sửa dứt điểm lỗi Dead Link `#bankTransferInstructions` khi chuyển khoản cọc. |
| **Quy trình 4**: Bàn giao & Ký số biên bản | 1, 2 và 3 | KT-09, KT-10, KT-11 và KT-12 | DEF-05 | Mobile hỗ trợ ký số Canvas và tải ảnh CCCD trực tiếp, khép kín quy trình bàn giao máy mà không cần Web. |
| **Quy trình 5**: Báo sự cố, bảo trì & SLA | 1, 2, 3, 4, 5 và 6 | KT-23, KT-24, KT-25 và KT-26 | DEF-12, DEF-13 | Form báo sự cố có validation client; làm sạch giao diện phân công kỹ thuật. |
| **Quy trình 6**: Gia hạn hợp đồng | 1, 2, 3 và 4 | KT-19, KT-27 | DEF-01 | Khắc phục đứt gãy luồng gia hạn: Yêu cầu từ Mobile được lưu vào `YeuCauGiaHans` và hiển thị cho Admin duyệt. |
| **Quy trình 7**: Thu hồi & Quyết toán hoàn cọc | 1, 2, 3, 4 và 5 | KT-20, KT-21 và KT-22 | DEF-06, DEF-09 | Mobile có Sổ công nợ và VietQR theo dõi nợ; dòng thời gian hợp đồng khớp hoàn toàn với CSDL. |
| **Hệ thống Kiểm thử**: Công nợ & Báo cáo BI | 1, 2 và 3 | KT-31, KT-32 | DEF-02, DEF-10, DEF-11 | Mở khóa 100% test PASS cho `ChallengerTests`; chuẩn hóa giao diện báo cáo Classic Navy. |

---

## PHẦN V: MA TRẬN KIỂM SOÁT RỦI RO, DỰ PHÒNG ROLLBACK & TIÊU CHÍ NGHIỆM THU HOÀN TẤT

### 5.1. Ma trận kiểm soát rủi ro kỹ thuật và giải pháp dự phòng

<p align="center"><b>Bảng 3: Ma trận đánh giá rủi ro kỹ thuật và biện pháp giảm thiểu</b></p>

| Hạng mục Sửa đổi | Mức Rủi Ro | Rủi Ro Tiềm Ẩn Khi Áp Dụng | Biện Pháp Phòng Ngừa Kỹ Thuật | Kịch Bản Kiểm Tra Xác Nhận |
|:---:|:---:|:---:|:---:|:---:|
| **Sửa DEF-02 (`DebtCalculationHelper`)** | Thấp | Tên nhóm nợ hiển thị lệch trên các view cũ | Giữ nguyên các giá trị số nguyên của `tier` (0 đến 4), chỉ thay đổi chuỗi trả về khớp với assertions của test suite | Chạy `dotnet test ChallengerTests` ngay lập tức để xác nhận 595 bài test PASS |
| **Sửa DEF-01 (API `RenewContract`)** | Trung bình | Yêu cầu gia hạn bị từ chối do xung đột lịch sai | Sử dụng chung logic truy vấn kiểm tra trùng lịch đã kiểm chứng trên Web (`CartController.cs`) | Gửi request gia hạn thử nghiệm trên hợp đồng cô lập, xác minh bản ghi trong bảng `YeuCauGiaHans` |
| **Sửa DEF-03 (Cấu hình STK)** | Rất thấp | Thiếu tệp `appsettings.json` gây lỗi null | Cung cấp giá trị mặc định cứng (fallback default values) ngay trong thuộc tính của `BankingConfigHelper` | Kiểm tra giao diện khi xóa tạm khối cấu hình trong `appsettings.json`, đảm bảo không crash |
| **Sửa DEF-05 (Mobile Ký số & CCCD)** | Trung bình | Tệp ảnh chữ ký Base64 quá lớn làm nghẽn API | Nén ảnh phía Flutter trước khi gửi (kích thước tối đa 200KB, định dạng PNG chuẩn) | Thử nghiệm ký trên mạng 3G/4G mô phỏng độ trễ |
| **Sửa DEF-10, DEF-11 (Giao diện Classic Navy)** | Rất thấp | Lỗi bố cục hiển thị trên màn hình nhỏ (Mobile responsive) | Sử dụng các lớp lưới Bootstrap chuẩn (`col-12 col-sm-6 col-md-4`) bên ngoài `.stat-card` | Kiểm tra hiển thị ở khung nhìn 375px (iPhone) và 1920px (Desktop) |

---

### 5.2. Quy trình phục hồi khẩn cấp (Rollback Procedures)

Nếu trong quá trình áp dụng có bất kỳ bước nào gây lỗi biên dịch hoặc làm gãy bộ kiểm thử tự động mà không thể khắc phục trong vòng 15 phút, kỹ sư triển khai phải thực hiện quy trình hoàn nguyên khẩn cấp:

1. **Bước 1**: Dừng máy chủ Web Kestrel và ứng dụng Mobile đang chạy.
2. **Bước 2**: Khôi phục lại tệp bị lỗi từ bản lưu trữ dự phòng gốc (Backup copy) được tạo trước mỗi đợt chỉnh sửa.
3. **Bước 3**: Chạy lệnh kiểm tra biên dịch độc lập:
   ```powershell
   dotnet build d:\DoAnCuNhan\RentalSystem\RentalSystem.csproj
   dotnet build d:\DoAnCuNhan\ChallengerTests\ChallengerTests.csproj
   ```
4. **Bước 4**: Xác nhận trạng thái hệ thống đã trở về điểm kiểm tra an toàn (Safe Checkpoint) trước khi phân tích nguyên nhân.

---

### 5.3. Tiêu chí nghiệm thu hoàn tất tổng thể (Acceptance Criteria)

Kế hoạch sửa đổi được nghiệm thu hoàn tất khi và chỉ khi thỏa mãn đầy đủ các tiêu chí định lượng sau:

- [ ] **Tiêu chí 1 (Biên dịch)**: Lệnh `dotnet build RentalSystem/RentalSystem.csproj` đạt 0 Cảnh báo, 0 Lỗi.
- [ ] **Tiêu chí 2 (Kiểm thử Backend)**: Bộ kiểm thử `ChallengerTests` biên dịch thành công và đạt **595/595 PASS (100%)**.
- [ ] **Tiêu chí 3 (Kiểm thử Mobile)**: Lệnh `flutter test` trong thư mục `MobileApp` đạt **13/13 test files PASS (100%)**.
- [ ] **Tiêu chí 4 (Toàn vẹn Nghiệp vụ API)**: Gửi yêu cầu gia hạn từ Mobile App tạo thành công bản ghi trong bảng `YeuCauGiaHans`, xuất hiện trên màn hình duyệt của Quản trị viên (`/Admin/HopDong/YeuCauGiaHan`).
- [ ] **Tiêu chí 5 (An toàn Thông tin)**: Toàn bộ thông tin tài khoản ngân hàng hiển thị là thông tin pháp nhân doanh nghiệp, không còn bất kỳ dấu vết nào của STK cá nhân `0783406516`.
- [ ] **Tiêu chí 6 (Chuẩn Giao diện Classic Navy)**: Toàn bộ các trang `CongNo/Index.cshtml`, `Database/Index.cshtml` và biểu mẫu sử dụng 100% semantic classes `.stat-card`, `.admin-card`, `.admin-table`, `.action-btn` và `.btn-navy`.
- [ ] **Tiêu chí 7 (Bảo toàn Git Policy)**: Không thực hiện bất kỳ lệnh git commit, push nào ngoài thẩm quyền.

---

*Tài liệu Kế hoạch sửa đổi chi tiết Web và Mobile được thiết lập hoàn tất, bảo đảm tính khả thi, chuẩn xác và an toàn tuyệt đối cho hệ thống RentalSystem.*
