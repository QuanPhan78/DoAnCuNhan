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

  static Role fromString(String role) {
    switch (role) {
      case 'Khách hàng': return Role.customer;
      case 'Nhân viên': return Role.staff;
      case 'Quản lý': return Role.admin;
      default: return Role.customer;
    }
  }
}