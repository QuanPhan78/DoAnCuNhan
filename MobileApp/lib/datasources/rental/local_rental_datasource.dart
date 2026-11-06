import '../../services/rental_service.dart';
import '../../models/rental_request_model.dart';
import '../../models/rental_status.dart';
import 'rental_datasource.dart';

class LocalRentalDataSource implements RentalDataSource {
  final List<RentalRequestModel> _rentals = [
    RentalRequestModel(
      id: 'RNT-001',
      customerId: 'user123',
      items: [RentalRequestItem(deviceId: 'dev1', deviceName: 'Thiết bị A', quantity: 1, rentalPrice: 500000, subtotal: 500000)],
      rentalType: 'Theo ngày',
      startDate: DateTime.now(),
      endDate: DateTime.now().add(const Duration(days: 1)),
      deliveryAddress: 'Địa chỉ 1',
      note: '',
      estimatedAmount: 500000,
      status: RentalStatus.pending,
      createdAt: DateTime.now(),
    ),
    RentalRequestModel(
      id: 'RNT-002',
      customerId: 'user123',
      items: [RentalRequestItem(deviceId: 'dev2', deviceName: 'Thiết bị B', quantity: 2, rentalPrice: 300000, subtotal: 600000)],
      rentalType: 'Theo tuần',
      startDate: DateTime.now().subtract(const Duration(days: 2)),
      endDate: DateTime.now().add(const Duration(days: 5)),
      deliveryAddress: 'Địa chỉ 2',
      note: '',
      estimatedAmount: 4200000,
      status: RentalStatus.confirmed,
      contractId: 'HD-001',
      createdAt: DateTime.now().subtract(const Duration(days: 3)),
    ),
    RentalRequestModel(
      id: 'RNT-003',
      customerId: 'user123',
      items: [RentalRequestItem(deviceId: 'dev3', deviceName: 'Thiết bị C', quantity: 1, rentalPrice: 1000000, subtotal: 1000000)],
      rentalType: 'Theo tháng',
      startDate: DateTime.now(),
      endDate: DateTime.now().add(const Duration(days: 30)),
      deliveryAddress: 'Địa chỉ 3',
      note: '',
      estimatedAmount: 24000000, // 30 * 1tr * 0.8
      status: RentalStatus.preparing,
      createdAt: DateTime.now().subtract(const Duration(days: 1)),
    ),
    RentalRequestModel(
      id: 'RNT-004',
      customerId: 'user123',
      items: [RentalRequestItem(deviceId: 'dev4', deviceName: 'Thiết bị D', quantity: 1, rentalPrice: 200000, subtotal: 200000)],
      rentalType: 'Theo ngày',
      startDate: DateTime.now(),
      endDate: DateTime.now().add(const Duration(days: 2)),
      deliveryAddress: 'Địa chỉ 4',
      note: '',
      estimatedAmount: 600000,
      status: RentalStatus.delivering,
      createdAt: DateTime.now().subtract(const Duration(hours: 10)),
    ),
    RentalRequestModel(
      id: 'RNT-005',
      customerId: 'user123',
      items: [RentalRequestItem(deviceId: 'dev5', deviceName: 'Thiết bị E', quantity: 1, rentalPrice: 150000, subtotal: 150000)],
      rentalType: 'Theo ngày',
      startDate: DateTime.now().subtract(const Duration(days: 5)),
      endDate: DateTime.now().add(const Duration(days: 5)),
      deliveryAddress: 'Địa chỉ 5',
      note: '',
      estimatedAmount: 1500000,
      status: RentalStatus.renting,
      contractId: 'HD-002',
      createdAt: DateTime.now().subtract(const Duration(days: 6)),
    ),
    RentalRequestModel(
      id: 'RNT-006',
      customerId: 'user123',
      items: [RentalRequestItem(deviceId: 'dev6', deviceName: 'Thiết bị F', quantity: 1, rentalPrice: 400000, subtotal: 400000)],
      rentalType: 'Theo ngày',
      startDate: DateTime.now().subtract(const Duration(days: 10)),
      endDate: DateTime.now().subtract(const Duration(days: 1)),
      deliveryAddress: 'Địa chỉ 6',
      note: '',
      estimatedAmount: 4000000,
      status: RentalStatus.completed,
      contractId: 'HD-003',
      createdAt: DateTime.now().subtract(const Duration(days: 11)),
    ),
    RentalRequestModel(
      id: 'RNT-007',
      customerId: 'user123',
      items: [RentalRequestItem(deviceId: 'dev7', deviceName: 'Thiết bị G', quantity: 1, rentalPrice: 800000, subtotal: 800000)],
      rentalType: 'Theo ngày',
      startDate: DateTime.now().add(const Duration(days: 1)),
      endDate: DateTime.now().add(const Duration(days: 2)),
      deliveryAddress: 'Địa chỉ 7',
      note: '',
      estimatedAmount: 1600000,
      status: RentalStatus.cancelled,
      createdAt: DateTime.now().subtract(const Duration(hours: 2)),
    ),
  ];

  @override
  Future<List<RentalRequestModel>> getRentals({String? userId}) async {
    await Future.delayed(const Duration(milliseconds: 500));
    return List.from(_rentals);
  }

  @override
  Future<RentalRequestModel> quoteRental(RentalRequestModel request) async {
    if (request.promoCode?.trim().isNotEmpty == true) {
      throw Exception('Cần kết nối máy chủ để áp dụng mã khuyến mãi.');
    }
    final days = RentalService.rentalDays(request.startDate, request.endDate);
    return request.copyWith(
      rentalDays: days,
      estimatedAmount: request.items.fold<double>(
        0, (total, item) => total + item.rentalPrice * item.quantity * days,
      ),
    );
  }

  @override
  Future<RentalRequestModel> createRental(RentalRequestModel request) async {
    await Future.delayed(const Duration(milliseconds: 500));
    _rentals.insert(0, request);
    return request;
  }

  @override
  Future<void> requestCancellation(String id, String reason) async {
    final index = _rentals.indexWhere((request) => request.id == id);
    if (index == -1 || _rentals[index].status != RentalStatus.pending) {
      throw Exception('Chỉ có thể yêu cầu hủy đơn chờ duyệt.');
    }
    _rentals[index] = _rentals[index].copyWith(
      status: RentalStatus.cancellationRequested,
      cancellationReason: reason,
    );
  }
}
