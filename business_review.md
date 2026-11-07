# BÁO CÁO ĐÁNH GIÁ TOÀN DIỆN NGHIỆP VỤ HỆ THỐNG QUẢN LÝ CHO THUÊ THIẾT BỊ RENTAL SYSTEM
## BUSINESS PROCESS REVIEW REPORT — ASP.NET CORE MVC PROJECT

> **Dự án:** Rental System — Hệ thống Quản lý Cho thuê Thiết bị Công nghệ  
> **Nền tảng công nghệ:** ASP.NET Core 9.0 MVC, Entity Framework Core, SQL Server, Bootstrap 5, Razor Views  
> **Đối tượng hướng tới:** Nhóm phát triển sinh viên, Giảng viên hướng dẫn & Hội đồng đánh giá Đồ án Cử nhân  
> **Mục tiêu tài liệu:** Rà soát tĩnh toàn diện nghiệp vụ (Static Business Process Review), nhận diện các mắt xích quy trình còn thiếu, các trạng thái nhập nhằng, các trường hợp biên (edge cases) chưa được xử lý và sự bất đối xứng thông tin giữa Admin và Khách hàng; từ đó đưa ra lộ trình cải tiến thiết thực, chuẩn chỉnh và dễ áp dụng.  
> **Nguyên tắc rà soát:** Không chỉnh sửa mã nguồn hệ thống; giữ nguyên hiện trạng mã nguồn để phục vụ đánh giá độc lập.

---

## LỜI MỞ ĐẦU & TỔNG QUAN KIẾN TRÚC HỆ THỐNG (EXECUTIVE SUMMARY)

Chào các bạn sinh viên và thầy cô trong hội đồng chuyên môn!

Trong các dự án phần mềm cho thuê tài sản công nghệ (như Laptop, PC workstation, Máy ảnh, Máy lạnh, Thiết bị âm thanh), độ phức tạp lớn nhất không nằm ở giao diện hiển thị mà nằm ở **vòng đời vận hành thực tế** (Business Life-cycle) của tài sản và dòng tiền. Một chiếc máy tính xách tay có giá trị 25.000.000đ khi xuất khỏi kho không chỉ đơn thuần là một đơn hàng thương mại điện tử, mà nó kéo theo cả một chuỗi cam kết pháp lý: từ việc đặt cọc giữ máy, ký kết hợp đồng điện tử, kiểm tra hiện trạng ngoại quan lúc bàn giao, phân kỳ thanh toán trả góp, theo dõi sự cố kỹ thuật trong quá trình thuê, cho đến việc thu hồi máy, nghiệm thu hư hại và quyết toán hoàn trả tiền cọc cho khách.

Hiện tại, hệ thống **Rental System (ASP.NET Core MVC)** đã xây dựng được một nền tảng kỹ thuật rất đáng khen ngợi:
- Hệ thống hỗ trợ cả đặt hàng trực tuyến (`CartController.Checkout`) lẫn lập hợp đồng trực tiếp tại quầy (`HopDongController.Create`).
- Đã tích hợp chữ ký điện tử HTML5 Canvas chuyển đổi Base64 PNG (`ChuKyKhachHang`, `ChuKyNhanVien`) và lưu trữ ảnh chụp căn cước công dân (`AnhCMND`).
- Mô hình hóa thiết bị vật lý cụ thể theo số Serial (`ThietBi`) độc lập với danh mục mẫu mã (`SanPham`).
- Tự động chia nhỏ lịch trình trả góp theo kỳ hạn (`KyHanThanhToan`) và hỗ trợ tạo mã VietQR động để khách quét mã thanh toán.

Tuy nhiên, khi soi chiếu sâu vào mã nguồn dưới góc nhìn vận hành thực tế tại các doanh nghiệp cho thuê thiết bị, hệ thống vẫn tồn tại nhiều "khoảng trống quy trình" (Process Gaps), các trạng thái dữ liệu còn nhập nhằng và một số rủi ro thất thoát tài sản / dòng tiền.

Báo cáo này được cấu trúc thành **4 Phần trọng tâm** tương ứng với 4 phân hệ cốt lõi của bài toán:
1. **Phần 1: Phân hệ Hợp đồng (Contract Domain)**
2. **Phần 2: Phân hệ Thanh toán (Payment Domain)**
3. **Phần 3: Phân hệ Bảo trì (Maintenance Domain)**
4. **Phần 4: Phân hệ Quản lý Công nợ (Debt Management Domain)**

Mỗi vấn đề được phát hiện đều tuân thủ nghiêm ngặt cấu trúc 3 phần bắt buộc:
- **(1) Tên vấn đề**
- **(2) Mô tả tác động thực tế**
- **(3) Đề xuất cải thiện cụ thể**
đồng thời trích dẫn đầy đủ vị trí Controller, Action, Model, Razor View và dòng mã nguồn tương ứng.

---

# PHẦN 1: PHÂN HỆ HỢP ĐỒNG (CONTRACT DOMAIN)

Phân hệ Hợp đồng là "xương sống" pháp lý điều phối toàn bộ tài sản và cam kết giữa Cửa hàng và Khách thuê, liên kết giữa `HopDong`, `ChiTietHopDong`, `ThietBi`, `KyHanThanhToan` và `PhieuThu`. Dưới đây là 16 vấn đề nghiệp vụ được phát hiện trong phân hệ này.

---

### Vấn đề 1: Thiếu quy trình Hoàn trả tiền cọc và Quyết toán hoàn cọc khi kết thúc hợp đồng
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 401–428 (Action `UpdateStatus`, trường hợp `status == 2`).
  - `RentalSystem/Models/AppModels.cs`, dòng 76 (`TienDaCoc`), dòng 36 (`SanPham.TienCoc`).
  - `RentalSystem/Views/Document/InHopDong.cshtml`, dòng 141 (Điều khoản 4.2: *"Hoàn trả lại tiền cọc cho Bên A khi hợp đồng kết thúc và Bên B đã thu hồi thiết bị an toàn"*).
- **1. Tên vấn đề:** Thiếu quy trình Hoàn trả tiền cọc và Nghiệm thu quyết toán hoàn cọc khi thu hồi máy kết thúc hợp đồng.
- **2. Mô tả tác động thực tế:**
  Trong thực tế cho thuê thiết bị điện tử, tiền cọc là khoản tiền rất lớn nhằm bảo đảm an toàn cho tài sản (ví dụ: máy tính bàn PC Dell OptiPlex có tiền cọc lên tới 8.000.000đ). Trên văn bản hợp đồng in ra cho khách ký (`InHopDong.cshtml`), công ty cam kết sẽ hoàn trả tiền cọc này khi khách mang máy trả đầy đủ.
  Tuy nhiên, trong mã nguồn `HopDongController.UpdateStatus`, khi Admin bấm nút chuyển trạng thái sang `2` (Hoàn tất/Thu hồi), code chỉ kiểm tra xem khách đã nộp đủ tiền thuê chưa (`hopDong.TrangThaiThanhToan == 2`) và phí đền bù máy hỏng (`totalDamages`), sau đó lập tức đổi trạng thái máy về kho (`tb.TrangThai = 0`). Hệ thống **hoàn toàn không có nút Hoàn cọc, không có phiếu chi hoàn cọc, không ghi nhận ngày hoàn cọc hay tài khoản nhận lại tiền cọc của khách**. Hậu quả là số tiền cọc của khách bị "treo" vĩnh viễn trên sổ sách phần mềm; khách hàng không biết khi nào mình được nhận lại tiền; nhân viên không có căn cứ đối soát xem ca trước đã trả cọc cho khách hay chưa.
- **3. Đề xuất cải thiện cụ thể:**
  - Bổ sung bước "Nghiệm thu thiết bị & Quyết toán hoàn cọc" trong `HopDongController`:
    1. Khi Admin chọn chuyển trạng thái hợp đồng sang Hoàn tất (`status = 2`), hệ thống bật Modal quyết toán:
       $$\text{Tiền cọc thực hoàn} = \text{TienDaCoc} - \text{Tiền thuê còn thiếu} - \text{Phí bồi thường hư hỏng}$$
    2. Bổ sung trường `TrangThaiHoanCoc` (0: Chưa hoàn, 1: Đã hoàn cọc) vào model `HopDong`.
    3. Tự động sinh bản ghi chứng từ chi tiền (`PhieuChi` hoặc `PhieuThu` loại hoàn cọc âm) lưu lại phương thức hoàn trả (Tiền mặt hoặc Chuyển khoản ngân hàng), mã giao dịch và nhân viên thực hiện.

---

### Vấn đề 2: Thiếu quy trình Gia hạn hợp đồng đang hoạt động (Contract Extension / Renewal)
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Views/Document/InHopDong.cshtml`, dòng 131 (Quy định hợp đồng: *"Bên A có trách nhiệm báo trước 01 ngày nếu có nhu cầu gia hạn hợp đồng"*).
  - `RentalSystem/Controllers/CartController.cs`, dòng 574 và dòng 598 (`EditContract` POST chỉ cho phép chỉnh sửa ngày khi `chuaKy && hopDong.TrangThai == 0`).
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs` (Không có action gia hạn ngày kết thúc).
- **1. Tên vấn đề:** Thiếu quy trình tiếp nhận và phê duyệt Gia hạn hợp đồng đối với các đơn hàng đang thuê (`TrangThai == 1`).
- **2. Mô tả tác động thực tế:**
  Hợp đồng in ra có điều khoản cho phép khách báo trước để gia hạn. Giả sử sinh viên thuê laptop làm đồ án tốt nghiệp trong 1 tháng, đến ngày thứ 28 đồ án bị dời lịch bảo vệ thêm 1 tuần nên sinh viên muốn thuê thêm 7 ngày. Khi sinh viên đăng nhập vào hệ thống, nút chỉnh sửa đơn hàng đã biến mất từ lúc ký duyệt hợp đồng. Phía Admin cũng không có màn hình nào để sửa `NgayKetThuc` của hợp đồng đang chạy. Nếu muốn cho thuê tiếp, Admin buộc phải tạo một hợp đồng mới từ đầu, bắt khách làm thủ tục cọc lần hai, xé lẻ lịch sử thuê của thiết bị. Nếu không tạo đơn mới, hợp đồng cũ sẽ bị trôi vào trạng thái quá hạn trả máy, gây sai lệch báo cáo công nợ.
- **3. Đề xuất cải thiện cụ thể:**
  - Xây dựng tính năng "Yêu cầu Gia hạn hợp đồng":
    1. Phía Khách hàng (`Cart/ContractDetail.cshtml`): Hiển thị nút "Yêu cầu gia hạn" khi hợp đồng ở trạng thái `1` và cách ngày kết thúc từ 1 đến 3 ngày. Khách chọn số ngày gia hạn mong muốn.
    2. Phía Hệ thống: Kiểm tra lịch trống của các thiết bị trong hợp đồng (`ThietBi`) xem có bị trùng với đơn hàng nào khác đã đặt trước trong tương lai không (Conflict Calendar Check).
    3. Phía Admin (`HopDongController`): Xem xét yêu cầu gia hạn; nếu duyệt, hệ thống cập nhật `NgayKetThuc` mới, tự động sinh thêm kỳ hạn thanh toán bổ sung cho số tiền thuê phát sinh (`Số ngày thuê thêm * Đơn giá/ngày`) và in phụ lục hợp đồng điện tử.

---

### Vấn đề 3: Thiếu quy trình Trả máy trước hạn và Thanh lý hợp đồng sớm (Early Termination)
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 401–405 (Trong `UpdateStatus`, kiểm tra cứng: `if (hopDong.TrangThaiThanhToan != 2) return Error("Không thể hoàn tất hợp đồng khi khách hàng chưa thanh toán đủ công nợ!")`).
- **1. Tên vấn đề:** Hệ thống ép buộc thanh toán 100% giá trị hợp đồng ban đầu, không có cơ chế tính lại tiền thuê thực tế khi khách trả máy trước hạn.
- **2. Mô tả tác động thực tế:**
  Một đoàn làm phim thuê 2 máy quay chuyên dụng trong 30 ngày với tổng chi phí 15.000.000đ chia làm 3 kỳ hạn. Đến ngày thứ 10, dự án quay hoàn thành sớm nên họ mang máy đến trả trước hạn 20 ngày.
  Tuy nhiên, khi Admin bấm nút "Hoàn tất (Thu hồi)" để nhận lại máy về kho, hệ thống từ chối vì `TrangThaiThanhToan != 2` (khách mới đóng kỳ 1 là 5.000.000đ, còn thiếu 10.000.000đ của 2 kỳ sau). Admin bị kẹt vào thế tiến thoái lưỡng nan: nếu ép khách đóng nốt 10 triệu cho 20 ngày không hề sử dụng thì khách sẽ phản ứng dữ dội; còn nếu bấm "Hủy đơn" (`status = 3`) thì toàn bộ doanh thu 10 ngày đã cho thuê bị hủy sạch và báo cáo tài chính bị sai.
- **3. Đề xuất cải thiện cụ thể:**
  - Xây dựng chức năng "Thanh lý hợp đồng trước hạn (Early Termination)":
    1. Cho phép Admin chọn "Trả máy trước hạn" và nhập `NgayTraThucTe`.
    2. Tự động tính lại chi phí:
       $$\text{Tiền thuê thực tế} = \text{Số ngày thực tế sử dụng} \times \text{Đơn giá thuê/ngày} + \text{Phí phạt trả sớm (nếu có)}$$
    3. Hủy bỏ (Status = 3) các kỳ hạn thanh toán trong tương lai chưa phát sinh.
    4. Cấn trừ số tiền đã thu (tiền cọc + tiền kỳ 1) với chi phí thực tế vừa tính toán, hoàn trả tiền thừa cho khách hoặc thu bổ sung phần còn thiếu, rồi đưa máy về kho an toàn.

---

### Vấn đề 4: Thiếu Biên bản Bàn giao thiết bị và Kiểm tra ngoại quan khi xuất/nhập kho (Handover Slip)
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 332–341 (`UpdateStatus` với `status == 1`).
  - `RentalSystem/Models/AppModels.cs`, dòng 47 (`ThietBi.TinhTrangMay`).
  - `RentalSystem/Models/AppModels.cs`, dòng 105–111 (`ChiTietHopDong`).
- **1. Tên vấn đề:** Không có quy trình lập Biên bản bàn giao thiết bị, ghi nhận phụ kiện kèm theo và hình ảnh ngoại quan máy lúc giao / nhận.
- **2. Mô tả tác động thực tế:**
  Khi Admin duyệt giao máy (`status = 1`), thiết bị vật lý trong CSDL lập tức nhảy từ trạng thái `3` (Giữ chỗ) sang `1` (Đang cho thuê). Quá trình này không tạo ra bất kỳ biên bản giao nhận nào. Không ai biết khi xuất kho chiếc laptop có kèm theo sạc zin, chuột không dây, túi chống sốc hay không; vỏ máy có vết trầy xước nào sẵn từ trước không. Đến khi khách đem trả máy, nếu máy bị nứt góc hoặc mất củ sạc, khách nói "lúc tôi nhận máy đã bị nứt rồi và không có chuột", cửa hàng không có bất kỳ bằng chứng văn bản hay hình ảnh nào để đối chất, dẫn đến tranh cãi gay gắt và nguy cơ mất mát phụ kiện.
