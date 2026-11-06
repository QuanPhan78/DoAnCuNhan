enum RentalStatus {
  pending,
  confirmed,
  preparing,
  delivering,
  installed,
  renting,
  completed,
  rejected,
  cancelled,
}

extension RentalStatusExtension on RentalStatus {
  String get displayName {
    switch (this) {
      case RentalStatus.pending:
        return 'Chờ xác nhận';
      case RentalStatus.confirmed:
        return 'Đã xác nhận';
      case RentalStatus.preparing:
        return 'Đang chuẩn bị';
      case RentalStatus.delivering:
        return 'Đang giao';
      case RentalStatus.installed:
        return 'Đã lắp đặt / Đã bàn giao';
      case RentalStatus.renting:
        return 'Đang thuê';
      case RentalStatus.completed:
        return 'Hoàn thành';
      case RentalStatus.rejected:
        return 'Từ chối';
      case RentalStatus.cancelled:
        return 'Đã hủy';
    }
  }

  // Tiện ích để sắp xếp thứ tự trên Timeline
  int get stepIndex {
    switch (this) {
      case RentalStatus.pending: return 0;
      case RentalStatus.confirmed: return 1;
      case RentalStatus.preparing: return 2;
      case RentalStatus.delivering: return 3;
      case RentalStatus.installed: return 4;
      case RentalStatus.renting: return 5;
      case RentalStatus.completed: return 6;
      case RentalStatus.rejected: return -1;
      case RentalStatus.cancelled: return -1;
    }
  }
}
