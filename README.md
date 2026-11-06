# DoAnCuNhan

## Demo bảo vệ khóa luận

Bộ demo 10–12 phút gồm Web, Android thật, dữ liệu giả lập riêng, kịch bản nói, bảng nhắc A4 và công cụ diễn tập.

- [Hướng dẫn chạy và dữ liệu demo](docs/demo/README.md)
- [Kịch bản trình bày 11 phút 30 giây](docs/demo/KICH_BAN.md)
- [Bảng nhắc một trang để in](docs/demo/BANG_NHAC.html)

Chạy Web/API bằng `dotnet run --project RentalSystem/RentalSystem.csproj`. Xem [quy trình SQL, sao lưu và quay lui](docs/database-cutover.md). Công cụ demo chỉ nạp mẫu khi V2 được đánh dấu diễn tập.

Để thử thanh toán VNPAY, đặt `Vnpay:TmnCode` và `Vnpay:HashSecret` trong .NET User Secrets của dự án Web ở môi trường Development hoặc dùng các biến môi trường `Vnpay__TmnCode` và `Vnpay__HashSecret`.