- **3. Đề xuất cải thiện cụ thể:**
  - Bổ sung bảng `BienBanBanGiao` (hoặc mở rộng `ChiTietHopDong`):
    - Danh sách phụ kiện kèm theo (Adapter sạc, Cáp HDMI, Túi chống sốc, Chuột...).
    - Trường ghi chú tình trạng ngoại quan và tải lên 3–4 ảnh chụp thiết bị ở các góc độ lúc giao máy.
    - Cho phép khách hàng ký xác nhận biên bản giao nhận trực tiếp trên tablet của nhân viên hoặc qua mã OTP SMS/Email trước khi nhận máy rời khỏi cửa hàng.

---

### Vấn đề 5: Cho phép duyệt giao máy khi Hợp đồng chưa có Chữ ký khách hàng hoặc thiếu CCCD
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 332–387 (`UpdateStatus` khi `status == 1`).
- **1. Tên vấn đề:** Lỗ hổng nghiệp vụ cho phép Admin bấm duyệt giao thiết bị ngay cả khi hợp đồng chưa được khách ký tên và chưa tải ảnh CCCD/CMND.
- **2. Mô tả tác động thực tế:**
  Trong mã nguồn `UpdateStatus` khi chuyển trạng thái sang `1` (Đang thuê), hệ thống chỉ thực hiện: kiểm tra số lượng thiết bị, đổi trạng thái thiết bị sang 1, và tự sinh lịch trả góp `KyHanThanhToan`. Toàn bộ đoạn code này **hoàn toàn không có câu lệnh kiểm tra xem `ChuKyKhachHang` và `AnhCMND` có dữ liệu hay không**.
  Nghĩa là: một khách hàng mới chỉ bỏ đồ vào giỏ và bấm checkout, hợp đồng sinh ra ở trạng thái 0; khách chưa hề ký canvas và chưa gửi CMND. Admin chỉ cần vào màn hình `Details.cshtml` và ấn nút "Giao máy & Cho thuê" là máy được xuất kho bình thường! Đây là lỗ hổng kiểm soát nội bộ nghiêm trọng, dẫn đến việc tài sản giá trị hàng chục triệu đồng bị bàn giao ra ngoài mà không có căn cứ pháp lý để ràng buộc người thuê.
- **3. Đề xuất cải thiện cụ thể:**
  - Thêm điều kiện chặn bắt buộc (Validation Guard) trong `HopDongController.UpdateStatus`:
    ```csharp
    if (status == 1)
    {
        if (string.IsNullOrEmpty(hopDong.ChuKyKhachHang) || string.IsNullOrEmpty(hopDong.AnhCMND))
        {
            TempData["Error"] = "CẢNH BÁO BẢO MẬT: Không thể giao máy khi hợp đồng chưa có chữ ký của khách hàng hoặc chưa có ảnh CCCD!";
            return RedirectToAction(nameof(Details), new { id = id });
        }
        if (string.IsNullOrEmpty(hopDong.ChuKyNhanVien))
        {
            TempData["Error"] = "Vui lòng hoàn tất Chữ ký nhân viên đối chiếu trước khi thực hiện bàn giao máy!";
            return RedirectToAction(nameof(Details), new { id = id });
        }
    }
    ```

---

### Vấn đề 6: Chuyển ngược trạng thái phi lý từ "Đang thuê" (1) về "Chờ duyệt" (0)
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 324–328 và dòng 388–398.
  - `RentalSystem/Areas/Admin/Views/HopDong/Details.cshtml`, dòng 387:
    `<button type="button" class="btn btn-outline-warning fw-bold px-4" @(Model.TrangThai == 0 || isDone ? "disabled" : "") onclick="submitStatus(0, '')">Chờ duyệt</button>`
- **1. Tên vấn đề:** Giao diện và Controller cho phép chuyển ngược trạng thái bất hợp lý từ "Đang thuê" (1) về "Chờ duyệt" (0).
- **2. Mô tả tác động thực tế:**
  Khi hợp đồng đang ở trạng thái `1` (máy đã giao cho khách mang về dùng), trên màn hình Admin, nút "Chờ duyệt" vẫn ở trạng thái sáng và bấm được bình thường. Nếu nhân viên bấm nhầm vào nút này, Controller sẽ thực thi khối `else if (status == 0)`: đổi các thiết bị vật lý từ trạng thái `1` (Đang thuê) ngược về trạng thái `3` (Khóa giữ chỗ), và đưa hợp đồng về `0` (Chờ duyệt).
  Tuy nhiên, các kỳ hạn thanh toán (`KyHanThanhToans`) đã được sinh từ trước và máy thì đang nằm ở nhà khách hàng. Trạng thái hệ thống bị xung đột hoàn toàn: một hợp đồng hiển thị "Chờ duyệt" nhưng đã phát sinh công nợ, đã sinh lịch trả góp và máy đã ra khỏi kho từ lâu!
- **3. Đề xuất cải thiện cụ thể:**
  - Trên Razor View `Admin/HopDong/Details.cshtml`: Sửa thuộc tính disabled thành `@(Model.TrangThai != 0 ? "disabled" : "")` để nút "Chờ duyệt" không thể bấm một khi hợp đồng đã rời khỏi trạng thái 0.
  - Trong Controller `HopDongController.UpdateStatus`: Thêm điều kiện chặn triệt để:
    ```csharp
    if (hopDong.TrangThai == 1 && status == 0)
    {
        TempData["Error"] = "Hợp đồng đã bàn giao máy không thể chuyển ngược về trạng thái Chờ duyệt!";
        return RedirectToAction(nameof(Details), new { id = id });
    }
    ```

---

### Vấn đề 7: Cho phép Hủy hợp đồng (Status 3) khi thiết bị đang nằm trong tay khách hàng
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 429–462 (`UpdateStatus` khi `status == 3`).
  - `RentalSystem/Areas/Admin/Views/HopDong/Details.cshtml`, dòng 390.
- **1. Tên vấn đề:** Cho phép Admin bấm nút "Hủy đơn" ngay cả khi hợp đồng đang ở trạng thái "Đang thuê" (`TrangThai == 1`).
- **2. Mô tả tác động thực tế:**
  Tại dòng 429 của `HopDongController`, khi Admin bấm Hủy đơn (`status = 3`), code tự động thực hiện: giải phóng toàn bộ thiết bị về kho (`tb.TrangThai = 0`), và hủy các kỳ hạn thanh toán chưa trả (`k.TrangThai = 3`).
  Hãy tưởng tượng rủi ro thực tế: Khách hàng đang cầm 5 chiếc laptop của cửa hàng về dùng. Admin sơ ý hoặc cố tình bấm "Hủy đơn" trên hệ thống. Ngay lập tức:
  1. Toàn bộ 5 chiếc laptop trên phần mềm được đánh dấu là "Sẵn sàng trong kho" (`TrangThai = 0`), dẫn đến việc khách hàng khác trên website có thể đặt thuê trùng những chiếc máy này.
  2. Toàn bộ các kỳ hạn nợ tiền thuê của khách bị hủy bỏ (`TrangThai = 3`), làm mất dấu vết công nợ đòi tiền của khách! Doanh nghiệp đứng trước nguy cơ mất trắng cả máy lẫn tiền.
- **3. Đề xuất cải thiện cụ thể:**
  - Quy định chặt chẽ luồng trạng thái (State Machine Guard):
    - Chỉ cho phép "Hủy đơn" (`status = 3`) khi hợp đồng ở trạng thái `0` (Chờ duyệt, máy chưa bàn giao ra khỏi kho).
    - Khi hợp đồng đang ở trạng thái `1` (Đang thuê), vô hiệu hóa hoàn toàn nút "Hủy đơn", bắt buộc phải đi qua quy trình "Thu hồi máy & Thanh lý hợp đồng" có kiểm tra serial thiết bị nhập kho.

---

### Vấn đề 8: Hợp đồng không có trạng thái nhận diện "Quá hạn trả máy" (Overdue Return)
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 26–41 (Action `Index`).
  - `RentalSystem/Models/AppModels.cs`, dòng 78 (`HopDong.TrangThai`).
- **1. Tên vấn đề:** Thiếu trạng thái hoặc cảnh báo nhận diện các hợp đồng đã quá ngày kết thúc mà khách chưa trả máy.
- **2. Mô tả tác động thực tế:**
  Hệ thống hiện tại chỉ theo dõi việc trễ hạn đóng tiền của các kỳ hạn trả góp. Đối với bản thân việc thuê thiết bị: Giả sử hợp đồng có ngày kết thúc `NgayKetThuc` là ngày 01/10/2026, nhưng đến ngày 06/10/2026 khách hàng vẫn chưa mang máy tới trả.
  Trên trang danh sách hợp đồng của Admin (`HopDong/Index.cshtml`), hợp đồng này vẫn hiển thị nhãn màu xanh êm đềm: "Đang thuê" (Trạng thái 1). Không có chuông báo, không có badge cảnh báo "Quá hạn trả máy", không có bộ lọc để thủ kho biết hôm nay có những máy nào phải thu hồi. Quản lý kho không phát hiện kịp thời để gọi điện đòi máy, tăng nguy cơ thất thoát thiết bị.
- **3. Đề xuất cải thiện cụ thể:**
  - Bổ sung trạng thái suy diễn (Derived status badge) trên giao diện:
    - Nếu `item.TrangThai == 1 && item.NgayKetThuc.Date < DateTime.Now.Date`: Hiển thị Badge đỏ nổi bật: `<span class="badge bg-danger"><i class="fas fa-clock"></i> Quá hạn trả máy (Trễ @((DateTime.Now.Date - item.NgayKetThuc.Date).Days) ngày)</span>`.
    - Thêm bộ lọc "Hợp đồng quá hạn trả máy" trên thanh công cụ của trang `HopDong/Index`.

---

### Vấn đề 9: Khách hàng bị khóa hoàn toàn, không thể gửi Yêu cầu hủy đơn trước khi nhận máy
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Controllers/CartController.cs`, dòng 664–721 (Action `DeleteContract`).
  - `RentalSystem/Views/Cart/MyContracts.cshtml`, dòng 44–45 và dòng 107–109.
- **1. Tên vấn đề:** Khách hàng bị khóa tính năng hủy đơn ngay sau khi ký hợp đồng hoặc nộp cọc, không có nút gửi yêu cầu hủy đơn trước ngày nhận máy.
- **2. Mô tả tác động thực tế:**
  Trong `CartController.DeleteContract`, hệ thống chỉ cho phép khách hàng tự xóa hợp đồng khi thỏa mãn đồng thời: `chuaKy && hopDong.TrangThai == 0 && hopDong.TienDaCoc == 0`.
  Nghĩa là: Nếu khách vừa ký tên điện tử xong (hoặc đã chuyển khoản đặt cọc trước), toàn bộ các nút thao tác trên màn hình `MyContracts.cshtml` đều biến mất. Nếu khách có việc bận đột xuất và muốn hủy đơn trước ngày nhận máy 3 ngày, khách không có nút bấm nào để thông báo cho cửa hàng. Khách buộc phải gọi hotline hoặc tự ý không đến nhận máy, trong khi cửa hàng vẫn giữ máy trong kho chờ đợi, làm lỡ cơ hội cho khách khác thuê.
- **3. Đề xuất cải thiện cụ thể:**
  - Bổ sung chức năng "Gửi yêu cầu hủy hợp đồng" trong `Cart/ContractDetail.cshtml` và `MyContracts.cshtml` khi hợp đồng ở trạng thái 0 (dù đã ký hay đã nộp cọc).
  - Khi khách bấm yêu cầu hủy và nhập lý do, hệ thống gắn cờ `YeuCauHuy = true` và hiển thị cảnh báo trên Dashboard của Admin để nhân viên xét duyệt chính sách hoàn cọc (ví dụ hoàn 100% nếu báo trước 48h, phạt 30% nếu báo sát giờ) và giải phóng thiết bị kịp thời.

---

### Vấn đề 10: Lệch tiền lẻ và mất độ chính xác khi chia kỳ hạn trả góp (Installment Rounding & Remainder Loss)
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 362–378:
    ```csharp
    decimal tienMoiKy = (hopDong.TongTien - hopDong.TienDaCoc) / soKy;
    ...
    for (int i = 1; i <= soKy; i++) {
        var kyHan = new KyHanThanhToan {
            ...
            SoTienPhai = tienMoiKy
        };
    }
    ```
- **1. Tên vấn đề:** Lệch tiền lẻ và mất độ chính xác số học khi chia đều tiền kỳ hạn trả góp.
- **2. Mô tả tác động thực tế:**
  Giả sử tổng tiền thuê còn lại sau khi trừ cọc là 10.000.000đ, khách hàng chọn chia làm 3 kỳ hạn.
  Phép chia `10.000.000 / 3` ra kết quả số thập phân tuần hoàn: `3.333.333,3333...đ`.
  Do vòng lặp gán `SoTienPhai = tienMoiKy` cho cả 3 kỳ, tổng tiền của 3 kỳ hạn cộng lại chỉ là `9.999.999,99đ` (bị hụt 1 đồng). Trong tiền tệ Việt Nam (VND không có tiền xu hào lẻ), khách hàng không thể nộp số lẻ thập phân. Quan trọng nhất, khi đối soát công nợ cuối cùng, hệ thống kiểm tra `Tổng thu < Tổng tiền hợp đồng` (hụt 1 đồng), khiến trạng thái hợp đồng không thể tự động chuyển sang `TrangThaiThanhToan = 2` (Đã thanh toán đủ).
- **3. Đề xuất cải thiện cụ thể:**
  - Áp dụng thuật toán làm tròn chuẩn tài chính (Rounding & Remainder Allocation):
    1. Làm tròn `tienMoiKy` về bội số 1.000 VNĐ: `decimal tienMoiKy = Math.Round((tongConLai / soKy) / 1000m) * 1000m;`.
    2. Gán `tienMoiKy` cho các kỳ từ 1 đến `soKy - 1`.
    3. Kỳ cuối cùng (`i == soKy`) sẽ chịu phần tiền dư còn lại: `kyCuoi.SoTienPhai = tongConLai - (tienMoiKy * (soKy - 1));`.
    4. Cách xử lý này đảm bảo 100% tổng tiền các kỳ hạn luôn khớp hoàn hảo từng đồng với tổng số tiền nợ.

---

### Vấn đề 11: Mâu thuẫn logic kiểm tra thuê trong cùng một ngày (Same-day Rental Inconsistency)
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Controllers/CartController.cs`, dòng 181 (Checkout POST: `if (NgayKetThuc.Date < NgayBatDau.Date)` -> chấp nhận thuê cùng ngày).
  - `RentalSystem/Controllers/CartController.cs`, dòng 603 (EditContract POST: `if (NgayKetThuc.Date <= NgayBatDau.Date)` -> **chặn cùng ngày**, báo lỗi *"Ngày trả máy phải sau ngày nhận máy!"*).
  - `RentalSystem/Views/Cart/EditContract.cshtml`, dòng 34 (`min="@DateTime.Now.AddDays(1)..."`).
