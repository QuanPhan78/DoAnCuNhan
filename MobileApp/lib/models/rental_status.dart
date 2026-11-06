enum RentalStatus {
  pending,
  confirmed,
  preparing,
  delivering,
  installed,
  renting,
  cancellationRequested,
  returnedPendingSettlement,
  completed,
  rejected,
  cancelled,
  unknown;

  static RentalStatus fromApi(int? code, {bool cancellationRequested = false}) =>
      switch (code) {
        0 when cancellationRequested => RentalStatus.cancellationRequested,
        0 => RentalStatus.pending,
        1 => RentalStatus.renting,
        2 => RentalStatus.completed,
        3 => RentalStatus.cancelled,
        4 => RentalStatus.returnedPendingSettlement,
        _ => RentalStatus.unknown,
      };
}

extension RentalStatusExtension on RentalStatus {
  String get displayName {
    switch (this) {
      case RentalStatus.pending:
        return 'Chờ duyệt';
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
      case RentalStatus.cancellationRequested:
        return 'Yêu cầu hủy';
      case RentalStatus.returnedPendingSettlement:
        return 'Đã trả máy (Chờ quyết toán)';
      case RentalStatus.completed:
        return 'Hoàn thành';
      case RentalStatus.rejected:
        return 'Từ chối';
      case RentalStatus.cancelled:
        return 'Đã hủy';
      case RentalStatus.unknown:
        return 'Chưa xác định';
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
      case RentalStatus.returnedPendingSettlement: return 6;
      case RentalStatus.completed: return 7;
      case RentalStatus.cancellationRequested:
      case RentalStatus.unknown:
      case RentalStatus.rejected: return -1;
      case RentalStatus.cancelled: return -1;
    }
  }
}
