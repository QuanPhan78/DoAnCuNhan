# BÁO CÁO ĐỐI CHIẾU VÀ KẾ HOẠCH HOÀN THIỆN NỘI DUNG KHÓA LUẬN TỐT NGHIỆP THEO ĐỀ CƯƠNG CHI TIẾT (MÃ ĐỀ TÀI: CNTT-KLCN058)

> **Cơ sở đối chiếu**:
> - **Văn bản gốc**: Đề cương chi tiết Khóa luận cử nhân ngành CNTT năm học 2026 – 2027 (Mã đề tài: `CNTT-KLCN058`), Trường Đại học Công Thương TP.HCM (HUIT), đã được Trưởng bộ môn và 02 Giảng viên hướng dẫn ký duyệt.
> - **Tài liệu Word thực tế**: Thống nhất duy trì DUY NHẤT 01 TỆP WORD CHÍNH THỨC trong toàn bộ dự án (loại bỏ hoàn toàn việc nhân bản ra 2 tệp song song gây phân mảnh).
> - **Kịch bản sinh tài liệu**: `tools/build_master_thesis.py` (chỉ xuất duy nhất 01 file đích).
> - **Nguyên tắc an toàn**: **TUYỆT ĐỐI KHÔNG** cập nhật, ghi đè hoặc chỉnh sửa tệp Word khi chưa có sự phê duyệt rõ ràng từ người dùng.

---

## PHẦN I. MA TRẬN ĐỐI CHIẾU CHI TIẾT (PDF ĐỀ CƯƠNG vs. FILE WORD HIỆN TẠI)

### 1. Thông Tin Hành Chính & Pháp Lý

| Tiêu chí | Đề cương chi tiết (File PDF đã duyệt) | File Word hiện tại (`KHOA_LUAN_...docx`) | Đánh giá & Trạng thái | Giải pháp điều chỉnh |
|---|---|---|---|---|
| **Mã đề tài** | `CNTT-KLCN058` | Chưa có mã đề tài trên trang bìa chính và trang phụ bìa | ⚠️ Thiếu thông tin bắt buộc | Bổ sung dòng `Mã đề tài: CNTT-KLCN058` vào bìa ngoài và bìa trong |
| **Tên đề tài** | Xây dựng hệ thống quản lý cho thuê thiết bị. | XÂY DỰNG HỆ THỐNG QUẢN LÝ CHO THUÊ THIẾT BỊ (RENTALSYSTEM) | ✅ Phù hợp (giữ nguyên tên có kèm định danh hệ thống) | Giữ nguyên |
| **Giảng viên hướng dẫn** | 1. **ThS. Vũ Văn Vinh** (GVHD1, Trưởng bộ môn)<br>Email: `vinhvv@huit.edu.vn` - ĐT: `0909 443886`<br>2. **ThS. Nguyễn Trần Duy Khang** (GVHD2)<br>Email: `nguyentranduykhangts@gmail.com` - ĐT: `0366361437` | Đang để chữ giữ chỗ (Placeholder):<br>`ThS. [Họ tên Giảng viên hướng dẫn]`<br>`TS. [Họ tên Cán bộ phản biện]` | 🚨 **Sai lệch nghiêm trọng** | Điền chính xác học vị và họ tên của 2 Thầy vào Bìa, Phụ bìa, Lời cảm ơn và Phiếu nhận xét GVHD |
| **Nhóm sinh viên thực hiện** | Bản PDF ghi tên mẫu của nhóm khác (Đạt, Toàn, Trọng) | Đang thể hiện đúng 2 sinh viên tác giả thực tế:<br>1. **Hồ Sĩ Tuấn** – MSSV: `2001230725` – Lớp `14DHTH09`<br>2. **Phan Minh Quân** – MSSV: `2001230726` – Lớp `14DHTH09` | ✅ **Đã xác nhận giữ đúng 2 sinh viên thực tế** | Duy trì nhất quán danh sách 2 sinh viên (Hồ Sĩ Tuấn, Phan Minh Quân) xuyên suốt toàn bộ tài liệu |
| **Thời gian thực hiện** | 12 tuần: từ ngày 17/08/2026 tới ngày 08/11/2026 | Chỉ ghi chung chung năm 2026 | ⚠️ Thiếu mốc thời gian đề cương | Bổ sung khung thời gian 12 tuần vào Phần Mở Đầu và Kế hoạch thực hiện |

