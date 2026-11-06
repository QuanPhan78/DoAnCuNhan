import 'dart:convert';
import '../../services/api_session.dart';
import '../../models/rental_request_model.dart';
import '../../models/rental_status.dart';
import '../../services/api_config.dart';
import 'rental_datasource.dart';

class RemoteRentalDataSource implements RentalDataSource {
  final String? _baseUrl;
  String get baseUrl => _baseUrl ?? ApiConfig.baseUrl;

  RemoteRentalDataSource({String? baseUrl}) : _baseUrl = baseUrl;

  @override
  Future<List<RentalRequestModel>> getRentals({String? userId}) async {
    try {
      final url = Uri.parse('$baseUrl/contracts');
      final response = await ApiSession.get(url);

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        return data.map((jsonItem) {
          final status = RentalStatus.fromApi(
            (jsonItem['statusCode'] as num?)?.toInt(),
            cancellationRequested: jsonItem['cancellationRequested'] == true,
          );

          final deviceNames = (jsonItem['deviceIds'] as List<dynamic>?)
                  ?.map((e) => e.toString())
                  .toList() ??
              [];
          final mainDeviceName =
              deviceNames.isNotEmpty ? deviceNames.first : 'Thiết bị thuê';

          DateTime start = DateTime.now();
          DateTime end = DateTime.now().add(const Duration(days: 1));

          try {
            if (jsonItem['createdAt'] != null) {
              start = DateTime.parse(jsonItem['createdAt']);
            }
          } catch (_) {}

          return RentalRequestModel(
            id: jsonItem['id']?.toString() ?? '',
            customerId: jsonItem['customerId']?.toString() ?? '',
            contractId: jsonItem['contractCode'] ?? 'HD-${jsonItem['id']}',
            items: [
              RentalRequestItem(
                deviceId: jsonItem['id']?.toString() ?? '1',
                deviceName: mainDeviceName,
                quantity: 1,
                rentalPrice: (jsonItem['totalAmount'] as num?)?.toDouble() ?? 0,
                subtotal: (jsonItem['totalAmount'] as num?)?.toDouble() ?? 0,
              )
            ],
            rentalType: jsonItem['rentalType'] ?? 'Theo ngày',
            startDate: start,
            endDate: end,
            deliveryAddress: jsonItem['note'] ?? '',
            note: jsonItem['note'] ?? '',
            estimatedAmount: (jsonItem['totalAmount'] as num?)?.toDouble() ?? 0,
            status: status,
            cancellationReason: jsonItem['cancellationReason'],
            createdAt: start,
          );
        }).toList();
      } else {
        throw Exception('Không thể tải danh sách đơn thuê (${response.statusCode})');
      }
    } catch (e) {
      if (e is Exception) rethrow;
      throw Exception('Lỗi kết nối máy chủ: $e');
    }
  }

  Map<String, dynamic> _payload(RentalRequestModel request) {
    String date(DateTime value) =>
        DateTime.utc(value.year, value.month, value.day).toIso8601String().split('T').first;
    return {
      'startDate': date(request.startDate),
      'endDate': date(request.endDate),
      'deliveryAddress': request.deliveryAddress,
      'note': request.note,
      'promoCode': request.promoCode,
      'items': request.items.map((item) => {
        'productId': int.tryParse(item.deviceId),
        'quantity': item.quantity,
      }).toList(),
    };
  }

  @override
  Future<RentalRequestModel> quoteRental(RentalRequestModel request) async {
    final response = await ApiSession.post(
      Uri.parse('$baseUrl/contracts/quote'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(_payload(request)),
    );
    final data = jsonDecode(utf8.decode(response.bodyBytes));
    if (response.statusCode != 200) {
      throw Exception(data['message'] ?? 'Không thể báo giá đơn thuê.');
    }

    final items = (data['items'] as List<dynamic>).map((item) {
      final id = item['productId'].toString();
      final original = request.items.firstWhere((line) => int.tryParse(line.deviceId) == item['productId']);
      return RentalRequestItem(
        deviceId: id,
        deviceName: item['productName'],
        imageUrl: original.imageUrl,
        quantity: item['quantity'],
        rentalPrice: (item['dailyPrice'] as num).toDouble(),
        subtotal: (item['subtotal'] as num).toDouble(),
      );
    }).toList();
    return request.copyWith(
      items: items,
      rentalDays: data['rentalDays'],
      estimatedAmount: (data['totalAmount'] as num).toDouble(),
      discountAmount: (data['discountAmount'] as num).toDouble(),
      promoCode: data['promoCode'],
    );
  }

  @override
  Future<RentalRequestModel> createRental(RentalRequestModel request) async {
    final response = await ApiSession.post(
      Uri.parse('$baseUrl/contracts'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        ..._payload(request),
        if (request.rentalDays != null) 'expectedTotal': request.estimatedAmount,
      }),
    );
    final data = jsonDecode(utf8.decode(response.bodyBytes));
    if (response.statusCode != 200 || data['success'] != true) {
      throw Exception(data['message'] ?? 'Không thể tạo hợp đồng.');
    }

    return request.copyWith(
      id: data['contractId']?.toString(),
      contractId: data['contractCode'],
      customerId: data['customerId']?.toString(),
      estimatedAmount: (data['totalAmount'] as num).toDouble(),
      rentalDays: data['rentalDays'],
      discountAmount: (data['discountAmount'] as num).toDouble(),
      status: RentalStatus.pending,
    );
  }

  @override
  Future<void> requestCancellation(String id, String reason) async {
    final response = await ApiSession.post(
      Uri.parse('$baseUrl/contracts/$id/cancellation-request'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'reason': reason}),
    );
    final data = jsonDecode(utf8.decode(response.bodyBytes));
    if (response.statusCode != 200 || data['cancellationRequested'] != true) {
      throw Exception(data['message'] ?? 'Không thể gửi yêu cầu hủy.');
    }
  }
}