- **1. Tên vấn đề:** Mâu thuẫn logic kiểm tra ngày thuê giữa chức năng Checkout và chức năng EditContract.
- **2. Mô tả tác động thực tế:**
  Nhu cầu thuê thiết bị trong ngày rất phổ biến đối với sinh viên và doanh nghiệp (ví dụ: thuê máy chiếu hoặc máy ảnh từ sáng đến chiều trong ngày 10/10/2026 để làm sự kiện).
  Khách hàng tạo đơn ở màn hình `Checkout` thì hệ thống cho phép tạo thành công (tính giá 1 ngày). Nhưng sau đó, nếu khách bấm vào "Chỉnh sửa đơn hàng" (`EditContract`) để đổi địa chỉ giao hàng, hệ thống lại báo lỗi đỏ chặn không cho lưu vì điều kiện `<=`. Khách hàng bị ức chế vì không hiểu tại sao lúc đặt thì được mà lúc sửa thông tin thì bị báo lỗi ngày không hợp lệ.
- **3. Đề xuất cải thiện cụ thể:**
  - Thống nhất quy tắc nghiệp vụ cho phép thuê trong ngày trên toàn hệ thống:
    Sửa điều kiện trong `CartController.EditContract` thành:
    `if (NgayKetThuc.Date < NgayBatDau.Date)` và tính số ngày: `int days = Math.Max(1, (int)(NgayKetThuc.Date - NgayBatDau.Date).TotalDays)`.

---

### Vấn đề 12: Thời hạn nộp tiền kỳ 1 bị dồn về ngày trả máy thay vì ngày nhận máy
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 365–373:
    ```csharp
    double daysPerKy = totalContractDays / soKy;
    for (int i = 1; i <= soKy; i++) {
        NgayDenHan = hopDong.NgayBatDau.Date.AddDays(Math.Round(i * daysPerKy))
    }
    ```
- **1. Tên vấn đề:** Thuật toán tính ngày đến hạn dồn thời hạn nộp tiền kỳ 1 về cuối chu kỳ thay vì thu tiền trước đầu kỳ.
- **2. Mô tả tác động thực tế:**
  Nếu khách hàng thuê máy trong 30 ngày và chọn thanh toán 1 lần (`soKy = 1`), công thức tính: `daysPerKy = 30 / 1 = 30`. Khi đó `NgayDenHan = NgayBatDau + 30 = NgayKetThuc`!
  Điều này đồng nghĩa với việc khách hàng nhận máy về sử dụng suốt 30 ngày mà không phải trả bất kỳ đồng tiền thuê nào cho đến tận ngày cuối cùng mang máy tới trả! Trong ngành cho thuê tài sản, tiền thuê luôn phải được **thu trước đầu kỳ** (thanh toán ngay khi nhận máy hoặc trả trước chu kỳ). Việc cho khách dùng máy 1 tháng rồi mới thu tiền tiềm ẩn rủi ro cực lớn nếu khách chây ì không trả tiền sau khi đã sử dụng xong.
- **3. Đề xuất cải thiện cụ thể:**
  - Điều chỉnh lịch thu tiền kỳ hạn:
    - Kỳ 1: Hạn thanh toán chính là ngày nhận máy (`NgayBatDau`).
    - Các kỳ tiếp theo (2, 3...): Phân bổ đều theo chu kỳ thuê.
    - Trường hợp `soKy == 1`, hạn thanh toán bắt buộc phải là ngày bắt đầu nhận máy `NgayBatDau`.

---

### Vấn đề 13: Không có cơ chế tự động giải phóng thiết bị khi đơn hàng bị bỏ quên (Reservation Leak)
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Controllers/CartController.cs`, dòng 288 (`device.TrangThai = 3` - Khóa giữ chỗ).
  - `RentalSystem/Models/AppModels.cs`, dòng 48 (`ThietBi.TrangThai`).
- **1. Tên vấn đề:** Thiếu cơ chế tự động hủy và giải phóng thiết bị khi đơn hàng online bị bỏ quên (Reservation Leakage).
- **2. Mô tả tác động thực tế:**
  Khi một khách hàng bấm Checkout trên website, các thiết bị vật lý trong kho lập tức bị khóa sang trạng thái `3` (Giữ chỗ).
  Nếu khách hàng này sau đó đổi ý không muốn thuê nữa, không vào ký hợp đồng, không nộp cọc và tắt trình duyệt, hợp đồng sẽ nằm ở trạng thái `0` vĩnh viễn. Kết quả là những chiếc máy đó bị "giam lỏng" trong CSDL mãi mãi. Khi khách hàng thật khác vào website muốn thuê mẫu máy đó, hệ thống báo "Hết hàng trong kho", dù trên kệ kho thực tế máy vẫn đang nằm yên không có ai dùng.
- **3. Đề xuất cải thiện cụ thể:**
  - Xây dựng cơ chế hết hạn giữ chỗ (Reservation Expiration):
    1. Bổ sung trường `HanChotKy` vào `HopDong` (mặc định cho phép giữ chỗ trong vòng 24 giờ kể từ khi checkout).
    2. Cài đặt một Hosted Service ngầm (`IHostedService`) hoặc Cron Job chạy mỗi giờ: Quét các hợp đồng ở trạng thái 0 chưa ký quá 24h, tự động chuyển hợp đồng sang trạng thái Hủy (`TrangThai = 3`) và mở khóa thiết bị về kho (`ThietBi.TrangThai = 0`).

---

### Vấn đề 14: Form ký hợp đồng chỉ cho phép tải 1 ảnh CCCD (Thiếu mặt sau)
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Models/AppModels.cs`, dòng 82 (`public string AnhCMND { get; set; }`).
  - `RentalSystem/Controllers/CartController.cs`, dòng 397 (`IFormFile cmndFile`).
  - `RentalSystem/Views/Cart/SignContract.cshtml`, dòng 68 (`<input type="file" name="cmndFile" ...>`).
- **1. Tên vấn đề:** Form ký hợp đồng và cấu trúc dữ liệu chỉ hỗ trợ tải lên 1 mặt của thẻ Căn cước công dân.
- **2. Mô tả tác động thực tế:**
  Căn cước công dân gắn chip của Việt Nam bắt buộc phải có 2 mặt: Mặt trước có ảnh chân dung, họ tên, số định danh cá nhân; Mặt sau chứa thông tin ngày cấp, nơi cấp, đặc điểm nhân dạng và chip điện tử.
  Hiện tại hệ thống chỉ có đúng 1 trường dữ liệu và 1 ô chọn file. Khách hàng chỉ có thể tải lên mặt trước hoặc mặt sau. Khi nhân viên Admin vào kiểm tra đối chiếu danh tính khách hàng, họ không xem được ngày cấp và nơi cấp của thẻ, gây khó khăn cho việc xác thực pháp lý và tăng rủi ro sử dụng giấy tờ giả mạo.
- **3. Đề xuất cải thiện cụ thể:**
  - Bổ sung 2 trường `AnhCCCD_Truoc` và `AnhCCCD_Sau` vào Model `HopDong`.
  - Cập nhật giao diện `SignContract.cshtml` hiển thị 2 ô tải ảnh trực quan: "Ảnh mặt trước CCCD" và "Ảnh mặt sau CCCD" kèm tính năng xem trước ảnh (image preview).

---

### Vấn đề 15: Khách hàng không nhìn thấy Chữ ký số của bên Cho thuê (ABC Rental)
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Views/Cart/ContractDetail.cshtml`, dòng 314–344 (Chỉ hiển thị `Model.ChuKyKhachHang`).
  - `RentalSystem/Areas/Admin/Views/HopDong/Details.cshtml`, dòng 154–163 (Hiển thị cả `ChuKyKhachHang` và `ChuKyNhanVien`).
- **1. Tên vấn đề:** Giao diện chi tiết hợp đồng của khách hàng không hiển thị chữ ký số của đại diện công ty cho thuê.
- **2. Mô tả tác động thực tế:**
  Trên màn hình chi tiết hợp đồng của khách hàng (`ContractDetail.cshtml`), khách chỉ nhìn thấy ảnh chữ ký của chính mình. Khách không hề biết phía công ty đã ký duyệt hợp đồng hay chưa, nhân viên nào chịu trách nhiệm đại diện ký kết. Điều này tạo cảm giác hợp đồng mang tính đơn phương, thiếu tính pháp lý hai chiều và làm giảm độ tin cậy của dịch vụ trong mắt khách hàng.
- **3. Đề xuất cải thiện cụ thể:**
  - Tại `ContractDetail.cshtml`, bổ sung khung hiển thị chữ ký của đại diện bên cho thuê:
    Nếu `Model.ChuKyNhanVien` đã có thì hiển thị ảnh chữ ký và họ tên của nhân viên duyệt; nếu chưa có thì hiển thị badge màu vàng "Đang chờ đại diện công ty ký đối chiếu".

---

### Vấn đề 16: Khách hàng không có tính năng Gửi biên lai xác nhận đã chuyển khoản
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Views/Cart/ContractDetail.cshtml`, dòng 217–260 (Khối Hướng dẫn chuyển khoản VietQR).
  - `RentalSystem/Areas/Admin/Views/HopDong/Details.cshtml`, dòng 263–305 (Form `ConfirmPayment`).
- **1. Tên vấn đề:** Khách hàng không có nút hay form để gửi mã giao dịch và tải ảnh biên lai chuyển khoản ngân hàng.
- **2. Mô tả tác động thực tế:**
  Giao diện khách hàng có hiển thị mã VietQR rất tiện lợi. Tuy nhiên, sau khi khách mở app ngân hàng quét mã và chuyển tiền thành công, khách **hoàn toàn không có chỗ nào để bấm "Tôi đã chuyển khoản"** hay đính kèm ảnh chụp màn hình giao dịch. Khách hàng rơi vào tâm trạng bất an: tiền tài khoản đã bị trừ mà trạng thái trên web vẫn báo "Chưa trả". Khách buộc phải gọi điện thoại hoặc nhắn tin Zalo giục nhân viên kiểm tra tài khoản, làm mất đi tính tự động của hệ thống.
- **3. Đề xuất cải thiện cụ thể:**
  - Bổ sung nút "Xác nhận đã chuyển khoản" kèm modal cho phép khách: Nhập mã giao dịch ngân hàng (Mã FT/Trace) và tải ảnh biên lai chuyển tiền.
  - Sau khi khách gửi, kỳ hạn chuyển sang trạng thái "Chờ kế toán duyệt đối soát", đồng thời hiển thị thông báo nổi bật trên trang Admin để kế toán viên kiểm tra và duyệt nhanh chỉ với 1 click.

---

# PHẦN 2: PHÂN HỆ THANH TOÁN (PAYMENT DOMAIN)

Phân hệ Thanh toán đảm bảo an toàn dòng tiền, hạch toán phiếu thu, kiểm soát trả góp và tích hợp cổng thanh toán. Dưới đây là 15 vấn đề nghiệp vụ được phát hiện trong phân hệ này.

---

### Vấn đề 1: Cổng thanh toán trực tuyến VNPay bị "bỏ rơi" trong cấu hình mà không được triển khai
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/appsettings.json`, dòng 12–21 (Cấu hình `Vnpay` với đầy đủ `TmnCode`, `HashSecret`, `BaseUrl`, `ReturnUrl`).
  - Toàn bộ codebase không có `PaymentController.cs` hay `VnPayService.cs`.
  - `RentalSystem/Controllers/CartController.cs` (Hoàn toàn không có logic tích hợp thanh toán online).
- **1. Tên vấn đề:** Cổng thanh toán trực tuyến VNPay đã được cấu hình trong `appsettings.json` nhưng bị bỏ rơi, không hề có Controller hay Service xử lý.
- **2. Mô tả tác động thực tế:**
  File cấu hình dự án khai báo thông số VNPay Sandbox rất đầy đủ và chuyên nghiệp. Tuy nhiên, toàn bộ website hiện tại hoạt động như một hệ thống đặt chỗ thủ công. Khách hàng muốn trả tiền cọc hoặc thanh toán tiền thuê online không thể thực hiện qua cổng thanh toán tự động, làm mất đi tính hiện đại của một đồ án tốt nghiệp web ASP.NET Core.
- **3. Đề xuất cải thiện cụ thể:**
  - Xây dựng `VnPayService` và `PaymentController`:
    1. Action `CreatePaymentUrl`: Tạo URL thanh toán VNPay có mã hóa chữ ký HMAC-SHA512.
    2. Action `PaymentCallback`: Tiếp nhận kết quả thanh toán từ VNPay, kiểm tra tính toàn vẹn của chữ ký số (`vnp_SecureHash`).
    3. Action `VnPayIPN`: Xử lý Webhook ngầm từ server VNPay, tự động tạo bản ghi `PhieuThu`, cập nhật `SoTienDaTra` cho `KyHanThanhToan` và đổi trạng thái hợp đồng.

---

### Vấn đề 2: Khách hàng không có chỗ gửi bằng chứng chuyển khoản và mã giao dịch ngân hàng
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Views/Cart/ContractDetail.cshtml`, dòng 217–260.
  - `RentalSystem/Controllers/CartController.cs` (Không có action xử lý tải lên biên lai ngân hàng).
- **1. Tên vấn đề:** Thiếu chức năng tải lên ảnh biên lai chuyển khoản (Bill Upload) và gửi mã giao dịch ngân hàng.
- **2. Mô tả tác động thực tế:**
  Khi khách quét mã VietQR và chuyển tiền qua Internet Banking, hệ thống không có kênh tiếp nhận chứng từ điện tử. Kế toán Admin không có danh sách giao dịch khách báo đã chuyển để tra soát sao kê, dẫn đến việc kích hoạt đơn hàng bị chậm trễ nhiều giờ nếu nhân viên bận hoặc quên kiểm tra app ngân hàng.
- **3. Đề xuất cải thiện cụ thể:**
  - Bổ sung action `[HttpPost] XacNhanChuyenKhoan(int maKyHan, string maGiaoDich, IFormFile hinhAnhBienLai)` trong `CartController`.
  - Lưu thông tin vào bảng tạm hoặc mở rộng bảng `PhieuThu` với trạng thái `TrangThaiXacNhan = 0` (Chờ đối soát), cho phép Admin đối chiếu hình ảnh bill và bấm duyệt 1 chạm.

---

