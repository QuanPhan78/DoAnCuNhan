# Kịch bản nói và thao tác — 11 phút 30 giây

Mục tiêu: chứng minh dữ liệu đi từ Mobile sang Web và kết quả xử lý quay về Mobile. Giữ điện thoại ở tài khoản `customer@demo.invalid`; các phiên Web đã đăng nhập đúng vai trò. Mật khẩu demo chung `Demo@123`. Đọc bảng nhắc một trang, không mở tài liệu này trên màn chiếu trong lúc nói.

## 0:00–0:40 — Mở đầu

**Màn hình:** trang danh mục trên điện thoại chiếu qua scrcpy; Web kinh doanh đặt cạnh.

**Nói:** “Em xin trình bày chương trình RentalSystem theo quá trình khách hàng thuê và sử dụng thiết bị. Khách hàng thao tác trên ứng dụng di động; nhân viên kinh doanh, kỹ thuật và quản trị làm việc trên Web. Em sẽ đối chiếu dữ liệu giữa hai nền tảng trong quá trình thao tác.”

**Thao tác:** chỉ tên tài khoản khách hàng và giao diện Mobile. Không đọc danh sách công nghệ ở đoạn này.

## 0:40–2:30 — Khách gửi yêu cầu thuê trên Mobile

1. Vào thiết bị, chọn **Laptop Demo Dell Latitude 5430** → **Thuê ngay**.
2. Hình thức **Theo ngày**, số lượng **1**. Chọn ngày bắt đầu D và kết thúc **D+6**, tương ứng 7 ngày lịch theo cách tính hiện tại của ứng dụng.
3. Địa chỉ: **Phòng demo, 123 Đường Minh Họa, TP.HCM**. Ghi chú: **DEMO LIVE**.
4. Xem màn xác nhận: **1.190.000đ**. Chỉ xác nhận khi đúng giá trị này. Bấm xác nhận thuê.
5. Xem đơn trong danh sách, ghi mã được trả về vào ô “Đơn mới” trên bảng nhắc. Đơn ở trạng thái chờ duyệt.

**Nói:** “Khách chọn thiết bị đang có sẵn, thời gian và địa chỉ nhận. Ứng dụng hiển thị số tiền dự kiến trước khi gửi. Đây là yêu cầu thuê mới; ở bước này chưa thực hiện thu cọc.”

**Điểm cần thấy:** tạo thành công và có đúng mã đơn; không chỉ dừng ở thông báo thành công.

## 2:30–4:00 — Đối chiếu trên Web kinh doanh

1. Sang phiên **Kinh doanh Demo**, mở `/Admin/HopDong`, tải lại trang.
2. Mở đúng mã đơn vừa tạo; kiểm tra khách **Khách hàng Demo An**, sản phẩm, thời gian thuê và **1.190.000đ**.
3. Chỉ trạng thái chờ duyệt và phần đã thu cọc **0đ**. Nếu cần giải thích, cọc tham khảo ở sản phẩm là **8.000.000đ**, chưa phải khoản đã thu.

**Nói:** “Yêu cầu vừa gửi trên Mobile đã có trong danh sách của nhân viên kinh doanh. Em đối chiếu mã đơn, khách hàng và số tiền để xác nhận đây là cùng một giao dịch. Nhân viên tiếp tục kiểm tra hồ sơ và thực hiện các bước bàn giao theo quy trình.”

**Điểm cần thấy:** mã đơn trên Web trùng với Mobile.

## 4:00–5:00 — Chuyển sang hợp đồng đang thuê đã chuẩn bị

1. Mở `/Admin/HopDong/Details/1`, chỉ **HD-0001**, serial **DEMO-LAP-001**.
2. Cuộn đến chữ ký hai bên; mở biên bản bàn giao mã **1** nếu cần. Các ảnh ghi rõ **DEMO ONLY**.

**Nói nguyên câu chuyển:** “Để minh họa giai đoạn sau bàn giao trong thời gian cho phép, em chuyển sang hợp đồng HD-0001 đã chuẩn bị đầy đủ hồ sơ và đang thuê. Đây là hợp đồng khác với yêu cầu vừa tạo. Hồ sơ và chữ ký trong buổi demo đều là dữ liệu giả lập.”

