# Quản lý lược đồ RentalSystem bằng SQL

`RentalSystemDB_V2` phục vụ Web và API. `RentalSystemDB` giữ dữ liệu tại thời điểm chuyển và chạy với bản build quay lui đã lưu trong `outputs/database-cutover/rollback`.

## Tạo mới và cập nhật

- Bộ SQL chính thức nằm trong `RentalSystem/Database/Sql`. Chạy `001_Baseline.sql` một lần trên CSDL trống với `sqlcmd -b`. File SQL trong MobileApp dẫn tới cùng bộ lệnh. Chạy từ thư mục gốc của dự án và chỉ định CSDL đích bằng `-d`.
- Với bản sao cũ, công cụ chuyển đổi giữ ảnh mặt trước hiện có, điền từ `AnhCMND` khi trường mới trống, giữ mặt sau, đối chiếu lược đồ rồi đăng ký phiên bản 001. Công cụ lưu bằng chứng so sánh theo từng bảng. Bảng lịch sử EF của CSDL cũ nằm trong bản quay lui và bản sao lưu.
- Với thay đổi tiếp theo, thêm script SQL mới theo thứ tự. Mỗi script xác nhận phiên bản trước, cập nhật dữ liệu và ghi phiên bản mới trong cùng giao dịch. Cập nhật `DatabaseSchema.CurrentVersion` cùng bản phát hành. Web kiểm tra phiên bản khi khởi động. Nạp mẫu qua công cụ diễn tập.

## Khởi động và sao lưu

```powershell
dotnet run --project RentalSystem/RentalSystem.csproj
```

Web giữ cổng và địa chỉ API hiện tại. Dữ liệu ảnh dùng thư mục `RentalSystem/wwwroot/uploads`. Cấu hình `Database:BackupDirectory` phải trỏ tới thư mục ngoài webroot mà tài khoản chạy ứng dụng và dịch vụ SQL Server cùng truy cập được. Thư mục sao lưu cục bộ và các bản `.bak` nằm trong `outputs/database-cutover`. Lưu thêm thư mục ảnh khi sao lưu.

Các thao tác `Prepare`, `Reset` và `Verify` chỉ dùng trong giai đoạn diễn tập của V2. Cả công cụ demo lẫn ChallengerTests đều kiểm tra dấu `RentalSystem.Rehearsal`. Khi đưa V2 vào sử dụng, công cụ chuyển đổi gỡ dấu này để chặn nạp mẫu.

## Quay lui

Trước khi quay lui, dừng bản V2. Nếu V2 đã có giao dịch mới, sao lưu V2 và đối soát những thay đổi đó trước khi mở bản cũ cho người dùng. Dữ liệu trong `RentalSystemDB` được giữ ở mốc chuyển đổi.

```powershell
sqlcmd -S localhost -E -C -b -d master -Q "ALTER DATABASE [RentalSystemDB] SET READ_WRITE WITH ROLLBACK IMMEDIATE;"
$oldApp = (Resolve-Path outputs/database-cutover/rollback).Path
$assets = (Resolve-Path RentalSystem/wwwroot).Path
$env:ConnectionStrings__DefaultConnection = 'Server=localhost;Database=RentalSystemDB;Trusted_Connection=True;TrustServerCertificate=True;'
dotnet "$oldApp/RentalSystem.dll" --contentRoot $oldApp --webroot $assets --urls http://localhost:5000
```