---

### 2. Mục Tiêu, Phạm Vi & Nền Tảng Công Nghệ

| Tiêu chí | Đề cương chi tiết (File PDF đã duyệt) | File Word hiện tại (`KHOA_LUAN_...docx`) | Đánh giá & Trạng thái | Giải pháp điều chỉnh |
|---|---|---|---|---|
| **Số lượng nền tảng** | **02 nền tảng bắt buộc**: Website và Mobile App (Mục 5, Mục 6, CLO2.2, Tuần 3, 5, 8) | Tập trung vào ASP.NET Core MVC (Web Responsive). Mục 3 (Hạn chế đề tài) trong Kết luận lại ghi: *"chưa xây dựng ứng dụng di động bản địa..."* | 🚨 **Mâu thuẫn trực tiếp với Đề cương** | Xóa câu mâu thuẫn ở phần Hạn chế; làm rõ kiến trúc phân hệ Mobile App (PWA / Mobile Client) kết nối Backend RESTful API |
| **Hệ thống Backend API** | "Xây dựng hệ thống API chung (Backend) phục vụ cho Website và Mobile App" (Tuần 5, CLO1.1 - 0.25đ) | Chưa có mục riêng trình bày thiết kế và đặc tả kỹ thuật RESTful API kết nối Mobile | ⚠️ Thiếu minh chứng điểm CLO1.1 | Bổ sung tiểu mục trình bày Kiến trúc RESTful Web API chung (OpenAPI / Swagger, JWT, JSON Data Contract) |
| **Giao diện di động** | CLO2.2 (0.5đ): "Thiết kế giao diện website và ứng dụng di động" | Mới chỉ có thiết kế giao diện Web Responsive trên Desktop/Tablet | ⚠️ Thiếu minh chứng CLO2.2 di động | Bổ sung hình ảnh thiết kế / mockup giao diện Mobile App cho Khách hàng & Kỹ thuật viên |

---

### 3. Nghiệp Vụ Khảo Sát & Thu Thập Biểu Mẫu (CLO1.1)

| Tiêu chí | Đề cương chi tiết (File PDF đã duyệt) | File Word hiện tại (`KHOA_LUAN_...docx`) | Đánh giá & Trạng thái | Giải pháp điều chỉnh |
|---|---|---|---|---|
| **Khảo sát hiện trạng & Thu thập biểu mẫu** | Mục tiêu 1 & CLO1.1 (0.5đ): "Khảo sát hiện trạng... Thu thập các biểu mẫu liên quan tới hoạt động của doanh nghiệp." | Đã có phân tích quy trình nghiệp vụ truyền thống nhưng thiếu các biểu mẫu chụp từ thực tế khảo sát | ⚠️ Chưa tối ưu điểm số khảo sát thực tế | Đưa các biểu mẫu thu thập thực tế (Hợp đồng thuê laptop mẫu từ doanh nghiệp ICT, Biên bản bàn giao máy, Phiếu báo sự cố) vào Chương 1 |

---

### 4. 4 Nhóm Chức Năng Cốt Lõi Theo Thang Điểm Đề Cương (CLO3 - 3.5 Điểm)