### Vấn đề 3: Thiếu hoàn toàn quy trình Hoàn trả tiền cọc & Nghiệp vụ Phiếu Chi (Deposit Refund & Payment Voucher)
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Models/AppModels.cs`, dòng 112–122 (Chỉ có model `PhieuThu`, hoàn toàn không có `PhieuChi`).
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 399–463 (Action `UpdateStatus`).
- **1. Tên vấn đề:** Hệ thống chỉ có nghiệp vụ thu tiền vào (`PhieuThu`), thiếu hoàn toàn nghiệp vụ chi tiền ra (`PhieuChi`) để hoàn trả tiền cọc cho khách.
- **2. Mô tả tác động thực tế:**
  Khi hợp đồng kết thúc tốt đẹp hoặc bị hủy, tiền cọc của khách hàng sau khi trả lại ngoài đời thực không có bất kỳ chứng từ nào lưu vết trên phần mềm. Dòng tiền chi ra (Cash Outflow) bị biến mất khỏi sổ sách kế toán, khiến báo cáo tài chính không thể trả lời được câu hỏi: Trong tháng công ty đã hoàn trả bao nhiêu tiền cọc cho khách hàng?
- **3. Đề xuất cải thiện cụ thể:**
  - Bổ sung model `PhieuChi` vào `AppModels.cs` (gồm: `MaPhieuChi`, `MaHopDong`, `LoaiChi`, `SoTien`, `NgayChi`, `HinhThucChi`, `MaNhanVienChi`, `GhiChu`).
  - Thêm chức năng "Lập phiếu hoàn trả cọc" trong `Admin/HopDong/Details.cshtml` tự động tính cấn trừ công nợ và ghi nhận dòng tiền xuất quỹ minh bạch.

---

### Vấn đề 4: Thiếu cơ chế Tái cấu trúc, Gộp hoặc Tất toán sớm các kỳ hạn (Installment Rescheduling & Early Settlement)
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 346–386.
  - `RentalSystem/Areas/Admin/Views/HopDong/Details.cshtml`, dòng 263–305.
- **1. Tên vấn đề:** Các kỳ hạn trả góp sau khi sinh bị cố định cứng, không thể gộp kỳ hạn để tất toán sớm hoặc điều chỉnh dời hạn nộp tiền.
- **2. Mô tả tác động thực tế:**
  Nếu khách muốn thanh toán toàn bộ số nợ còn lại trong một lần để kết thúc hợp đồng sớm, Admin phải mở từng kỳ một và bấm xác nhận thu tiền lặp đi lặp lại rất thủ công. Ngược lại, khi khách gặp sự cố tài chính xin lùi ngày thanh toán thêm vài ngày, Admin không thể sửa `NgayDenHan` trên phần mềm, khiến hệ thống tự động gán nhãn "Trễ hạn" đỏ lòm, gây áp lực tâm lý không đáng có cho khách hàng trung thực.
- **3. Đề xuất cải thiện cụ thể:**
  - Bổ sung nút "Tất toán toàn bộ nợ còn lại" trên `Details.cshtml`: Tự động gộp toàn bộ số dư nợ của các kỳ chưa trả vào 1 phiếu thu duy nhất và gạch nợ hàng loạt.
  - Cho phép Admin có quyền điều chỉnh ngày đến hạn của kỳ hạn kèm ô nhập lý do phê duyệt để lưu vết kiểm toán nội bộ.

---

### Vấn đề 5: Thiếu tính năng In Biên lai / Phiếu thu tiền điện tử cho khách hàng (Receipt Generation / Export)
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Controllers/DocumentController.cs`, dòng 26–58 (Chỉ có duy nhất action `InHopDong`).
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 573, 643, 676 (Các action `ConfirmPayment`, `ThemTienCoc`, `ThuPhiBaoTri` không hỗ trợ in biên lai).
- **1. Tên vấn đề:** Hệ thống không có chức năng xuất hoặc in Biên lai / Phiếu thu tiền khi khách nộp tiền thuê, tiền cọc hoặc phí bảo trì.
- **2. Mô tả tác động thực tế:**
  Khách hàng nộp tiền mặt tại quầy hoặc chuyển khoản không nhận được bất kỳ chứng từ thanh toán hợp pháp nào có chữ ký người thu tiền. Đối với khách hàng là cơ quan, doanh nghiệp thuê thiết bị, kế toán của họ bắt buộc phải có Phiếu thu có mộc để làm thủ tục thanh quyết toán tạm ứng. Việc thiếu phiếu thu khiến doanh nghiệp khó chấp nhận dịch vụ của cửa hàng.
- **3. Đề xuất cải thiện cụ thể:**
  - Bổ sung action `InPhieuThu(int id)` trong `DocumentController.cs` và view `Views/Document/InPhieuThu.cshtml`.
  - Thiết kế mẫu in biên lai chuẩn khổ A5/K80 hiển thị đầy đủ: Số phiếu thu, Ngày thu, Người nộp, Số hợp đồng, Số tiền (bằng số & bằng chữ), Người lập phiếu và chữ ký hai bên.
  - Bổ sung biểu tượng máy in `🖨️ In biên lai` cạnh mỗi dòng giao dịch trên cả giao diện Admin và Khách hàng.

---

### Vấn đề 6: Mâu thuẫn trạng thái thanh toán giữa `HopDong.TrangThaiThanhToan` và dữ liệu thực tế
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Models/AppModels.cs`, dòng 86 (`TrangThaiThanhToan`: 0 - Chưa thanh toán, 1 - Còn nợ, 2 - Đã thanh toán đủ).
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 230 (Khi tạo đơn tại quầy, dù đã thu cọc thì `TrangThaiThanhToan` vẫn bị gán cứng bằng 0).
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 624–631 (`ConfirmPayment` set `TrangThaiThanhToan = 2` dù đang còn nợ phí bồi thường hư hại máy `PhiDenBu`).
- **1. Tên vấn đề:** Mâu thuẫn và sai lệch trong việc cập nhật trạng thái thanh toán tổng thể của Hợp đồng.
- **2. Mô tả tác động thực tế:**
  Khách hàng vừa nộp cọc 10 triệu đồng tại quầy, mở màn hình xem hợp đồng vẫn thấy hiển thị huy hiệu: "Chưa thanh toán" (gây hoang mang). Ngược lại, khách hàng còn nợ 5 triệu tiền đền bù sửa máy hỏng, nhưng vì các kỳ hạn thuê đã trả đủ nên hệ thống vội vã đánh dấu "Đã thanh toán đủ", khiến nhân viên lơ là không đôn đốc thu nợ, gây thất thoát tài sản.
- **3. Đề xuất cải thiện cụ thể:**
  - Chuẩn hóa máy trạng thái thanh toán 4 cấp rõ ràng:
    - `0 - Chưa thanh toán`: Chưa nộp bất kỳ khoản nào.
    - `1 - Đã đặt cọc`: Đã nộp tiền cọc, chưa thanh toán kỳ thuê.
    - `2 - Còn nợ`: Đang trả dở dang các kỳ hạn hoặc còn nợ phí đền bù.
    - `3 - Đã tất toán đủ`: Toàn bộ tiền thuê, tiền cọc và toàn bộ phí bồi thường bảo trì đều đã thu đủ 100%.

---

### Vấn đề 7: Nguy cơ Race Condition / Double-Click gây thu tiền trùng lặp tại `ConfirmPayment`
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 573–638 (Action `ConfirmPayment`).
- **1. Tên vấn đề:** Nguy cơ Race Condition / Double-click gây ghi nhận trùng lặp số tiền và sinh nhiều phiếu thu ảo khi xác nhận thanh toán.
- **2. Mô tả tác động thực tế:**
  Khối xử lý `ConfirmPayment` không sử dụng Database Transaction ở mức cô lập cao, không có Concurrency Token (`RowVersion`) và không có Semaphore khóa tiến trình. Nếu thu ngân vô tình nhấp đúp (Double-click) nhanh vào nút "Xác nhận thu", hoặc hai nhân viên cùng mở một hợp đồng trên hai máy tính và cùng bấm xác nhận thu tiền cho cùng một kỳ hạn: cả hai request chạy song song đều cộng dồn `soTienThucThu` vào `SoTienDaTra` và sinh ra 2 bản ghi `PhieuThu` trùng lặp trong CSDL. Kết quả là số tiền thu bị đội lên gấp đôi thực tế, làm sai lệch sổ quỹ kế toán.
- **3. Đề xuất cải thiện cụ thể:**
  - Bọc logic cập nhật trong Database Transaction: `using var transaction = await _context.Database.BeginTransactionAsync(IsolationLevel.Serializable)`.
  - Phía Frontend: Ngay sau khi bấm submit, lập tức disable nút bằng JavaScript và hiển thị trạng thái `Đang xử lý...`.
  - Bổ sung cơ chế Idempotency Token để ngăn chặn các yêu cầu thanh toán trùng lặp cho cùng một kỳ hạn trong khoảng thời gian dưới 5 giây.

---

### Vấn đề 8: Thiếu trường lưu trữ thông tin kiểm chứng giao dịch chuyển khoản ngân hàng
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Views/HopDong/Details.cshtml`, dòng 292–295.
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 573.
  - `RentalSystem/Models/AppModels.cs`, dòng 112–122 (Model `PhieuThu`).
- **1. Tên vấn đề:** Phiếu thu thiếu các trường dữ liệu ngân hàng chuyên biệt để đối soát sao kê.
- **2. Mô tả tác động thực tế:**
  Khi thu ngân chọn hình thức "Chuyển khoản", form chỉ có 1 ô nhập văn bản tự do là `GhiChu`. Bảng `PhieuThu` không có trường lưu Mã giao dịch ngân hàng (`MaGiaoDichNganHang`) và Tên ngân hàng nhận. Khi đối soát sao kê ngân hàng vào cuối tháng, kế toán không thể biết khoản tiền 5.000.000đ trên web tương ứng với dòng tiền nào trên sao kê MB Bank / Vietcombank. Đồng thời tiềm ẩn nguy cơ gian lận nội bộ: thu ngân thu tiền mặt của khách nhưng ghi hình thức là "Chuyển khoản" để chiếm dụng tiền mặt.
- **3. Đề xuất cải thiện cụ thể:**
  - Mở rộng model `PhieuThu`: Thêm trường `MaGiaoDichNganHang` và `NganHangNhan`.
  - Trên giao diện thu tiền: Nếu chọn hình thức Chuyển khoản, JavaScript bắt buộc hiển thị và yêu cầu nhập mã chuẩn chi / mã tham chiếu ngân hàng.

---

### Vấn đề 9: Tiền trả thừa (Overpayment) bị "mắc kẹt" trong chuỗi ghi chú, không tự động cấn trừ kỳ tiếp theo
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 593–597:
    ```csharp
    if (kyHan.SoTienDaTra >= kyHan.SoTienPhai) {
        kyHan.TrangThai = 1;
        if (kyHan.SoTienDaTra > kyHan.SoTienPhai) {
            var traThua = kyHan.SoTienDaTra - kyHan.SoTienPhai;
            ghiChuKyHan = $" (Trả thừa {traThua:N0}đ)";
        }
    }
    ```
- **1. Tên vấn đề:** Tiền khách đóng thừa ở kỳ hiện tại chỉ được ghi thành chữ trong cột Ghi chú, không tự động cấn trừ sang kỳ tiếp theo.
- **2. Mô tả tác động thực tế:**
  Mỗi kỳ khách phải đóng 2.000.000đ. Kỳ 1 khách chuyển khoản luôn 3.000.000đ (đóng dư 1.000.000đ để đỡ tiền kỳ 2). Hệ thống ghi nhận Kỳ 1 nhận đủ và nối thêm chữ `(Trả thừa 1.000.000đ)`. Tuy nhiên, sang Kỳ 2, hệ thống vẫn báo nợ nguyên vẹn 2.000.000đ và `SoTienDaTra = 0`. Đến ngày đến hạn của Kỳ 2, hệ thống tự động nhảy sang tab "Đang trễ hạn", nhân viên kinh doanh vẫn tiếp tục gọi điện giục khách trả nợ, gây ức chế tột cùng cho khách hàng.
- **3. Đề xuất cải thiện cụ thể:**
  - Áp dụng thuật toán thác nước (Waterfall Payment Carryover):
    Khi số tiền thực thu lớn hơn số tiền còn thiếu của kỳ hiện tại, hệ thống gạch nợ đủ cho kỳ hiện tại, lấy số tiền dư kết chuyển ngay sang kỳ tiếp theo chưa thanh toán (`kyKeTiep.SoTienDaTra += tienDu`), đảm bảo số tiền của khách luôn được hạch toán chính xác.

---

### Vấn đề 10: Kỳ hạn đã đánh dấu "Đã trả" (`TrangThai == 1`) bị khóa cứng, không thể điều chỉnh hay thu bổ sung
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 584 (`if (kyHan.TrangThai != 1)`).
  - `RentalSystem/Areas/Admin/Views/HopDong/Details.cshtml`, dòng 264 (`@if (k.TrangThai != 1 ...)`).
- **1. Tên vấn đề:** Kỳ hạn thanh toán sau khi chuyển sang trạng thái "Đã trả" bị khóa cứng vĩnh viễn, không có cơ chế điều chỉnh sai sót.
- **2. Mô tả tác động thực tế:**
  Nếu thu ngân gõ nhầm số tiền (ví dụ khách đóng 1.500.000đ nhưng gõ nhầm thành 15.000.000đ) hoặc chọn nhầm kỳ hạn, sau khi bấm lưu thì nút "Thu tiền" biến mất hoàn toàn và controller từ chối xử lý. Thu ngân không thể hủy giao dịch sai (Void Transaction), không thể sửa lại số tiền. Muốn sửa, chỉ có cách nhờ kỹ thuật viên vào can thiệp trực tiếp CSDL, vi phạm quy trình vận hành chuẩn.
- **3. Đề xuất cải thiện cụ thể:**
  - Bổ sung quyền cho Kế toán trưởng: "Hủy phiếu thu / Điều chỉnh kỳ hạn".
  - Khi hủy phiếu thu sai, hệ thống ghi nhận lý do hủy, trừ ngược lại số tiền đã ghi nhận sai và trả trạng thái kỳ hạn về `0` (Chưa trả) một cách an toàn và minh bạch.

---

### Vấn đề 11: Trạng thái trễ hạn (`TrangThai == 2`) chưa từng được kích hoạt tự động, thiếu chính sách phí phạt trễ hạn
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Models/AppModels.cs`, dòng 100 (`// 0: Chưa trả, 1: Đã trả, 2: Trễ hạn`).
  - Toàn bộ codebase không có dòng lệnh nào gán `k.TrangThai = 2`.
- **1. Tên vấn đề:** Giá trị trạng thái `2` (Trễ hạn) là "mã chết" trong CSDL và thiếu chính sách phạt trễ hạn.
- **2. Mô tả tác động thực tế:**
  Trạng thái của các kỳ hạn trễ trong CSDL luôn chỉ là `0` (Chưa trả). Nếu kế toán chạy câu truy vấn SQL trực tiếp để tìm các kỳ trễ hạn thì kết quả trả về luôn là rỗng. Ngoài ra, khách đóng trễ 1 ngày hay trễ 1 tháng cũng không bị tính thêm một đồng phí phạt nào. Việc thiếu chế tài xử phạt khiến khách hàng chậm trễ thanh toán, làm giảm hiệu quả quay vòng vốn của cửa hàng.
