# Kết quả kiểm tra riêng Web — 04/11/2026

**38/38 kiểm tra đạt**, trên `http://localhost:5000`, CSDL `RentalSystemDemoDB`.

Phương pháp: gửi các biểu mẫu MVC Web bằng HTTP có cookie đăng nhập và mã chống giả mạo, đọc lại trang và bản sao lưu để đối chiếu dữ liệu. Không gọi `/api`, không kiểm tra điện thoại. Bộ điều khiển trình duyệt gặp lỗi trong phiên này nên kết quả không được coi là xác nhận thao tác chuột hoặc JavaScript giao diện.

## Kết quả chính

| Nhóm | Kết quả |
|---|---|
| Đăng nhập và phân quyền | Đăng nhập đủ các vai trò; chặn khách vào quản trị, kỹ thuật vào báo cáo và kinh doanh vào CSDL; chặn xem hợp đồng của khách khác |
| Danh mục và giỏ hàng | Xem sản phẩm/giá, thêm laptop vào giỏ hàng |
| Điều kiện đặt thuê | Chặn khách có nợ xấu; chặn ngày trả trước ngày nhận |
| Đặt thuê thành công | **HD-0009**, Khách hàng Demo Bình, thuê 7 ngày, **1.190.000đ**, trạng thái chờ duyệt |
| Điều kiện bàn giao | Chặn giao máy khi chưa có chữ ký và hồ sơ cần thiết |
| Bảo trì | **Phiếu #3**, hợp đồng #1 / thiết bị #1; khách báo lỗi, quản trị phân công Kỹ thuật Demo, kỹ thuật cập nhật đang sửa → đã sửa xong |
| Đánh giá | Chặn đánh giá trước khi sửa xong, chặn điểm ngoài 1–5; khách gửi **5 sao** thành công và tải lại vẫn thấy phản hồi |
| Nghiệm thu | Khách xác nhận, phiếu #3 chuyển trạng thái **5 — Đã nghiệm thu & Đóng phiếu** |
| Báo cáo | Lọc theo kỳ, tải Excel hợp lệ, xuất hợp đồng và biên bản bàn giao |
| Sao lưu | Lưu JSON trước/sau; đối chiếu được hợp đồng mới, 5 sao và trạng thái nghiệm thu |
| Dữ liệu đã có | Giữ nguyên HD-0008; không đặt lại CSDL demo |

## Tài khoản dùng cho kịch bản Web

- Đặt thuê mới: **other@demo.invalid**, tên Khách hàng Demo Bình, mật khẩu `Demo@123`.
- Báo lỗi/đánh giá hợp đồng #1: **customer@demo.invalid**, tên Khách hàng Demo An, mật khẩu `Demo@123`.
- Nhân viên: `sale@demo.invalid`, `tech@demo.invalid`, `admin@demo.invalid`; mật khẩu chung `Demo@123`.

Khách hàng Demo An có hợp đồng #4 nợ quá hạn, nên Web chặn đặt thuê mới đúng theo nghiệp vụ. Dùng Demo Bình cho nhánh đặt thuê thành công. Trên Web, 7 ngày thuê là từ D đến D+7; ví dụ 04/11 đến 11/11.

## Tệp kết quả

- `outputs/demo/web-only/result.json`: 38 ca kiểm tra và mã bản ghi được tạo.
- `outputs/demo/web-only/BaoCaoKiemTraWeb.xlsx`: báo cáo tải qua Web.
- `outputs/demo/web-only/hop-dong-web.html`: nội dung hợp đồng mới.
- `outputs/demo/web-only/bao-tri-khach-hang.html`: phiếu khách hàng đã ghi nhận đánh giá.
- `outputs/demo/web-only/backup-before.json`, `backup-after.json`: bản sao lưu đối chiếu. Thư mục `uploads-before` giữ tệp đính kèm trước lượt thử.

Chạy lại bằng `python tools/demo/verify_web.py` khi Web demo đang chạy. Mỗi lần chạy tạo thêm một hợp đồng chờ duyệt và một phiếu bảo trì thử, không xóa dữ liệu cũ. Lần kiểm tra này không thực hiện ký hợp đồng, thu tiền, hoàn cọc hay khôi phục CSDL.
