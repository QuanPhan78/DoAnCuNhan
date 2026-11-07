class RentalService {
  static int rentalDays(DateTime startDate, DateTime endDate) {
    final start = DateTime.utc(startDate.year, startDate.month, startDate.day);
    final end = DateTime.utc(endDate.year, endDate.month, endDate.day);
    final days = end.difference(start).inDays;
    if (days < 0) throw ArgumentError('Ngày trả phải từ ngày nhận trở đi.');
    return days == 0 ? 1 : days;
  }
}
