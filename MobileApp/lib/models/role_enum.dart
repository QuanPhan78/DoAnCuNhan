enum Role {
  customer,
  staff,
  admin,
  unavailable
}

extension RoleExtension on Role {
  String get displayName {
    switch (this) {
      case Role.customer: return 'Khách hàng';
      case Role.staff: return 'Kỹ thuật';
      case Role.admin: return 'Quản lý';
      case Role.unavailable: return 'Chỉ dùng trên Web';
    }
  }

  static Role fromString(String? role) {
    final r = role?.trim().toLowerCase();
    if (r == 'khachhang' || r == 'khách hàng' || r == 'customer') return Role.customer;
    if (r == 'kythuat' || r == 'kỹ thuật' || r == 'staff') return Role.staff;
    if (r == 'admin' || r == 'quản lý' || r == 'quanly') return Role.admin;
    return Role.unavailable;
  }
}