- **3. Đề xuất cải thiện cụ thể:**
  - Xây dựng Scheduled Background Service chạy định kỳ mỗi đêm: Tự động cập nhật `k.TrangThai = 2` cho các kỳ hạn có `NgayDenHan < DateTime.Now` và `TrangThai == 0`.
  - Thiết lập chính sách phí phạt quá hạn: Cho phép ân hạn 3 ngày; nếu quá 3 ngày tính phạt 0.1%/ngày dựa trên số tiền chậm nộp.

---

### Vấn đề 12: Nghiệp vụ Trả thiếu (Underpayment) để kỳ hạn treo lơ lửng không có hạn định mới
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 601 (Khi trả thiếu, hệ thống giữ nguyên `kyHan.TrangThai = 0`).
- **1. Tên vấn đề:** Khi khách trả thiếu tiền, kỳ hạn vẫn bị gắn với ngày đến hạn cũ mà không có trường lưu hạn hẹn trả tiếp theo.
- **2. Mô tả tác động thực tế:**
  Một khách hàng có thiện chí thanh toán trước 80% tiền thuê và xin vài ngày sau nộp nốt 20%. Ngay khi qua ngày đến hạn cũ, toàn bộ kỳ hạn đó bị đánh đồng là "Quá hạn" đỏ rực. Kế toán không có chỗ ghi nhận ngày hẹn nộp số tiền còn lại, dẫn đến việc theo dõi và nhắc nợ bị rập khuôn, thiếu linh hoạt.
- **3. Đề xuất cải thiện cụ thể:**
  - Bổ sung trường `NgayHenTraTiepTheo` và `GhiChuTraThieu` vào `KyHanThanhToan`.
  - Khi thu thiếu tiền, cho phép thu ngân chọn ngày hẹn nộp tiếp. Nếu trong thời gian hẹn, giao diện hiển thị badge màu vàng: "Đang chờ nộp tiếp đợt 2" thay vì gắn mác quá hạn gay gắt.

---

### Vấn đề 13: Mã VietQR chuyển khoản ngân hàng bị cố định số tiền bằng 0 (`amount=0`) và cấu hình cứng trong View
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Views/Cart/ContractDetail.cshtml`, dòng 226–248:
    `<img src="https://img.vietqr.io/image/MB-0987654321-compact2.png?amount=0&addInfo=HD@(Model.MaHopDong)...">`
- **1. Tên vấn đề:** Mã VietQR bị gán cứng số tiền bằng 0đ (`amount=0`) và thông tin ngân hàng bị hardcoded trực tiếp trong file HTML Razor View.
- **2. Mô tả tác động thực tế:**
  Khi khách mở app ngân hàng quét mã QR, ô số tiền bị trống trơn. Khách phải tự nhớ hoặc tự tính số tiền cần đóng rồi gõ tay vào. Rủi ro sai sót cực lớn: khách gõ thiếu số 0 (ví dụ nộp 300.000đ thay vì 3.000.000đ), gây mất công sức đối chiếu và thu bổ sung. Ngoài ra, nếu cửa hàng đổi số tài khoản ngân hàng, lập trình viên phải sửa tay trong view và build lại code, Admin không thể cấu hình trong trang quản trị.
- **3. Đề xuất cải thiện cụ thể:**
  - Đưa cấu hình tài khoản thụ hưởng vào `appsettings.json` hoặc bảng cấu hình hệ thống.
  - Tự động tính số tiền cần nộp của kỳ hạn gần nhất chưa trả: `var soTienCanNop = kyHan.SoTienPhai - kyHan.SoTienDaTra;` và gắn trực tiếp vào URL VietQR: `amount=@soTienCanNop`. Khi khách quét mã, số tiền được điền sẵn chính xác 100%.

---

### Vấn đề 14: Thiếu thông tin Người lập phiếu (Thu ngân) trên Phiếu thu gây mờ ám trách nhiệm
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Models/AppModels.cs`, dòng 112–122 (Model `PhieuThu` hoàn toàn không có trường `MaNhanVien`).
  - `RentalSystem/Views/Cart/ContractDetail.cshtml`, dòng 270 và `Admin/HopDong/Details.cshtml`, dòng 337.
- **1. Tên vấn đề:** Phiếu thu không lưu trữ thông tin nhân viên thu tiền, gây mờ ám trách nhiệm nội bộ.
- **2. Mô tả tác động thực tế:**
  Khách nộp tiền mặt tại cửa hàng nhưng phiếu thu trên web không hiện ai đã nhận tiền. Nếu xảy ra thất thoát tiền mặt trong ca làm việc hoặc có khiếu nại về số tiền đã nộp, ban quản lý không có căn cứ tra soát nhân viên nào đã lập phiếu thu đó.
- **3. Đề xuất cải thiện cụ thể:**
  - Thêm trường `MaNhanVienThu` (khóa ngoại liên kết `NguoiDung`) vào bảng `PhieuThu`.
  - Tự động lấy ID của nhân viên đang đăng nhập từ `User.FindFirst(ClaimTypes.NameIdentifier)` để gán vào phiếu thu khi bấm xác nhận thanh toán. Hiển thị cột "Người lập phiếu" trên bảng lịch sử giao dịch.

---

### Vấn đề 15: Sai lệch nghiêm trọng trong Báo cáo Doanh thu & Danh sách Quản lý Công nợ
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/ThongKeController.cs`, dòng 25:
    `var tongDoanhThu = hopDongs.Where(h => h.TrangThai == 2).Sum(h => h.TongTien);`
  - `RentalSystem/Areas/Admin/Controllers/CongNoController.cs`, dòng 30:
    `Where(h => h.TrangThaiThanhToan != 2 && h.TrangThai != 3)`
- **1. Tên vấn đề:** Báo cáo doanh thu chỉ tính đơn hoàn tất, và danh sách quản lý công nợ bỏ lọt hoàn toàn các khoản nợ phí bảo trì.
- **2. Mô tả tác động thực tế:**
  1. Trong `ThongKeController`: Doanh thu chỉ được cộng khi hợp đồng đã hoàn tất (`TrangThai == 2`). Những hợp đồng đang cho thuê (`TrangThai == 1`) đã thu được nhiều kỳ với số tiền hàng chục triệu đồng đều bị coi là doanh thu bằng 0đ! Báo cáo gửi cấp trên không phản ánh đúng dòng tiền thực thu trong tháng.
  2. Trong `CongNoController`: Nếu khách đã đóng đủ tiền thuê (`TrangThaiThanhToan == 2`) nhưng còn nợ phí đền bù bảo trì máy hỏng (`PhiDenBu`), hợp đồng đó biến mất hoàn toàn khỏi danh sách Công nợ! Kế toán bị "bỏ quên" khoản nợ này, dẫn đến nguy cơ thất thoát vốn.
- **3. Đề xuất cải thiện cụ thể:**
  - Trong `ThongKeController`: Doanh thu thực tế phải tính bằng tổng tiền của tất cả các `PhieuThu` đã thu thành công (`LoaiPhieu == 0` và `LoaiPhieu == 2`).
  - Trong `CongNoController`: Bổ sung điều kiện kiểm tra công nợ toàn diện: `TongPhaiThu = HopDong.TongTien + TongPhiDenBu` và kiểm tra `TongPhaiThu > TongDaThu`.

---

# PHẦN 3: PHÂN HỆ BẢO TRÌ (MAINTENANCE DOMAIN)

Phân hệ Bảo trì phụ trách giải quyết sự cố kỹ thuật, sửa chữa thiết bị trong thời gian thuê và xác định chi phí bồi thường hư hỏng máy giữa Cửa hàng và Khách thuê. Dưới đây là 15 vấn đề nghiệp vụ được phát hiện trong phân hệ này.

---

### Vấn đề 1: Khách hàng không có bước xác nhận nghiệm thu kết quả sửa chữa và chỉ được đánh giá sao cụt ngủn
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/BaoTriController.cs`, dòng 58–103 (Action `UpdateStatus`).
  - `RentalSystem/Controllers/BaoTriController.cs`, dòng 144–176 (Action `DanhGia`).
  - `RentalSystem/Views/BaoTri/MyTickets.cshtml`, dòng 44–65.
- **1. Tên vấn đề:** Khách hàng không có quy trình nghiệm thu kết quả sửa chữa và chỉ có thể đánh giá sao số mà không có ô nhập nhận xét phản hồi.
- **2. Mô tả tác động thực tế:**
  Khi kỹ thuật viên sửa xong máy, họ chỉ cần chọn trạng thái `3` (Hoàn thành) trong trang Admin là phiếu lập tức đóng lại. Khách hàng chưa hề nhận lại máy, chưa kiểm tra xem lỗi đã hết chưa (ví dụ: máy tính đã hết sập nguồn chưa, màn hình còn sọc không) thì hệ thống đã coi như xong. Khách chỉ có thể chọn từ 1 đến 5 sao trong một thẻ `<select>` nhỏ, hoàn toàn không có ô nhập nhận xét bằng chữ. Nếu máy sửa chưa đạt, khách không có cách nào từ chối nghiệm thu hay yêu cầu xử lý lại trên hệ thống.
- **3. Đề xuất cải thiện cụ thể:**
  - Tách trạng thái hoàn thành thành 2 bước: `3 - Đã sửa xong (Chờ khách nghiệm thu)` và `4 - Khách đã nghiệm thu (Đóng phiếu)`.
  - Trên `MyTickets.cshtml`, hiển thị nút "Xác nhận nhận máy & Nghiệm thu" hoặc "Chưa khắc phục được (Yêu cầu xử lý lại)".
  - Mở rộng action `DanhGia` nhận thêm chuỗi `string yKienPhanHoi` và lưu vào bảng `PhieuBaoTri`.

---

### Vấn đề 2: Admin/KTV đơn phương áp đặt phí đền bù hư hỏng mà không có quy trình gửi báo giá cho khách duyệt trước
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/BaoTriController.cs`, dòng 58–103.
  - `RentalSystem/Areas/Admin/Views/BaoTri/Details.cshtml`, dòng 51–53 (`<input type="number" name="phiDenBu" value="@Model.PhiDenBu" />`).
- **1. Tên vấn đề:** Admin/Kỹ thuật viên đơn phương áp đặt phí bồi thường hư hỏng mà không có quy trình gửi bảng báo giá chi tiết cho khách duyệt trước khi sửa.
- **2. Mô tả tác động thực tế:**
  Khi máy bị rơi vỡ màn hình, KTV nhập con số bất kỳ vào ô `phiDenBu` (ví dụ 4.000.000đ) và bấm Lưu. Hệ thống lập tức ghi khoản nợ này vào hợp đồng của khách. Khách hàng hoàn toàn không được xem bảng kê chi phí linh kiện (Màn hình bao nhiêu, công thợ bao nhiêu) và không có quyền chấp thuận hay khiếu nại. Việc bị áp đặt chi phí đơn phương gây bức xúc cho khách và dễ dẫn đến tình trạng khách bỏ cọc, tranh chấp khiếu kiện.
- **3. Đề xuất cải thiện cụ thể:**
  - Xây dựng quy trình 3 bước chuẩn: `KTV lập bảng kê chi phí linh kiện` -> `Gửi báo giá cho khách duyệt trên web` -> `Khách bấm Đồng ý báo giá` -> `KTV mới tiến hành thay thế sửa chữa`.
  - Thêm trường `TrangThaiBaoGia` (0: Chưa báo, 1: Chờ khách duyệt, 2: Đã duyệt, 3: Từ chối báo giá) vào model `PhieuBaoTri`.

---

### Vấn đề 3: Hợp đồng cam kết cấp máy Backup nhưng phần mềm không có chức năng hoán đổi máy hoặc tạm dừng tính tiền thuê
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Views/Document/InHopDong.cshtml`, dòng 139 (Điều 4.2: *"Có trách nhiệm sửa chữa, bảo trì hoặc thay thế thiết bị khác (máy Backup) cho Bên A nếu thiết bị gặp sự cố kỹ thuật..."*).
  - Cả 2 controller `BaoTriController` (Admin và Client) không có tính năng đổi máy.
- **1. Tên vấn đề:** Cam kết cấp thiết bị thay thế (Swap Device) trong hợp đồng không được hỗ trợ trong phần mềm, và không có tính năng tạm dừng tính tiền thuê khi máy bị hỏng.
- **2. Mô tả tác động thực tế:**
  Hợp đồng cam kết cấp máy Backup nếu thiết bị gặp sự cố. Tuy nhiên trên phần mềm, khi máy bị hỏng, máy hỏng vẫn nằm trong hợp đồng của khách, không có nút nào để nhân viên đổi sang một máy dự phòng khác trong kho. Đồng thời, đồng hồ tính tiền thuê vẫn chạy đều theo ngày: Khách thuê 10 ngày, máy hỏng nằm ở tiệm sửa mất 5 ngày không dùng được, nhưng cuối hợp đồng vẫn phải trả đủ 100% tiền thuê của 10 ngày! Điều này vi phạm nghiêm trọng cam kết dịch vụ.
- **3. Đề xuất cải thiện cụ thể:**
  - Thêm chức năng "Cấp thiết bị thay thế (Swap Device)": Gỡ máy hỏng ra khỏi hợp đồng, đưa vào diện bảo trì, và gán một máy dự phòng khả dụng trong kho vào hợp đồng của khách.
  - Trường hợp kho hết máy dự phòng: Kích hoạt tính năng "Tạm ngưng tính tiền thuê (Pause Billing)" trong những ngày chờ sửa chữa, tự động giảm trừ số tiền thuê tương ứng trên kỳ hạn.

---

### Vấn đề 4: Form báo hỏng chỉ có ô chữ mô tả, thiếu chức năng tải lên hình ảnh/video bằng chứng sự cố
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Controllers/BaoTriController.cs`, dòng 60–109 (Action `TaoPhieu`).
  - `RentalSystem/Views/BaoTri/TaoPhieu.cshtml`, dòng 11–39.
- **1. Tên vấn đề:** Form báo hỏng thiết bị thiếu chức năng tải lên tệp đa phương tiện (ảnh chụp / video hiện trạng lỗi).
- **2. Mô tả tác động thực tế:**
  Khi thiết bị gặp sự cố, khách hàng chỉ có một ô văn bản `moTaLoi` để gõ chữ (ví dụ gõ: "máy không lên hình"). Kỹ thuật viên không có hình ảnh để chẩn đoán sơ bộ xem máy bị rơi cấn móp góc hay lỗi cáp màn hình. Khi khách gửi máy về cửa hàng, nếu máy bị nứt vỏ, khách có thể khẳng định máy lúc ở nhà chưa nứt; cửa hàng không có bằng chứng hình ảnh lúc khách báo hỏng để đối chiếu.
- **3. Đề xuất cải thiện cụ thể:**
  - Cập nhật form `TaoPhieu.cshtml` bổ sung thẻ tải file: `<input type="file" name="hinhAnhSuCo" multiple accept="image/*,video/*" />`.
  - Bổ sung trường `HinhAnhLoi` vào model `PhieuBaoTri` để lưu trữ đường dẫn ảnh/video minh chứng.

---

### Vấn đề 5: Bảng `PhieuBaoTri` bắt buộc phải có `MaHopDong`, khiến quản trị viên không thể ghi nhận bảo dưỡng định kỳ cho thiết bị tồn kho
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Models/AppModels.cs`, dòng 123–137 (`[ForeignKey("HopDong")] public int MaHopDong { get; set; }`).
  - `RentalSystem/Areas/Admin/Controllers/BaoTriController.cs` (Không có action `Create`).
