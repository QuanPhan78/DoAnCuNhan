enum Role {
  customer,
  staff,
  admin
}

extension RoleExtension on Role {
  String get name {
    switch (this) {
      case Role.customer: return 'Khách hàng';
      case Role.staff: return 'Nhân viên';
      case Role.admin: return 'Quản lý';
    }
  }

  static Role fromString(String? role) {
    if (role == null) return Role.customer;
    final r = role.trim().toLowerCase();
    if (r == 'admin' || r == 'quản lý' || r == 'quanly' || r == 'quản trị viên') {
      return Role.admin;
    }
    if (r == 'nhân viên' || r == 'nhanvien' || r == 'staff' || r == 'kinhdoanh' || r == 'kythuat') {
      return Role.staff;
    }
    return Role.customer;
  }
}