| Nhóm chức năng theo Đề Cương | Yêu cầu chi tiết trong PDF | Tình trạng trong File Word | Đánh giá & Giải pháp |
|---|---|---|---|
| **Chức năng cơ bản (0.5đ)** | Đăng nhập, đăng xuất, **backup & restore CSDL** | Đã có đăng nhập/đăng xuất; Mã nguồn C# đã có sẵn `DatabaseController.cs` (JSON Backup/Restore 18 bảng an toàn với Transaction), nhưng **trong Word mới chỉ nhắc 1 dòng mơ hồ ở Chương 5**! | ⚠️ **CẦN BỔ SUNG GẤP**: Trình bày chi tiết giải thuật Backup & Restore CSDL tại Chương 4 và kịch bản kiểm thử tại Chương 5 để lấy trọn 0.5đ CLO3 |
| **Chức năng 01 (0.75đ)** | - Quản lý thiết bị, loại hình cho thuê (0.25đ)<br>- Quản lý khách hàng, lịch sử thuê (0.25đ)<br>- Quản lý nhân viên, phân công công việc (0.25đ) | Đã có đầy đủ trong Chương 2, 3, 4 | ✅ Đạt yêu cầu |
| **Chức năng 02 (1.50đ)** | - Đề xuất thuê, lập hợp đồng, chuyển giao (0.5đ)<br>- Vận hành thiết bị ở đơn vị thuê (0.5đ)<br>- Sửa chữa bảo trì & đảm bảo hoạt động (0.5đ) | Đã có luồng đặt máy, SemaphoreSlim, biên bản giao nhận, phiếu bảo trì | ✅ Đạt yêu cầu |
| **Chức năng 03 (0.75đ)** | - Phân quyền hệ thống (0.25đ)<br>- Báo và đánh giá kết quả bảo trì (0.25đ)<br>- Quản lý phản hồi trong đơn vị thuê (0.25đ) | Phân quyền RBAC 4 vai trò rất chuẩn; tuy nhiên luồng Khách hàng chấm điểm sao (Rating) đánh giá dịch vụ kỹ thuật viên chưa tách thành Use Case độc lập | ⚠️ **CẦN LÀM RÕ**: Bổ sung Use Case `UC_CUS_06: Đánh giá chất lượng dịch vụ bảo trì` và thiết kế màn hình đánh giá của khách hàng |
| **Chức năng 04 (0.50đ)** | - Kết xuất các biểu mẫu (0.25đ)<br>- Thống kê báo cáo (0.25đ) | Đã có xuất báo cáo Excel ClosedXML, nhưng chưa làm nổi bật cơ chế in/xuất Hợp đồng điện tử và Biên bản bàn giao | ⚠️ **CẦN NÂNG CẤP**: Nêu bật cơ chế kết xuất biểu mẫu Hợp đồng & Biên bản bàn giao có chữ ký số Canvas |

---

### 5. Kế Hoạch & Phân Công Công Việc 12 Tuần (CLO6 - 0.25 Điểm)

| Tiêu chí | Đề cương chi tiết (File PDF đã duyệt) | File Word hiện tại (`KHOA_LUAN_...docx`) | Đánh giá & Giải pháp |
|---|---|---|---|
| **Kế hoạch 12 tuần & Phân công** | Quy định chi tiết nội dung công việc từng tuần từ Tuần 1 đến Tuần 12 | Chưa có Bảng phân công công việc 12 tuần cho 2 sinh viên (Hồ Sĩ Tuấn, Phan Minh Quân) | ⚠️ **THIẾU MINH CHỨNG CLO6**: Bổ sung Bảng tiến độ 12 tuần và Ma trận trách nhiệm phân công nhiệm vụ vào Phần Mở Đầu |

---

### 6. Danh Mục Tài Liệu Tham Khảo (CLO5.1)

| Tiêu chí | Đề cương chi tiết (File PDF đã duyệt) | File Word hiện tại (`KHOA_LUAN_...docx`) | Đánh giá & Giải pháp |
|---|---|---|---|
| **Giáo trình cốt lõi của Khoa CNTT HUIT** | Đề cương quy định 5 tài liệu bắt buộc:<br>[1] Bài giảng PTHTTT - HUIT<br>[2] Bài giảng CNPM - HUIT<br>[3] Giáo trình PT&TK HTTT Hướng đối tượng (P.N. Cương, N.T.M. Thư, H.B. Quốc)<br>[4] C# OOP (S. Kendal)<br>[5] Software Engineering (I. Sommerville) | Hiện có 15 tài liệu tham khảo quốc tế (Microsoft, EMVCo, NAPAS, Martin...), nhưng **THIẾU** các giáo trình và bài giảng nội bộ HUIT | ⚠️ **CẦN ĐIỀU CHỈNH**: Bổ sung 5 tài liệu chuẩn của Đề cương vào các vị trí đầu tiên [1] đến [5] trong Danh mục Tài liệu tham khảo |