- **1. Tên vấn đề:** Phiếu bảo trì bắt buộc phải gắn với Hợp đồng, không thể lập phiếu bảo dưỡng định kỳ cho thiết bị đang tồn kho.
- **2. Mô tả tác động thực tế:**
  Trong bảng `ThietBi`, trạng thái `2` là "Đang bảo dưỡng / Sửa chữa". Khi một chiếc máy trong kho bị chai pin, lỗi quạt tản nhiệt hoặc cần vệ sinh tra keo, nhân viên không có cách nào tạo được phiếu bảo trì trên phần mềm vì trường `MaHopDong` là số nguyên bắt buộc (`int`, không cho null) và Controller không có action `Create` cho Admin. Hậu quả là máy trong kho được đem đi sửa "chui", không ghi nhận được lịch sử sửa chữa và chi phí bảo trì kho.
- **3. Đề xuất cải thiện cụ thể:**
  - Cho phép `MaHopDong` nhận giá trị null: `public int? MaHopDong { get; set; }`.
  - Thêm action `Create` trong `Admin/BaoTriController` cho phép thủ kho chọn trực tiếp thiết bị từ kho để bảo dưỡng định kỳ nội bộ.

---

### Vấn đề 6: Hợp đồng có thể hoàn tất thu hồi hoặc hủy bỏ khi phiếu bảo trì vẫn đang xử lý dở dang (Orphaned Tickets)
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 400–463 (Action `UpdateStatus`).
- **1. Tên vấn đề:** Cho phép đóng hoặc hủy hợp đồng khi các phiếu bảo trì liên quan vẫn đang trong quá trình xử lý dở dang.
- **2. Mô tả tác động thực tế:**
  Khi Admin bấm Hoàn tất (`status = 2`) hoặc Hủy hợp đồng (`status = 3`), code hoàn toàn không kiểm tra xem có phiếu bảo trì nào đang ở trạng thái `1` (Mới báo) hoặc `2` (Đang sửa) hay không. Hậu quả là hợp đồng đã đóng thành công, nhưng ngoài đời chiếc máy vẫn đang nằm tại trung tâm bảo hành của hãng. Phiếu bảo trì trở thành "phiếu mồ côi" không có hợp đồng hoạt động liên kết, gây sai lệch số liệu kiểm kê kho.
- **3. Đề xuất cải thiện cụ thể:**
  - Bổ sung điều kiện chặn trong `HopDongController.UpdateStatus`:
    ```csharp
    bool coPhieuChuaXong = await _context.PhieuBaoTris
        .AnyAsync(p => p.MaHopDong == id && (p.TrangThai == 1 || p.TrangThai == 2));
    if (coPhieuChuaXong)
    {
        TempData["Error"] = "Không thể hoàn tất hợp đồng: Còn phiếu bảo trì đang xử lý dở dang. Vui lòng đóng phiếu bảo trì trước!";
        return RedirectToAction(nameof(Details), new { id = id });
    }
    ```

---

### Vấn đề 7: Thiết bị bị "Hỏng không thể khắc phục" (`TrangThai = 4`) vẫn được tự động trả về kho ở trạng thái "Sẵn sàng cho thuê lại"
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/BaoTriController.cs`, dòng 76–84 (`UpdateStatus`).
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 423–427 (`UpdateStatus` status = 2).
- **1. Tên vấn đề:** Thiết bị bị đánh giá hỏng hoàn toàn (Status 4) vẫn được tự động trả về kho ở trạng thái sẵn sàng cho thuê khi đóng hợp đồng.
- **2. Mô tả tác động thực tế:**
  Đây là một lỗi logic dây chuyền rất nguy hiểm:
  1. Khi KTV xác định máy bị rơi vỡ nát không thể sửa chữa, họ chọn `PhieuBaoTri.TrangThai = 4`. Tuy nhiên, code trong `BaoTriController` không hề cập nhật gì vào bảng `ThietBi`.
  2. Khi khách bồi thường tiền xong, Admin vào `HopDongController` bấm "Hoàn tất (Thu hồi)". Tại dòng 423–427, code chạy vòng lặp gán: `tb.TrangThai = 0` (Sẵn sàng cho thuê)!
  3. Chiếc máy đã bị vỡ nát nay trở thành "Sẵn sàng cho thuê"! Khách hàng tiếp theo lên website đặt thuê sẽ được hệ thống gán trúng chiếc máy hỏng này.
- **3. Đề xuất cải thiện cụ thể:**
  - Trong `BaoTriController.UpdateStatus`: Nếu `status == 4`, lập tức cập nhật `tb.TrangThai = 4` (Thanh lý / Hủy bỏ) và `tb.TinhTrangMay = "Hỏng hoàn toàn - Đã hủy"`.
  - Trong `HopDongController.UpdateStatus`: Khi hoàn tất đơn, chỉ giải phóng về trạng thái 0 đối với máy bình thường; nếu máy có phiếu bảo trì trạng thái 4 thì giữ nguyên trạng thái thanh lý loại khỏi kho.

---

### Vấn đề 8: Khách hàng có thể tạo yêu cầu bảo trì cho hợp đồng chưa duyệt hoặc đã thanh lý từ lâu
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Controllers/BaoTriController.cs`, dòng 31–36 và dòng 69–76 (Action `TaoPhieu`).
- **1. Tên vấn đề:** Kiểm tra hợp lệ lỏng lẻo khi tạo phiếu báo hỏng, bỏ quên kiểm tra trạng thái hợp đồng (`hopDong.TrangThai`).
- **2. Mô tả tác động thực tế:**
  Trong `TaoPhieu`, code chỉ kiểm tra xem hợp đồng có thuộc về user hay không (`h.MaKhachHang == userId`). Khách hàng vừa ký đơn nhưng Admin chưa duyệt giao máy (`TrangThai == 0`), hoặc hợp đồng đã hoàn tất trả máy từ 6 tháng trước (`TrangThai == 2`), khách vẫn có thể truy cập URL `/BaoTri/TaoPhieu?hopDongId=...` và tạo phiếu báo hỏng thành công! Việc này làm rác CSDL và khiến kỹ thuật viên hoang mang khi nhận yêu cầu sửa máy cho hợp đồng đã đóng từ lâu.
- **3. Đề xuất cải thiện cụ thể:**
  - Bổ sung điều kiện chặn trong `TaoPhieu`: Hợp đồng bắt buộc phải đang ở trạng thái `1` (Đang thuê) thì mới cho phép tạo yêu cầu bảo trì:
    ```csharp
    if (hopDong.TrangThai != 1)
    {
        TempData["Error"] = "Chỉ có thể gửi yêu cầu bảo trì cho hợp đồng đang trong thời gian thuê!";
        return RedirectToAction("MyContracts", "Cart");
    }
    ```

---

### Vấn đề 9: Tham số `chiPhiSuaChua` trong Controller bị bỏ rơi và không lưu vào Database
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/BaoTriController.cs`, dòng 58 (`decimal? chiPhiSuaChua = null`) và dòng 61.
  - `RentalSystem/Models/AppModels.cs`, dòng 123–137 (Model `PhieuBaoTri`).
- **1. Tên vấn đề:** Controller tiếp nhận tham số `chiPhiSuaChua` nhưng không lưu vào Database do Model thiếu thuộc tính tương ứng.
- **2. Mô tả tác động thực tế:**
  Đây là một đoạn "mã chết" (dead code). Lập trình viên đã dự tính theo dõi chi phí sửa chữa thực tế của cửa hàng (`chiPhiSuaChua`), nhưng trong Model `PhieuBaoTri` chỉ có cột `PhiDenBu` (thu từ khách) mà không có cột `ChiPhiSuaChua` (chi phí cửa hàng bỏ ra). Khi KTV nhập chi phí sửa chữa và bấm lưu, con số này biến mất hoàn toàn. Cửa hàng không thể thống kê được chi phí bảo trì thực tế trong tháng.
- **3. Đề xuất cải thiện cụ thể:**
  - Bổ sung thuộc tính `[Column(TypeName = "decimal(18,2)")] public decimal ChiPhiSuaChua { get; set; }` vào model `PhieuBaoTri`.
  - Trong `BaoTriController.UpdateStatus`, gán: `phieu.ChiPhiSuaChua = chiPhiSuaChua ?? 0;`.

---

### Vấn đề 10: Giao diện khách hàng bị "mù thông tin" về tiến độ kỹ thuật, kỹ thuật viên và chi tiết phí đền bù
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Views/BaoTri/MyTickets.cshtml`, dòng 17–68.
  - `RentalSystem/Areas/Admin/Views/BaoTri/Index.cshtml`, dòng 14–53.
- **1. Tên vấn đề:** Giao diện khách hàng thiếu trang chi tiết phiếu bảo trì, không hiển thị tên KTV phụ trách, ghi chú tiến độ và chi tiết phí đền bù.
- **2. Mô tả tác động thực tế:**
  Trên bảng `MyTickets.cshtml`, khách hàng không biết ai là người đang sửa máy cho mình để liên hệ hỏi thăm tiến độ. Khách không đọc được `GhiChuSuaChua` (ví dụ KTV ghi: "đang chờ linh kiện từ hãng"). Đặc biệt, nếu phiếu bị chuyển sang trạng thái 4 (Hỏng không thể khắc phục), cột trạng thái trong view của khách còn bị **để trống hoàn toàn** vì code chỉ có các nhánh `if (TrangThai == 1) ... else if (TrangThai == 2) ... else if (TrangThai == 3)`.
- **3. Đề xuất cải thiện cụ thể:**
  - Xây dựng trang `/BaoTri/ChiTiet/{id}` dành riêng cho khách hàng: Hiển thị đầy đủ thông tin KTV phụ trách (Họ tên, SĐT), nhật ký tiến độ kỹ thuật, ảnh linh kiện thay thế và chi tiết phí bồi thường.
  - Bổ sung badge hiển thị cho trạng thái 4: `<span class="badge bg-danger">Hỏng không thể khắc phục</span>`.

---

### Vấn đề 11: Admin không thấy danh sách phiếu bảo trì trong màn hình Chi tiết Hợp đồng
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 43–73 (Action `Details`).
  - `RentalSystem/Areas/Admin/Views/HopDong/Details.cshtml`, dòng 1–407.
- **1. Tên vấn đề:** Màn hình Chi tiết Hợp đồng của Admin không hiển thị danh sách các phiếu bảo trì phát sinh của hợp đồng đó.
- **2. Mô tả tác động thực tế:**
  Khi Admin mở xem hợp đồng, họ chỉ thấy danh sách máy, lịch trả góp và phiếu thu. Không có bất kỳ thông tin nào về phiếu bảo trì. Khi Admin bấm nút "Hoàn tất hợp đồng", hệ thống đột ngột báo lỗi đỏ: *"Còn phí đền bù bảo trì chưa thanh toán (còn nợ: 1.500.000đ)!"*. Admin hoàn toàn không hiểu khoản nợ 1.500.000đ này từ đâu ra, do máy nào hỏng, vì màn hình hợp đồng không hiển thị thông tin phiếu bảo trì.
- **3. Đề xuất cải thiện cụ thể:**
  - Trong `HopDongController.Details`, nạp danh sách `PhieuBaoTris` liên kết với hợp đồng qua `ViewBag.PhieuBaoTris`.
  - Bổ sung một Card bảng "Lịch sử Bảo trì & Bồi thường Sự cố" trên `Details.cshtml`, hiển thị mã phiếu, thiết bị, lỗi, chi phí bồi thường và trạng thái xử lý.

---

### Vấn đề 12: Giao diện Admin Details thiếu lựa chọn trạng thái 4 và thiếu nút lập phiếu thu phí bảo trì
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Views/BaoTri/Details.cshtml`, dòng 43–47.
  - `RentalSystem/Areas/Admin/Controllers/BaoTriController.cs`, dòng 105–142 (Action `ThuPhiDenBu`, `ThuPhiBaoTri`).
- **1. Tên vấn đề:** Dropdown cập nhật trạng thái trong View thiếu lựa chọn `Status 4` và hoàn toàn không có giao diện gọi action thu phí bảo trì.
- **2. Mô tả tác động thực tế:**
  1. Trong View `Admin/BaoTri/Details.cshtml`, thẻ `<select name="status">` chỉ có 3 lựa chọn (1: Mới báo, 2: Đang xử lý, 3: Hoàn thành), hoàn toàn thiếu option `4` (Hỏng không thể khắc phục). KTV không thể chọn trạng thái 4 trên giao diện dù controller có code xử lý.
  2. Controller viết sẵn hai action `ThuPhiDenBu` và `ThuPhiBaoTri` rất chi tiết, nhưng trên file View lại không hề có bất kỳ form hay nút bấm nào để gọi đến hai action này.
- **3. Đề xuất cải thiện cụ thể:**
  - Thêm `<option value="4">Hỏng không thể khắc phục</option>` vào dropdown trạng thái.
  - Bổ sung form hoặc modal "Thu phí bồi thường bảo trì" ngay trên trang `Details.cshtml` cho phép thu tiền mặt hoặc chuyển khoản tại chỗ khi khách nộp tiền bồi thường.

---

### Vấn đề 13: Hệ thống quy chụp mọi chi phí sửa chữa thành "Phí đền bù" (`PhiDenBu`), thiếu phân định trách nhiệm hao mòn tự nhiên vs lỗi người dùng
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Models/AppModels.cs`, dòng 123–137 (Model `PhieuBaoTri` chỉ có duy nhất trường `PhiDenBu`).
- **1. Tên vấn đề:** Thiếu phân định trách nhiệm chi phí giữa hao mòn tự nhiên (cửa hàng chịu) và hư hỏng do người dùng (khách đền bù).
- **2. Mô tả tác động thực tế:**
  Khi thiết bị hỏng do linh kiện tự hết hạn sử dụng (ví dụ pin phồng tự nhiên, quạt hỏng sau 2 năm chạy), cửa hàng phải chịu chi phí bảo hành. Ngược lại, nếu máy bị rơi vỡ màn hình, khách mới phải đền. Hiện tại hệ thống chỉ có đúng một trường `PhiDenBu`. Nếu nhập vào thì hệ thống tự động bắt khách trả; nếu không nhập thì không theo dõi được chi phí cửa hàng bỏ ra để sửa máy.