**Điểm cần thấy:** một thiết bị vật lý có serial và hồ sơ gắn với hợp đồng.

## 5:00–6:30 — Khách báo sự cố

1. Điện thoại: vào **Hợp đồng**, tải danh sách, bảo đảm có **HD-0001**. Sau đó vào **Yêu cầu & Sự cố** → dấu **+**.
2. Chọn hợp đồng **HD-0001** và thiết bị có **DEMO-LAP-001**.
3. Loại sự cố **Mất kết nối**, mô tả **Máy không kết nối Wi-Fi**, mức độ **Trung bình**. Không thêm ảnh mô phỏng.
4. Gửi; tải lại danh sách. Sang Web quản trị `/Admin/BaoTri`, mở phiếu mới, ghi mã **SC-…** vào bảng nhắc.
5. Đối chiếu hợp đồng, serial và nội dung lỗi.

**Nói:** “Trong quá trình sử dụng, khách gửi yêu cầu hỗ trợ gắn với đúng hợp đồng và thiết bị. Khi tải lại Web, nhân viên thấy nội dung lỗi này để tiếp nhận.”

## 6:30–8:30 — Phân công và xử lý kỹ thuật

1. Phiên **Quản trị Demo**: ở chi tiết phiếu mới, chọn **Kỹ thuật Demo**; trạng thái **1 – Mới tiếp nhận**; ghi chú **Đã phân công kỹ thuật Demo**; bấm **Cập Nhật Tiến Độ & Thông Tin**.
2. Sang phiên **Kỹ thuật Demo**, mở `/Admin/BaoTri`, tải lại và mở đúng phiếu.
3. Chọn **2 – Đang sửa chữa**, ghi chú **Đang kiểm tra kết nối Wi-Fi**, lưu.
4. Chọn **3 – Đã sửa xong (Chờ nghiệm thu)**. Ghi kết quả **Đã cấu hình lại kết nối, kiểm tra hoạt động ổn định**; nguyên nhân **Cấu hình mạng**; linh kiện **Không thay linh kiện**.
5. Giữ phí sửa chữa và bồi thường **0đ**, trách nhiệm **Cửa hàng/Bảo hành**, không chọn tạm dừng tính tiền hoặc thu phí ngay. Lưu.

**Nói:** “Quản trị phân công người phụ trách. Kỹ thuật viên cập nhật khi bắt đầu và khi sửa xong, kèm nguyên nhân và kết quả xử lý. Tình huống này chỉ cấu hình lại kết nối, không phát sinh phí.”

**Điểm cần thấy:** đúng tên kỹ thuật viên, đúng phiếu, trạng thái đã sửa xong và nội dung xử lý đã lưu.

## 8:30–9:30 — Xem kết quả và đánh giá trên Mobile

1. Tải lại **Yêu cầu & Sự cố** hoặc danh sách bảo trì trên điện thoại, mở đúng phiếu để xem trạng thái/kết quả sửa chữa. Có thể vào lại màn hình nếu danh sách chưa tải mới.
2. Vào **Phản hồi** → tạo phản hồi. Chủ đề bắt buộc chọn **Bảo trì**.
3. Ô tham chiếu nhập đúng **SC-…** vừa ghi, chọn **5 sao**; nội dung **Hỗ trợ nhanh, máy hoạt động ổn định**; gửi.
4. Nếu còn thời gian, tải lại Web chi tiết phiếu để chỉ phản hồi được lưu.

**Nói:** “Khách tải lại để theo dõi kết quả, sau đó gửi đánh giá cho đúng phiếu bảo trì. Phản hồi được lưu cùng quá trình hỗ trợ.”

Không để chủ đề mặc định “Chung”: dữ liệu đánh giá cần mã phiếu bảo trì. Nếu phiếu trực tiếp gặp lỗi, dùng **SC-0001** và nói rõ đó là phiếu dự phòng thuộc **HD-0002**.

## 9:30–10:45 — Báo cáo quản trị