---

## PHẦN II. KẾ HOẠCH TRIỂN KHAI HOÀN THIỆN TỪNG CHƯƠNG (ROADMAP)

### Giai đoạn 1: Chuẩn Hóa Thông Tin Hành Chính & Trang Sơ Bộ
1. **Trang Bìa Chính (Page 1) & Trang Bìa Phụ (Page 2)**:
   - Thêm dòng: **MÃ ĐỀ TÀI: CNTT-KLCN058**.
   - Sinh viên thực hiện (2 sinh viên):
     1. `2001230725 – Hồ Sĩ Tuấn – Lớp: 14DHTH09`
     2. `2001230726 – Phan Minh Quân – Lớp: 14DHTH09`
   - Cán bộ hướng dẫn:
     - `GVHD 1: ThS. Vũ Văn Vinh` (Trưởng bộ môn)
     - `GVHD 2: ThS. Nguyễn Trần Duy Khang`
2. **Trang Lời Cảm Ơn (Page i)**:
   - Cập nhật lời tri ân trang trọng đến ThS. Vũ Văn Vinh và ThS. Nguyễn Trần Duy Khang.
   - Ký tên: Hồ Sĩ Tuấn – Phan Minh Quân.
3. **Trang Nhận Xét của GVHD (Page iii)**:
   - Cập nhật chính xác thông tin 2 sinh viên và 2 Giảng viên hướng dẫn.

---

### Giai đoạn 2: Phần Mở Đầu & Bảng Phân Công 12 Tuần (CLO1.1, CLO6)
1. **Mục tiêu đề tài**:
   - Khẳng định mục tiêu xây dựng giải pháp đồng bộ trên cả **02 nền tảng: Website và Mobile App**, vận hành trên nền tảng **Hệ thống API Backend chung**.
2. **Kế hoạch 12 tuần & Ma trận phân công nhiệm vụ (CLO6)**:
   - Xây dựng Bảng tiến độ 12 tuần (từ 17/08/2026 đến 08/11/2026) phân chia rõ ràng giữa 2 sinh viên:
     - **Hồ Sĩ Tuấn (Trưởng nhóm)**: Khảo sát nghiệp vụ, thiết kế kiến trúc phân tầng, cài đặt Backend API, cơ chế kiểm soát tương tranh SemaphoreSlim, tích hợp thanh toán VietQR động NAPAS 247, module Sao lưu & Khôi phục CSDL.
     - **Phan Minh Quân**: Thiết kế CSDL (18 bảng 3NF), xây dựng giao diện Quản trị Admin Executive Navy, phân hệ Mobile App / Web Client khách hàng (Đặt thuê, Báo sự cố, Đánh giá chất lượng, Ký số Canvas), kiểm thử tự động 12 ca sử dụng.

---

### Giai đoạn 3: Bổ Sung Biểu Mẫu Thực Tế Thu Thập (Chương 1 - CLO1.1)
1. Bổ sung tiểu mục **1.3.1. Các biểu mẫu nghiệp vụ thu thập từ thực tế doanh nghiệp**:
   - Trình bày mẫu Hợp đồng cho thuê thiết bị công nghệ (khảo sát thực tế doanh nghiệp dịch vụ ICT Sài Gòn).
   - Mẫu Biên bản bàn giao thiết bị có xác nhận số Serial vật lý và chữ ký khách hàng.
   - Mẫu Phiếu báo sự cố kỹ thuật và đề xuất đổi máy backup.
   - Mẫu Biên bản nghiệm thu thu hồi máy và thanh lý cọc.

---

### Giai đoạn 4: Bổ Sung Use Case Đánh Giá & Phân Hệ Mobile App (Chương 2 & Chương 3)
1. **Chương 2 (Phân tích hệ thống)**:
   - Bổ sung đặc tả Use Case `UC_CUS_06: Đánh giá chất lượng dịch vụ bảo trì` (Khách hàng chấm điểm 1-5 sao và để lại phản hồi sau khi KTV hoàn thành sửa chữa).
   - Bổ sung đặc tả tương tác API giữa Backend và Mobile App.
