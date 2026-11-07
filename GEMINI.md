# Project Instructions & UI Design System

## 1. QUY TẮC QUẢN LÝ PHIÊN BẢN (GIT POLICY)
- Chỉ chạy các lệnh git commit, git add, git push khi người dùng yêu cầu hoặc phê duyệt rõ ràng.
- Bảo tồn 100% các bài kiểm thử tự động trong ChallengerTests (luôn giữ toàn bộ bài test PASS).
- Duy trì biên dịch sạch: dotnet build đạt 0 lỗi (0 Errors).
---

## 2. CHUẨN THIẾT KẾ GIAO DIỆN CỔ ĐIỂN DOANH NGHIỆP (EXECUTIVE NAVY & PURE WHITE)
Khi tạo mới hoặc sửa đổi bất kỳ View / Giao diện nào trong dự án này (cả Admin và Client), Agent **BẮT BUỘC** phải tuân thủ nghiêm ngặt các quy tắc sau:

### 2.1. Bảng màu chủ đạo (Color Palette)
- **Màu chủ đạo (Primary)**: Deep Navy `#0f2b5c` (thanh lịch, uy tín, chuẩn mực doanh nghiệp).
- **Màu nhấn (Accent)**: Royal Blue `#1e3a8a` / `#2563eb`.
- **Màu nền (Canvas Background)**: Off-white `#f8fafc`.
- **Màu thẻ & bảng (Card Surface)**: Pure White `#ffffff`.
- **Đường viền (Border)**: Slate `#e2e8f0` (mảnh, tinh tế).
- **Màu chữ chính**: Slate 900 `#0f172a`, chữ phụ `#475569`, chữ mờ `#64748b`.
- **Tuyệt đối cấm**: Sử dụng các màu sắc đối chọi gay gắt, màu neon chói lọi (xanh lá chói, vàng chói, cyan rải rác) trong cùng một màn hình.

### 2.2. Nghiêm cấm sinh các câu mô tả/giới thiệu tính năng thừa thãi
- **TUYỆT ĐỐI KHÔNG** sinh các câu phụ đề rườm rà dưới tiêu đề trang dạng giới thiệu tính năng (ví dụ: *"Cấu hình các voucher giảm giá, tỷ lệ chiết khấu cho khách hàng khi tạo đơn thuê máy."*, *"Theo dõi công nợ toàn hệ thống..."*, *"Điều phối sửa chữa..."*).
- Tiêu đề trang phải súc tích, chuyên nghiệp: Chỉ gồm biểu tượng icon trang nhã và tên chức năng cốt lõi (ví dụ: `Mã Khuyến Mãi`, `Quản Lý Công Nợ`, `Bảo Trì & Sự Cố`, `Đơn Thuê Máy`).

### 2.3. Tối ưu hóa CSS ngữ nghĩa (Semantic Classes - Không gọi chuỗi dài)
Khi viết mã HTML cho view, **TUYỆT ĐỐI KHÔNG** lặp lại các chuỗi utility class dài lê thê của Bootstrap (ví dụ: `card border-0 shadow-sm rounded-3 bg-white p-3`). Thay vào đó, sử dụng các class ngữ nghĩa đã được đóng gói trong `classic-navy.css`:
- **Tiêu đề trang**: `<div class="page-header"><h3 class="page-title"><i class="fas fa-tags"></i> Mã Khuyến Mãi</h3>...</div>`
- **Thẻ chỉ số (KPI / Metric)**:
  ```html
  <div class="stat-card">
      <div class="stat-icon"><i class="fas fa-ticket-alt"></i></div>
      <div>
          <div class="stat-label">Tổng số mã</div>
          <div class="stat-value">@Model.Count()</div>
      </div>
  </div>
  ```
- **Khung chứa bảng**: `<div class="admin-card"><div class="admin-card-header">...</div><div class="table-responsive"><table class="admin-table">...</table></div></div>`
- **Bộ nút hành động trong bảng (Monochrome Slate)**:
  ```html
  <a class="action-btn" title="Tạm dừng"><i class="fas fa-pause"></i></a>
  <a class="action-btn" title="Chỉnh sửa"><i class="fas fa-edit"></i></a>
  <button class="action-btn" title="Xóa"><i class="fas fa-trash-alt"></i></button>
  ```
- **Nút bấm chính & phụ**: `.btn-navy`, `.btn-outline-navy`.
- **Huy hiệu trạng thái (Soft Pastel)**: `.badge-soft-success`, `.badge-soft-warning`, `.badge-soft-danger`, `.badge-soft-navy`.

### 2.4. Thanh Sidebar Quản Trị
- Nền màu Deep Navy `#0f2b5c`.
- Toàn bộ icon menu đồng nhất màu trắng bạc / slate nhạt, **không dùng các class màu neon rải rác** (`text-info`, `text-success`, `text-warning`, `text-primary`, `text-secondary`, `text-danger`).
