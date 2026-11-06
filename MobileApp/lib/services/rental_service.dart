class RentalService {
  static double calculateEstimatedCost({
    required double devicePrice,
    required String rentalType,
    required int quantity,
    required DateTime startDate,
    required DateTime endDate,
  }) {
    int days = endDate.difference(startDate).inDays;
    if (days < 0) return 0;
    // Đảm bảo thuê ít nhất 1 ngày nếu ngày kết thúc = ngày bắt đầu
    if (days == 0) {
      days = 1;
    } else {
      // Nếu thuê từ sáng hôm nay đến sáng ngày mai, difference là 1 ngày.
      // Nhưng theo nghiệp vụ thuê thường tính bao gồm cả ngày bắt đầu và kết thúc?
      // Tạm thời tính theo số ngày = difference + 1
      days += 1;
    }

    double multiplier = 1.0;
    if (rentalType == 'Theo tháng') {
      multiplier = 0.8; // Giảm giá 20%
    } else if (rentalType == 'Dài hạn') {
      multiplier = 0.7; // Giảm giá 30%
    }

    return devicePrice * quantity * days * multiplier;
  }
}