2. **Chương 3 (Thiết kế hệ thống)**:
   - Bổ sung tiểu mục **3.2.3. Thiết kế giao diện ứng dụng di động (Mobile App)**:
     - Màn hình di động tra cứu danh mục máy và đặt thuê trực tuyến.
     - Màn hình di động gửi ticket báo sự cố kèm ảnh chụp hiện trường.
     - Màn hình di động dành cho Kỹ thuật viên tiếp nhận lịch sửa chữa và thao tác đổi máy backup.

---

### Giai đoạn 5: Minh Chứng Module Backup & Restore và RESTful API (Chương 4 & Chương 5 - CLO3, CLO4)
1. **Chương 4 (Cài đặt hệ thống)**:
   - Bổ sung mục **4.3.5. Cài đặt hệ thống API Backend dùng chung (RESTful API / Swagger)**: Phục vụ truyền tải dữ liệu JSON hai chiều an toàn giữa hệ thống máy chủ và ứng dụng di động.
   - Bổ sung mục **4.3.6. Cài đặt module Sao lưu và Khôi phục CSDL an toàn (Database Backup & Restore)**: Trình bày chi tiết mã nguồn trong `Areas/Admin/Controllers/DatabaseController.cs` (cơ chế xuất/nhập tệp JSON toàn vẹn 18 bảng, kỹ thuật xử lý ngắt ràng buộc khóa ngoại `NOCHECK CONSTRAINT` và kích hoạt `IDENTITY_INSERT`).
2. **Chương 5 (Thử nghiệm và triển khai)**:
   - Bổ sung ca kiểm thử `TC-13: Kiểm thử chức năng Sao lưu và Khôi phục CSDL an toàn (18 bảng)`.
   - Bổ sung ca kiểm thử `TC-14: Kiểm thử gọi RESTful API từ ứng dụng di động`.

---

### Giai đoạn 6: Hoàn Thiện Phần Kết Luận & Tài Liệu Tham Khảo (CLO5.1)
1. **Phần Kết luận**:
   - Điều chỉnh mục "Hạn chế đề tài": Không dùng câu "chưa xây dựng Mobile App" vì mâu thuẫn với đề cương; thay bằng: *"Hệ thống đã xây dựng kiến trúc RESTful API phục vụ Mobile App, hướng phát triển tiếp theo là tối ưu hóa tính năng hoạt động ngoại tuyến (Offline-First) và đồng bộ nền (Background Sync) qua camera quét Barcode chuyên dụng"*.
2. **Danh mục Tài liệu tham khảo**:
   - Bổ sung 5 tài liệu chuẩn của Đề cương vào các vị trí đầu tiên `[1]` đến `[5]`.
   - Đánh số lại các tài liệu chuyên ngành quốc tế tiếp theo từ `[6]` đến `[20]`.

---

## PHẦN III. KẾ HOẠCH BẢO ĐẢM CHẤT LƯỢNG VÀ AN TOÀN HỆ THỐNG

| Tiêu chí | Mục tiêu kiểm soát | Phương thức kiểm tra |
|---|---|---|
| **Toàn vẹn File Word** | Tuyệt đối không can thiệp file docx khi người dùng chưa bấm nút đồng ý | Kiểm tra thuộc tính `LastWriteTime` của file |
| **Biên dịch hệ thống** | 0 Lỗi, 0 Cảnh báo (0 Errors, 0 Warnings) | `dotnet build RentalSystem\RentalSystem.sln` |
| **Kiểm thử tự động C#** | 100% PASS (595/595 bài test) | `dotnet run --project ChallengerTests\ChallengerTests.csproj` |
| **Kiểm định chất lượng luận văn** | 100/100 Điểm Rubric HUIT (33/33 tests PASS) | `python test_thesis_quality.py --fast` |
| **Chính sách Git** | Không tự ý chạy `git commit`, `git add`, `git push` | Duy trì trạng thái Git sạch theo chỉ thị của người dùng |