1. Sang phiên quản trị `/Admin/ThongKe`. Chọn khoảng tùy chỉnh theo `manifest.json`: ngày chuẩn bị trừ 60 ngày đến ngày chuẩn bị.
2. Chỉ **doanh thu** và **công nợ**; giải thích một kỳ đã thanh toán, một kỳ chưa đến hạn, một kỳ quá hạn. HD-0004 là dữ liệu minh họa quá hạn.
3. Bấm **Xuất Excel**, mở tệp nếu kịp; nếu tải chậm, mở bản đã xuất trong `outputs/demo-check/evidence/BaoCaoDemo.xlsx` và nói đó là bản chuẩn bị trước từ cùng bộ giả lập.

**Nói:** “Từ dữ liệu hợp đồng và phiếu thu, quản trị theo dõi doanh thu cùng công nợ theo kỳ. Báo cáo có thể xuất Excel để tiếp tục tổng hợp và lưu trữ.”

Không đọc một con số doanh thu cố định: chỉ vào số đang hiển thị của kỳ đã chọn.

## 10:45–11:30 — Sao lưu và kết thúc

1. Mở `/Admin/Database`, chỉ tên **RentalSystemDemoDB** và thông tin các bảng.
2. Tải sao lưu **JSON**. Không chọn `.bak` để tránh phụ thuộc quyền thư mục dịch vụ SQL Server trong lúc trình bày.
3. Nói một câu về khôi phục đã được kiểm tra trên CSDL thử riêng, nếu báo cáo kiểm chứng ghi nhận thành công.

**Nói:** “Quản trị có chức năng sao lưu dữ liệu. Ảnh và chữ ký được giữ kèm trong gói dự phòng. Qua phần demo, hệ thống thể hiện việc tiếp nhận yêu cầu giữa Mobile và Web, theo dõi quá trình bảo trì và tổng hợp thông tin quản lý. Em xin kết thúc phần trình diễn.”

## Xử lý gián đoạn và câu hỏi

| Tình huống | Cách chuyển và lời nói |
|---|---|
| Mất kết nối | Thử một lần, tối đa 20 giây. “Em xin chuyển sang bản quay trước của bước này.” Mở đúng clip đã kiểm tra. |
| Không tạo được đơn mới | Mở HD-0003. “Em dùng yêu cầu đã chuẩn bị để tiếp tục minh họa bước tiếp nhận; yêu cầu trực tiếp vừa rồi chưa hoàn thành.” |
| Phiếu mới chưa xử lý được | Mở SC-0001/HD-0002. “Em chuyển sang phiếu dự phòng đã sửa xong để minh họa phần khách đánh giá.” |
| Đến phút 9 vẫn đang bảo trì | Giữ đoạn Mobile xem kết quả/đánh giá; báo cáo chỉ chỉ hai chỉ số và tệp sẵn; sao lưu giới thiệu một câu. |
| Hỏi thanh toán | Mở phiếu thu giả lập mã 1, giải thích tiền thuê và tiền cọc là hai khoản. Không gọi giao dịch mẫu là giao dịch ngân hàng thật. |
| Hỏi phân quyền | Dùng phiên kỹ thuật thử mở `/Admin/ThongKe` để minh họa bị từ chối. Trình bày đúng giới hạn API trong README. |
| Hỏi khôi phục | Mở `outputs/demo-check/verification.json` để trình bày kết quả; nếu cần thao tác, dùng CSDL DemoCheck riêng, không khôi phục đè buổi demo đang chạy. |
| Hỏi ký hợp đồng | Chỉ khu vực chữ ký trên hợp đồng và nói rõ chữ ký viết tay/ảnh minh họa, không có chứng thư số trong bản demo này. |

## Phiếu tự chấm sau mỗi lượt tập

- ☐ Nói rõ hai hợp đồng khác nhau khi chuyển sang HD-0001.
- ☐ Mã đơn, số tiền khớp Mobile và Web.
- ☐ Phiếu sự cố đúng HD-0001 / DEMO-LAP-001; phân công đúng Kỹ thuật Demo.
- ☐ Mobile xem được kết quả sửa; gửi 5 sao thành công với chủ đề Bảo trì và đúng mã phiếu.
- ☐ Excel và sao lưu tải được; video dự phòng mở được.
- ☐ Tổng thời gian ≤12 phút. Ghi thời gian thật vào bảng trong README.