- **3. Đề xuất cải thiện cụ thể:**
  - Bổ sung trường `LoaiTrachNhiem` (0: Cửa hàng bảo hành 100%, 1: Khách hàng làm hỏng bồi thường 100%, 2: Hai bên chia sẻ chi phí theo tỷ lệ). Chi phí cửa hàng bỏ ra sẽ được hạch toán vào chi phí vận hành, không tính vào công nợ của khách.

---

### Vấn đề 14: Thiếu cam kết thời gian xử lý sự cố (SLA) và cảnh báo chậm trễ kỹ thuật
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Controllers/BaoTriController.cs` và `RentalSystem/Areas/Admin/Controllers/BaoTriController.cs` (Không có trường thời hạn xử lý).
- **1. Tên vấn đề:** Thiếu cam kết thời gian hoàn thành xử lý sự cố (SLA) và thiếu cảnh báo chậm trễ kỹ thuật.
- **2. Mô tả tác động thực tế:**
  Khách hàng gửi máy báo hỏng nhưng không biết khi nào được lấy máy. Kỹ thuật viên nhận máy về "ngâm" cả tháng mà Admin không hề hay biết vì hệ thống không có ngày hẹn trả máy và không có cảnh báo quá hạn xử lý.
- **3. Đề xuất cải thiện cụ thể:**
  - Bổ sung trường `NgayHenTraMay` và `MucDoKhanCap` (1: Tiêu chuẩn - xử lý trong 48h, 2: Khẩn cấp - xử lý trong 12h) vào `PhieuBaoTri`.
  - Trên Dashboard Admin, hiển thị cảnh báo đỏ đối với các phiếu bảo trì quá hạn SLA cam kết để quản lý đôn đốc KTV.

---

### Vấn đề 15: Thực thể `LichSuThietBi` đã được khai báo nhưng là mã ngủ quên, không controller nào sử dụng
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Models/AppModels.cs`, dòng 50–58 (Model `LichSuThietBi` với các trường `MaThietBi`, `NgayGhiNhan`, `HanhDong`, `GhiChu`, `NguoiThucHien`).
  - Toàn bộ controllers trong solution không có câu lệnh `_context.LichSuThietBis.Add(...)`.
- **1. Tên vấn đề:** Thực thể `LichSuThietBi` là mã ngủ quên (dormant code), không được kích hoạt để theo dõi vòng đời thiết bị.
- **2. Mô tả tác động thực tế:**
  Quản trị viên không thể tra cứu được lịch sử của một chiếc máy: trong 2 năm qua máy đã cho bao nhiêu người thuê, bị hỏng mấy lần, đã từng thay thế linh kiện gì, do ai sửa. Mọi thông tin vòng đời thiết bị bị phân mảnh và biến mất.
- **3. Đề xuất cải thiện cụ thể:**
  - Kích hoạt ghi log tự động vào `LichSuThietBi` mỗi khi thiết bị: Được xuất kho cho thuê, Nhận báo hỏng, KTV tiếp nhận sửa chữa, Hoàn thành sửa chữa, và Thu hồi nhập kho.

---

# PHẦN 4: PHÂN HỆ CÔNG NỢ (DEBT MANAGEMENT DOMAIN)

Phân hệ Quản lý Công nợ kiểm soát việc thu hồi dòng tiền, theo dõi các khoản nợ đến hạn và trễ hạn, xử lý cấn trừ cọc và đảm bảo an toàn tài chính. Dưới đây là 15 vấn đề nghiệp vụ được phát hiện trong phân hệ này.

---

### Vấn đề 1: Thiếu quy trình tính tiền phạt và lãi suất trễ hạn khi khách thanh toán quá ngày đến hạn
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Models/AppModels.cs`, dòng 92–103 (Model `KyHanThanhToan`).
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 573–638 (Action `ConfirmPayment`).
- **1. Tên vấn đề:** Hệ thống không có cơ chế tính tiền phạt và lãi suất trễ hạn đối với các khoản thanh toán quá hạn.
- **2. Mô tả tác động thực tế:**
  Trong kinh doanh cho thuê, ngày đến hạn (`NgayDenHan`) là ranh giới tài chính bắt buộc. Nếu khách trễ hạn 10 ngày, 30 ngày hay 60 ngày, khi đến nộp tiền tại `ConfirmPayment`, số tiền thu vẫn chỉ là `k.SoTienPhai - k.SoTienDaTra`. Khách trả đúng hạn hay chây ì trả trễ cả tháng thì số tiền nộp đều y như nhau! Điều này tạo tiền lệ xấu, không khuyến khích khách trả nợ đúng hạn, gây thâm hụt dòng tiền hoạt động của doanh nghiệp.
- **3. Đề xuất cải thiện cụ thể:**
  - Bổ sung trường `TienPhat` và `SoNgayTreHan` vào `KyHanThanhToan`.
  - Tự động tính số ngày trễ khi `DateTime.Now > NgayDenHan`:
    $$\text{TienPhat} = \text{SoTienConLai} \times \text{LaiSuatNgay} \times \text{SoNgayTre}$$
  - Trong form thu tiền, hiển thị rõ: Tiền gốc kỳ hạn + Tiền phạt quá hạn = Tổng tiền cần thu.

---

### Vấn đề 2: Nút "Nhắc nợ" và "Xử lý thu hồi" chỉ là liên kết giả lập, thiếu hệ thống gửi thông báo nhắc nợ thực tế
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Views/CongNo/Index.cshtml`, dòng 101 và dòng 146.
- **1. Tên vấn đề:** Các nút hành động "Nhắc nợ" và "Xử lý thu hồi" trên trang Quản lý Công nợ chỉ là liên kết giả lập trỏ link về trang chi tiết hợp đồng.
- **2. Mô tả tác động thực tế:**
  Tại trang `/Admin/CongNo`, ở các tab "Đang trễ hạn" và "Sắp đến hạn", người dùng nhìn thấy các nút rất chuyên nghiệp như `[Nhắc nợ]` và `[Xử lý thu hồi]`. Tuy nhiên khi bấm vào, đó chỉ là thẻ `<a href="/Admin/HopDong/Details/...">` dẫn về trang chi tiết hợp đồng! Không có email nhắc nợ nào được gửi, không có SMS phát đi, và không có nhật ký nhắc nợ nào được lưu lại. Nhân viên không biết khách này đã được nhắc nợ bao nhiêu lần và ai là người nhắc.
- **3. Đề xuất cải thiện cụ thể:**
  - Tạo bảng `LichSuNhacNo` (gồm: `MaHopDong`, `MaKyHan`, `NgayNhac`, `HinhThuc`, `NoiDung`, `NguoiThucHien`, `PhanHoiCuaKhach`).
  - Thay thế link giả lập bằng action `GuiNhacNo(int maKyHan)` tích hợp gửi Email tự động đính kèm thông tin tài khoản ngân hàng và mã QR thanh toán.
  - Hiển thị số lần đã nhắc nợ ngay trên bảng quản lý công nợ (ví dụ: `Đã nhắc 2 lần`).

---

### Vấn đề 3: Thiếu quy trình phân bổ tuổi nợ theo chuẩn nghiệp vụ kế toán (Debt Aging Schedule)
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/CongNoController.cs`, dòng 25–35.
  - `RentalSystem/Areas/Admin/Views/CongNo/Index.cshtml`, dòng 10–20.
- **1. Tên vấn đề:** Phân loại công nợ sơ sài, thiếu phân bổ theo các nhóm tuổi nợ (Aging Buckets) chuẩn nghiệp vụ tài chính.
- **2. Mô tả tác động thực tế:**
  Trong quản lý tài chính, khoản nợ trễ 3 ngày khác hoàn toàn với khoản nợ đã trễ 90 ngày (nguy cơ mất vốn). Hiện tại, hệ thống ném tất cả các kỳ hạn trễ vào chung một rổ "Đang trễ hạn". Kế toán không thể biết bao nhiêu tiền nằm ở nhóm mới trễ (nhắc nhở nhẹ nhàng), bao nhiêu tiền nằm ở nhóm nợ khó đòi (cần chuyển bộ phận pháp chế / thu hồi máy tận nơi).
- **3. Đề xuất cải thiện cụ thể:**
  - Phân loại công nợ theo 4 dải tuổi nợ chuẩn:
    - **Nhóm 1:** Quá hạn 1 – 30 ngày (Nợ cần chú ý).
    - **Nhóm 2:** Quá hạn 31 – 60 ngày (Nợ dưới tiêu chuẩn).
    - **Nhóm 3:** Quá hạn 61 – 90 ngày (Nợ nghi ngờ).
    - **Nhóm 4:** Quá hạn > 90 ngày (Nợ có khả năng mất vốn - Khóa tài khoản khách).

---

### Vấn đề 4: Thiếu quy trình hoàn trả tiền cọc và lập chứng từ chi tiền xuất quỹ khi tất toán công nợ
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 400–463 (Action `UpdateStatus`).
  - `RentalSystem/Models/AppModels.cs`, dòng 112–122 (Thiếu model `PhieuChi`).
- **1. Tên vấn đề:** Thiếu quy trình hoàn cọc và chứng từ chi tiền xuất quỹ khi quyết toán công nợ hợp đồng.
- **2. Mô tả tác động thực tế:**
  Khi hợp đồng bị hủy (`status = 3`, dòng 445–453), hệ thống chỉ nối một dòng chữ vào trường Ghi chú: `hopDong.GhiChu += " [Yêu cầu hoàn trả cọc/tiền thuê: " + totalCollected + " VNĐ]";`. Hoàn toàn không có nút "Xác nhận đã hoàn cọc", không lưu vết hình thức chi tiền. Dòng tiền chi ra của cửa hàng bị thất thoát khỏi sổ sách kế toán.
- **3. Đề xuất cải thiện cụ thể:**
  - Bổ sung bảng `PhieuChi` và màn hình "Quyết toán công nợ & Hoàn cọc":
    $$\text{Tiền hoàn trả} = \text{Tiền cọc ban đầu} - \text{Tiền thuê còn thiếu} - \text{Phí bồi thường máy hỏng}$$
    Tự động sinh `PhieuChi` khi nhân viên bấm xác nhận hoàn tiền cho khách.

---

### Vấn đề 5: Thiết bị vật lý bị phong tỏa "chết" trong kho nếu khách hàng còn nợ tiền thuê
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 401–428 (Action `UpdateStatus`).
- **1. Tên vấn đề:** Ràng buộc cứng `TrangThaiThanhToan == 2` mới giải phóng máy, dẫn đến việc thiết bị đã thu hồi về kho nhưng phần mềm vẫn báo "Đang cho thuê".
- **2. Mô tả tác động thực tế:**
  Khách hàng mang 3 chiếc laptop đến trả tại cửa hàng đúng hạn. Máy đã nằm an toàn trên kệ kho. Nhưng khách còn thiếu 200.000đ tiền thuê kỳ cuối và xin chuyển khoản sau. Do khách còn nợ 200.000đ (`TrangThaiThanhToan != 2`), Admin KHÔNG THỂ BẤM "Hoàn tất (Thu hồi)"! Và vì không bấm được hoàn tất, 3 chiếc laptop trên phần mềm VẪN MANG TRẠNG THÁI `1` (Đang cho thuê)! Hậu quả: 3 chiếc laptop nằm sờ sờ trong kho nhưng hệ thống không cho ai thuê vì phần mềm nghĩ máy vẫn ở nhà khách cũ. Tài sản bị "chôn chân" vô lý chỉ vì một khoản nợ nhỏ chưa thu xong.
- **3. Đề xuất cải thiện cụ thể:**
  - Tách bạch hoàn toàn giữa **Quy trình thu hồi thiết bị vật lý** và **Quy trình quyết toán công nợ tài chính**:
    1. Thêm trạng thái hợp đồng: `4 - Đã trả máy (Chờ quyết toán công nợ)`.
    2. Khi khách mang máy về, Admin bấm "Xác nhận thu hồi máy": Thiết bị lập tức được trả về kho (`ThietBi.TrangThai = 0`), sẵn sàng cho người khác thuê ngay.
    3. Khoản nợ còn lại của hợp đồng được chuyển sang danh sách nợ để kế toán tiếp tục theo dõi đòi nợ độc lập.

---

### Vấn đề 6: Thu cọc bổ sung làm ghi đè và phá vỡ số tiền phải trả ban đầu của kỳ hạn (`SoTienPhai`)
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 741–748 (Action `ThemTienCoc`):
    ```csharp
    if (remainingDeposit >= unpaidInPeriod) {
        k.SoTienPhai = k.SoTienDaTra; // GHI ĐÈ SỐ TIỀN PHẢI TRẢ!
        k.TrangThai = 1;
        k.SoTienDaTra = k.SoTienPhai;
        ...
    } else {
        k.SoTienPhai -= remainingDeposit; // GIẢM SỐ TIỀN PHẢI TRẢ!
    }
    ```
- **1. Tên vấn đề:** Thuật toán cấn trừ cọc bổ sung sửa trực tiếp trường `k.SoTienPhai` thay vì tăng `k.SoTienDaTra`, phá vỡ dữ liệu gốc của kỳ hạn.
- **2. Mô tả tác động thực tế:**
  Đây là một sai lầm nghiêm trọng về nguyên lý kế toán: Kỳ 1 có số tiền phải trả gốc là `SoTienPhai = 1.000.000đ`. Khách nộp cọc bổ sung 400.000đ. Code chạy dòng `k.SoTienPhai -= 400.000đ`, biến `SoTienPhai` thành `600.000đ`! Sau này khi in lại lịch sử hợp đồng hoặc đối soát, kỳ hạn đó hiển thị "Phải trả: 600.000đ, Đã trả: 0đ". Số tiền gốc ban đầu của hợp đồng (1.000.000đ) bị xóa sổ vĩnh viễn khỏi CSDL! Tổng các kỳ hạn cộng lại không còn khớp với tổng giá trị hợp đồng ban đầu.
- **3. Đề xuất cải thiện cụ thể:**
  - Tuyệt đối không được sửa giá trị gốc `SoTienPhai`. Tiền cọc bổ sung phải được hạch toán bằng cách tăng số tiền đã trả:
    ```csharp
    k.SoTienDaTra += allocatedDeposit;
    k.GhiChu += $" (Cấn trừ {allocatedDeposit:N0}đ từ cọc bổ sung)";
    if (k.SoTienDaTra >= k.SoTienPhai) k.TrangThai = 1;
    ```

---

### Vấn đề 7: Tiền trả thừa kỳ hạn bị "bỏ tù" trong ghi chú, không tự động cấn trừ cho kỳ tiếp theo
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 595–598 (Action `ConfirmPayment`).
- **1. Tên vấn đề:** Xử lý đóng tiền thừa kỳ hạn bị lưu dưới dạng text trong Ghi chú, không tự động chuyển sang trừ vào kỳ tiếp theo.
- **2. Mô tả tác động thực tế:**
  Khách nộp dư tiền ở Kỳ 1, hệ thống chỉ ghi chú text `(Trả thừa ...)`. Sang Kỳ 2, hệ thống vẫn báo nợ nguyên vẹn và nhảy vào danh sách trễ hạn khi đến ngày. Tiền của khách đã nộp vào nhưng không được khấu trừ nợ thực tế.
- **3. Đề xuất cải thiện cụ thể:**
  - Áp dụng thuật toán Waterfall Payment Carryover: Tự động chuyển số tiền dư sang kỳ tiếp theo chưa thanh toán, sinh phiếu thu tương ứng và cập nhật trạng thái nợ minh bạch.

---

### Vấn đề 8: Màn hình Công nợ tổng hợp loại trừ hoàn toàn các khoản phí bồi thường hư hỏng máy
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Views/CongNo/Index.cshtml`, dòng 42–43 (`var conNo = hd.TongTien - daThu;`).
  - `RentalSystem/Areas/Admin/Views/HopDong/Details.cshtml`, dòng 318.
