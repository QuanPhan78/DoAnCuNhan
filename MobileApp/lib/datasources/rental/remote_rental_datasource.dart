import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../models/rental_request_model.dart';
import '../../models/rental_status.dart';
import 'rental_datasource.dart';

class RemoteRentalDataSource implements RentalDataSource {
  final String baseUrl;

  RemoteRentalDataSource({this.baseUrl = 'http://10.0.2.2:5000/api'});

  @override
  Future<List<RentalRequestModel>> getRentals({String? userId}) async {
    try {
      final url = Uri.parse('$baseUrl/contracts${userId != null ? '?userId=$userId' : ''}');
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        return data.map((jsonItem) {
          final statusCode = jsonItem['statusCode'] as int? ?? 0;
          RentalStatus status;
          switch (statusCode) {
            case 0:
              status = RentalStatus.pending;
              break;
            case 1:
              status = RentalStatus.renting;
              break;
            case 2:
              status = RentalStatus.completed;
              break;
            case 3:
              status = RentalStatus.cancelled;
              break;
            default:
              status = RentalStatus.pending;
          }

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

  @override
  Future<RentalRequestModel> createRental(RentalRequestModel request) async {
    final url = Uri.parse('$baseUrl/contracts');
    try {
      final firstItem = request.items.isNotEmpty ? request.items.first : null;
      final payload = {
        'customerId': request.customerId,
        'deviceId': firstItem?.deviceId ?? '1',
        'quantity': firstItem?.quantity ?? 1,
        'rentalType': request.rentalType,
        'startDate': request.startDate.toIso8601String(),
        'endDate': request.endDate.toIso8601String(),
        'deliveryAddress': request.deliveryAddress,
        'note': request.note,
        'estimatedAmount': request.estimatedAmount,
        'rentalPrice': firstItem?.rentalPrice,
        'installmentCount': 1,
        'items': request.items.map((i) => {
          'deviceId': i.deviceId,
          'deviceName': i.deviceName,
          'quantity': i.quantity,
          'rentalPrice': i.rentalPrice,
          'subtotal': i.subtotal,
        }).toList(),
      };

      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(payload),
      );

      final data = json.decode(utf8.decode(response.bodyBytes));
      if (response.statusCode >= 200 && response.statusCode < 300 && data['success'] == true) {
        return request.copyWith(
          id: data['contractId']?.toString() ?? request.id,
          contractId: data['contractCode'] ?? 'HD-${data['contractId']}',
          status: RentalStatus.pending,
        );
      } else {
        final message = data['message'] ?? 'Không thể tạo hợp đồng (${response.statusCode})';
        throw Exception(message);
      }
    } catch (e) {
      if (e is Exception) rethrow;
      throw Exception('Lỗi kết nối máy chủ: $e');
    }
  }

  @override
  Future<bool> cancelRental(String id) async {
    try {
      final url = Uri.parse('$baseUrl/contracts/$id/cancel');
      final response = await http.put(url);
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
