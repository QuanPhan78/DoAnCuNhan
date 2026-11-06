class AppTranslations {
  static const Map<String, String> en = {
    // Navigation & Main
    'Trang chủ': 'Home',
    'Thiết bị': 'Devices',
    'Hợp đồng': 'Contracts',
    'Công việc': 'Tasks',
    'Bảo trì': 'Maintenance',
    'Thông báo': 'Notifications',
    'Tài khoản': 'Account',
    'Yêu cầu': 'Requests',
    'Báo cáo': 'Reports',
    'Hệ Thống Quản Lý': 'Management System',
    'Xin chào,': 'Hello,',
    
    // Customer Dashboard
    'Tổng quan hợp đồng': 'Contract Overview',
    'Đang thuê': 'Active Rentals',
    'Sắp hết hạn': 'Expiring Soon',
    'Yêu cầu bảo trì đang xử lý': 'Ongoing Maintenance',
    'Thao tác nhanh': 'Quick Actions',
    'Báo sự cố': 'Report Issue',
    'Phản hồi': 'Feedback',
    'Khuyến mãi': 'Promotions',
    'Khuyến mãi & Thông báo': 'Promotions & Alerts',
    'Chưa có thông báo nào mới.': 'No new announcements.',

    // Staff Dashboard
    'Công việc của tôi': 'My Tasks',
    'Được giao': 'Assigned',
    'Đang chờ': 'Pending',
    'Đang xử lý': 'In Progress',
    'Hoàn thành': 'Completed',
    'Nhiệm vụ & Chức năng': 'Operations & Tasks',
    'Sự cố': 'Incidents',

    // Admin Dashboard
    'Tổng quan kinh doanh': 'Business Overview',
    'Thiết bị (Tổng)': 'Total Devices',
    'Đang cho thuê': 'Currently Rented',
    'Tổng hợp đồng': 'Total Contracts',
    'Bảo trì (Tồn đọng)': 'Pending Maintenance',
    'Công việc đang xử lý': 'Tasks in Progress',
    'Quản lý vận hành': 'Operations Management',

    // Account & Settings
    'Thông tin cá nhân': 'Profile Info',
    'Cài đặt hệ thống': 'System Settings',
    'Bảo mật & Phân quyền': 'Security & Permissions',
    'Đăng xuất': 'Log Out',
    'Thông báo đẩy': 'Push Notifications',
    'Nhận tin báo hợp đồng và thiết bị': 'Receive alerts on contracts & devices',
    'Thông báo qua Email': 'Email Notifications',
    'Nhận bản sao hợp đồng và hóa đơn': 'Receive contract copies & invoices',
    'Âm thanh thông báo': 'Notification Sound',
    'Giao diện & Ngôn ngữ': 'Appearance & Language',
    'Ngôn ngữ': 'Language',
    'Chế độ hiển thị': 'Theme Mode',
    'Giao diện Sáng': 'Light Mode',
    'Giao diện Tối': 'Dark Mode',
    'Theo hệ thống': 'System Default',
    'Dữ liệu & Ứng dụng': 'Data & Application',
    'Phiên bản ứng dụng': 'App Version',
    'Mới nhất': 'Latest',
    'Bảo mật tài khoản': 'Account Security',
    'Đổi mật khẩu': 'Change Password',
    'Cập nhật mật khẩu định kỳ để bảo vệ tài khoản': 'Update password regularly for security',
    'Xác thực 2 yếu tố (2FA)': 'Two-Factor Authentication (2FA)',
    'Chưa kích hoạt': 'Not Enabled',
    'Kích hoạt': 'Enable',
    'Quyền hạn của bạn': 'Your Permissions',
    'Mã người dùng': 'User ID',
    'Họ và tên': 'Full Name',
    'Email': 'Email',
    'Vai trò tài khoản': 'Account Role',
    'Trạng thái hoạt động': 'Account Status',
    'Đang hoạt động': 'Active',
    'Chỉnh sửa thông tin': 'Edit Profile',

    // Common Buttons & Dialogs
    'Chọn ngôn ngữ': 'Select Language',
    'Chọn chế độ hiển thị': 'Select Theme Mode',
    'Đóng': 'Close',
    'Hủy': 'Cancel',
    'Lưu': 'Save',
    'Cập nhật': 'Update',
    'Mặc định': 'Default',
    'Đang chọn': 'Selected',
    'Tất cả': 'All',
    'Tìm kiếm': 'Search',
    'Đơn giá:': 'Rate:',
    'ngày': 'day',
    'Mô tả': 'Description',
    'Thông số kỹ thuật': 'Specifications',
    'Thông tin thuê': 'Rental Info',
    'Thuê ngay': 'Rent Now',
    'Không khả dụng': 'Unavailable',
    'Sẵn sàng': 'Available',
    'Vai trò': 'Role',
    'Vai trò:': 'Role:',
    'Test truy cập Báo Cáo': 'Test Reports Access',
    'Đã chọn ngôn ngữ: Tiếng Việt': 'Language selected: Vietnamese',
    'Đã chọn: Theo hệ thống': 'Selected: System Default',
    'Đã chuyển sang: Giao diện Tối': 'Switched to: Dark Mode',
    'Đã chuyển sang: Giao diện Sáng': 'Switched to: Light Mode',
  };

  static String tr(String key, String lang) {
    if (lang == 'en') {
      return en[key] ?? key;
    }
    return key;
  }
}