- **1. Tên vấn đề:** Công thức tính công nợ trên màn hình tổng hợp chỉ lấy tiền thuê mà bỏ quên phí bồi thường hư hỏng máy (`PhiDenBu`).
- **2. Mô tả tác động thực tế:**
  Khách hàng đã đóng đủ 100% tiền thuê (`TongTien - daThu == 0`), nhưng trong quá trình thuê làm vỡ màn hình và bị lập phiếu phạt bảo trì `PhiDenBu = 4.000.000đ` chưa trả. Khi Admin mở trang "Quản lý Công Nợ", hợp đồng này **biến mất hoàn toàn** khỏi danh sách nợ (vì `conNo = 0`)! Doanh nghiệp hoàn toàn "quên mất" khoản nợ 4 triệu này, dẫn đến nguy cơ thất thoát tiền bồi thường.
- **3. Đề xuất cải thiện cụ thể:**
  - Sửa đổi công thức tính nợ toàn diện:
    $$\text{Tổng phải thu} = \text{HopDong.TongTien} + \sum \text{PhieuBaoTri.PhiDenBu}$$
    $$\text{Thực tế còn nợ} = \text{Tổng phải thu} - \sum \text{PhieuThu.SoTien}$$

---

### Vấn đề 9: Trạng thái trễ hạn (`TrangThai = 2`) trong `KyHanThanhToan` là mã chết trong Database
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Models/AppModels.cs`, dòng 100 (`// 0: Chưa trả, 1: Đã trả, 2: Trễ hạn`).
  - Toàn bộ controllers không có nơi nào gán `k.TrangThai = 2`.
- **1. Tên vấn đề:** Trạng thái `TrangThai = 2` (Trễ hạn) không bao giờ được ghi vào CSDL, chỉ tính tạm thời trên Razor View.
- **2. Mô tả tác động thực tế:**
  Trong CSDL, cột `TrangThai` của bảng `KyHanThanhToans` chỉ luôn mang giá trị `0` hoặc `1`. Kế toán không thể dùng truy vấn SQL trực tiếp để lọc nợ quá hạn. Hệ thống không thể đánh chỉ mục (index) tối ưu hóa truy vấn cho các khoản nợ xấu khi dữ liệu lớn dần.
- **3. Đề xuất cải thiện cụ thể:**
  - Viết Background Service chạy hàng ngày lúc 00:01: Quét tất cả kỳ hạn có `TrangThai == 0` và `NgayDenHan < DateTime.Now`, cập nhật chính thức `k.TrangThai = 2` vào CSDL.

---

### Vấn đề 10: Khách hàng thiếu trang Sổ chi tiết công nợ tổng hợp (Customer Debt Ledger)
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Controllers/CartController.cs`, dòng 310–322 (Action `MyContracts`).
  - `RentalSystem/Views/Cart/ContractDetail.cshtml`.
- **1. Tên vấn đề:** Khách hàng thiếu trang Sổ chi tiết công nợ tổng hợp để theo dõi toàn bộ các khoản nợ cá nhân.
- **2. Mô tả tác động thực tế:**
  Một khách hàng thuê nhiều thiết bị trên nhiều hợp đồng khác nhau không có trang tổng quan để biết: "Hiện tại tôi đang nợ cửa hàng tổng cộng bao nhiêu tiền?", "Hạn đóng tiền tiếp theo là ngày nào, của hợp đồng nào?". Khách phải mở từng hợp đồng ra để tự tính nhẩm, và không thấy được các khoản phạt bảo trì phát sinh.
- **3. Đề xuất cải thiện cụ thể:**
  - Xây dựng trang `/Account/MyDebt` (Sổ công nợ của tôi) dành riêng cho khách hàng: Liệt kê tổng dư nợ hiện tại, danh sách kỳ hạn sắp đến hạn trong 7 ngày tới, các khoản phí bồi thường và nút thanh toán nhanh qua mã QR.

---

### Vấn đề 11: Admin thiếu Bảng điều khiển (Dashboard) phân tích công nợ và công cụ lọc/tìm kiếm, xuất Excel
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/CongNoController.cs`, dòng 25–35.
  - `RentalSystem/Areas/Admin/Views/CongNo/Index.cshtml`, dòng 1–157.
- **1. Tên vấn đề:** Trang Quản lý Công nợ của Admin chỉ là các bảng tĩnh thuần túy, thiếu KPI Dashboard, bộ lọc đa tiêu chí và tính năng xuất Excel.
- **2. Mô tả tác động thực tế:**
  Trang `/Admin/CongNo` không có 4 Card KPI đầu trang (Tổng công nợ toàn hệ thống, Tổng nợ quá hạn, Tỷ lệ thu hồi nợ %, Số khách hàng nợ xấu). Không có ô tìm kiếm theo Tên khách, Số điện thoại hay Mã hợp đồng. Khi hệ thống có hàng trăm hợp đồng, kế toán phải cuộn trang tìm bằng mắt thường và không thể xuất file Excel để báo cáo tài chính cuối tháng.
- **3. Đề xuất cải thiện cụ thể:**
  - Bổ sung hàng Card KPI thống kê công nợ ở đầu trang `CongNo/Index.cshtml`.
  - Thêm thanh tìm kiếm đa tiêu chí (Khách hàng, SĐT, Mã HĐ, Khoảng tiền nợ).
  - Tích hợp thư viện xuất Excel (ClosedXML hoặc EPPlus) cho phép xuất danh sách công nợ chi tiết chỉ với 1 click.

---

### Vấn đề 12: Hướng dẫn chuyển khoản VietQR không hỗ trợ thanh toán cho phí bảo trì phát sinh
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Views/Cart/ContractDetail.cshtml`, dòng 217–260:
    `@if (kyHans != null && kyHans.Any(k => k.TrangThai == 0)) { ... }`
- **1. Tên vấn đề:** Khối QR Code chuyển khoản biến mất hoàn toàn khi khách đã trả hết kỳ hạn thuê nhưng vẫn còn nợ phí bảo trì máy hỏng.
- **2. Mô tả tác động thực tế:**
  Khách hàng đã hoàn thành đầy đủ tất cả các kỳ hạn trả góp tiền thuê. Sau đó máy bị hỏng và phát sinh phí bồi thường 1.000.000đ. Do các kỳ hạn đều đã thanh toán đủ (`TrangThai == 1`), điều kiện `Any(k => k.TrangThai == 0)` trả về **false**. Toàn bộ khối hướng dẫn chuyển khoản và mã VietQR biến mất khỏi màn hình của khách! Khách muốn chuyển khoản 1.000.000đ phí bồi thường thì không biết chuyển vào tài khoản nào và cú pháp ra sao.
- **3. Đề xuất cải thiện cụ thể:**
  - Cập nhật điều kiện hiển thị mã VietQR: Hiển thị nếu còn kỳ hạn chưa trả HOẶC còn nợ phí bảo trì:
    ```csharp
    bool conNoBaoTri = ViewBag.PhiBaoTriChuaTra > 0;
    bool conNoKyHan = kyHans != null && kyHans.Any(k => k.TrangThai == 0);
    if (conNoKyHan || conNoBaoTri) { ... }
    ```

---

### Vấn đề 13: Đánh đồng khái niệm "Tiền cọc đảm bảo tài sản" với "Tiền thuê trả trước"
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 362 (Action `UpdateStatus` / `Create`):
    `decimal tienMoiKy = (hopDong.TongTien - hopDong.TienDaCoc) / soKy;`
- **1. Tên vấn đề:** Mã nguồn đánh đồng bản chất kế toán giữa "Tiền cọc đảm bảo tài sản" và "Tiền thuê trả trước".
- **2. Mô tả tác động thực tế:**
  Hệ thống lấy toàn bộ tiền cọc (`TienDaCoc`) đem trừ thẳng vào tiền thuê khi tính kỳ hạn trả góp! Nghĩa là cửa hàng không hề giữ đồng cọc nào để bảo đảm cho chiếc máy. Nếu khách làm mất máy, cửa hàng trắng tay vì tiền cọc đã bị cấn trừ hết vào tiền thuê hàng tháng.
- **3. Đề xuất cải thiện cụ thể:**
  - Tách bạch 2 khoản tiền riêng biệt trong Hợp đồng:
    1. `TienCocBaoDamMay` (Security Deposit): Giữ nguyên vẹn 100% trong suốt thời gian thuê để bảo đảm an toàn tài sản, chỉ dùng để đền bù nếu mất máy/hỏng hóc, hoàn trả lại khi kết thúc hợp đồng.
    2. `TienThueTraTruoc` (Advance Rent): Khoản tiền thuê trả trước dùng để cấn trừ vào các kỳ hạn.

---

### Vấn đề 14: Thiếu cơ chế "Khóa tài khoản nợ xấu" (Customer Blacklist & Rent Lock)
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Controllers/CartController.cs`, dòng 170–302 (Action `Checkout`).
- **1. Tên vấn đề:** Khách hàng đang bùng nợ quá hạn ở hợp đồng cũ vẫn có thể tự do đặt thuê thêm các thiết bị mới.
- **2. Mô tả tác động thực tế:**
  Action `Checkout` không hề kiểm tra lịch sử công nợ của khách hàng. Một khách hàng đang nợ quá hạn 10 triệu đồng ở hợp đồng A vẫn có thể đặt thuê thêm laptop ở hợp đồng B để ôm thêm máy của cửa hàng, tạo rủi ro mất tài sản dây chuyền.
- **3. Đề xuất cải thiện cụ thể:**
  - Bổ sung quy tắc kiểm tra nợ xấu tại `Checkout`: Nếu khách hàng có kỳ hạn quá hạn > 15 ngày hoặc tổng dư nợ quá hạn > 3.000.000đ, hệ thống tạm khóa quyền đặt thuê mới cho đến khi khách tất toán nợ cũ.

---

### Vấn đề 15: Xác nhận thu tiền phụ thuộc hoàn toàn vào thao tác bấm tay thủ công, thiếu tự động hóa đối soát ngân hàng
- **Căn cứ mã nguồn quan sát:**
  - `RentalSystem/Areas/Admin/Controllers/HopDongController.cs`, dòng 573–638 (Action `ConfirmPayment`).
- **1. Tên vấn đề:** Xác nhận thanh toán phụ thuộc 100% vào thao tác thủ công của nhân viên, thiếu Webhook đối soát ngân hàng tự động.
- **2. Mô tả tác động thực tế:**
  Khách chuyển khoản đúng cú pháp lúc nửa đêm nhưng phải đợi đến sáng hôm sau nhân viên mở máy lên bấm thì nợ mới được xóa. Dễ dẫn đến việc hệ thống gửi nhầm thông báo đòi nợ khi khách đã trả tiền xong.
- **3. Đề xuất cải thiện cụ thể:**
  - Tích hợp cổng Webhook Open Banking (như SePay hoặc Casso): Khi khách chuyển khoản đúng cú pháp `HD[MaHopDong]`, hệ thống tự động gạch nợ kỳ hạn tương ứng trong vòng 5 giây mà không cần con người can thiệp.

---

# TỔNG KẾT VÀ LỘ TRÌNH HOÀN THIỆN ĐỒ ÁN (CONCLUSION & ROADMAP)

Báo cáo trên đã phân tích chi tiết **61 vấn đề nghiệp vụ cốt lõi** trải dài qua 4 phân hệ quan trọng nhất của hệ thống Rental System:
- **Phân hệ Hợp đồng:** 16 vấn đề
- **Phân hệ Thanh toán:** 15 vấn đề
- **Phân hệ Bảo trì:** 15 vấn đề
- **Phân hệ Quản lý Công nợ:** 15 vấn đề

### Bảng tóm tắt các điểm nghẽn nghiêm trọng nhất cần ưu tiên hoàn thiện:

| Phân hệ | Điểm nghẽn rủi ro lớn nhất | Tác động thực tế | Giải pháp ưu tiên hàng đầu |
|---|---|---|---|
| **Hợp đồng** | Xuất máy khi chưa ký CCCD; Cho phép hủy đơn khi khách đang giữ máy; Thiếu hoàn cọc | Mất máy, thất thoát tài sản, tranh chấp pháp lý với khách | Ràng buộc State Machine, chặn duyệt khi thiếu chữ ký, thêm quy trình hoàn cọc |
| **Thanh toán** | Cổng VNPay bị bỏ rơi; VietQR amount=0; Lệch tiền lẻ kỳ hạn; Race condition | Thu tiền thủ công, khách gõ sai tiền, sai lệch sổ quỹ | Triển khai VNPay + VietQR động, làm tròn tài chính, bọc DB Transaction |
| **Bảo trì** | Máy vỡ nát (Status 4) tự động biến thành máy sẵn sàng cho thuê; Khách không được duyệt báo giá | Cho thuê trúng máy hỏng, tranh chấp chi phí đền bù gay gắt | Cập nhật triệt để trạng thái thiết bị trong kho, bổ sung bước khách duyệt báo giá |
| **Công nợ** | Máy về kho bị phong tỏa "chết" vì khách còn nợ; Báo cáo nợ quên phí bảo trì; Không tính phạt trễ | Tài sản bị giam lỏng không cho thuê được; Báo cáo tài chính sai lệch | Tách rời thu hồi máy khỏi thu nợ tài chính, tích hợp phí bảo trì vào tổng nợ |

### Lời nhắn nhủ dành cho nhóm phát triển sinh viên:
Một đồ án tốt nghiệp công nghệ thông tin xuất sắc không chỉ nằm ở việc giao diện đẹp hay sử dụng công nghệ mới nhất (.NET 9, MVC, EF Core), mà thước đo giá trị cao nhất của người kỹ sư phần mềm chính là **sự thấu hiểu nghiệp vụ thực tế (Domain Knowledge) và tính chặt chẽ trong luồng dữ liệu (Data Integrity)**.

Việc nhận diện và giải quyết dứt điểm các kẽ hở nghiệp vụ nêu trong báo cáo này sẽ là điểm cộng cực kỳ lớn trước Hội đồng phản biện Đồ án, khẳng định năng lực phân tích thiết kế hệ thống chuyên nghiệp và tư duy sản phẩm sẵn sàng triển khai trong thực tế doanh nghiệp!
