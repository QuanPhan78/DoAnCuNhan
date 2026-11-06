# Chạy thử Web và Redmi Note 12 Pro — 04/11/2026

- Backend đang dùng `RentalSystemDemoDB`, Web tại `http://localhost:5000`.
- Điện thoại Android 13 đã được ADB nhận; APK demo cài thành công sau khi người dùng cho phép cài qua USB.
- API được nối bằng `adb reverse tcp:5000 tcp:5000`. scrcpy chiếu được màn hình; Xiaomi chưa cấp quyền điều khiển INJECT_EVENTS nên người dùng thao tác trực tiếp trên điện thoại.
- Người dùng đăng nhập khách hàng demo và tạo **HD-0008** từ điện thoại. Đơn đã xuất hiện trên giao diện Web quản trị, đúng khách hàng Demo An, thiết bị laptop, thời gian 04–10/11, trạng thái chờ duyệt, số tiền **1.020.000đ**, chưa thu cọc.
- Đã tạo phiếu sự cố **#2** trên Web khách hàng cho hợp đồng #1 / DEMO-LAP-001; Web quản trị phân công Kỹ thuật Demo, cập nhật đang sửa và đã sửa xong; chi phí 0đ.
- Minh chứng ảnh nằm trong `outputs/demo/live-test/`.

## Vấn đề phát hiện khi chạy trên điện thoại

Hướng dẫn cũ dự kiến 1.190.000đ cho 04–10/11 chưa khớp hành vi thực tế. Ngày bắt đầu lưu là `2026-11-04T10:22:03.4346660`, ngày kết thúc `2026-11-10T00:00:00`; `RentalService` dùng `difference().inDays` rồi cộng 1 nên ra 6 ngày, tương ứng 1.020.000đ. Khi chọn lại ngày bắt đầu về 00:00, cùng khoảng ngày có thể cho kết quả khác.

Đây là điểm chưa thống nhất giữa cách tính ngày trên Mobile và cách biểu diễn số ngày trên Web. Chưa sửa quy tắc tính phí và chưa sửa số tiền của HD-0008 trong lần chạy này. Không dùng kịch bản “chắc chắn 7 ngày = 1.190.000đ với D đến D+6” cho đến khi chuẩn hóa cách tính ngày và kiểm chứng lại trên thiết bị thật.

Kết quả chiều Web → điện thoại và đánh giá sẽ được ghi trong `outputs/demo/live-test/result.json` sau khi người dùng hoàn tất thao tác trên điện thoại. Lần chạy phối hợp này chưa được tính là một lượt tập độc lập có bấm giờ.
