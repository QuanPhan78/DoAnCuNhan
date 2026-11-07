import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:quan_ly_cho_thue_thiet_bi/datasources/rental/remote_rental_datasource.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/rental_request_model.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/rental_status.dart';
import 'package:quan_ly_cho_thue_thiet_bi/services/api_session.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('Mobile sends a cancellation request and distinguishes lifecycle states', () async {
    SharedPreferences.setMockInitialValues({
      ApiSession.tokenKey: jsonEncode({
        'accessToken': 'rs1.lifecycle-fixture',
        'expiresIn': DateTime.now().add(const Duration(hours: 1)).toIso8601String(),
      }),
    });
    await http.runWithClient(() async {
      final source = RemoteRentalDataSource(baseUrl: 'https://test.invalid/api');
      await source.requestCancellation('42', 'Đổi kế hoạch');
      final rentals = await source.getRentals();
      expect(rentals.map((rental) => rental.status), [
        RentalStatus.cancellationRequested,
        RentalStatus.cancelled,
        RentalStatus.returnedPendingSettlement,
        RentalStatus.completed,
      ]);
      expect(rentals.first.cancellationReason, 'Đổi kế hoạch');
    }, () => MockClient((request) async {
      if (request.method == 'POST') {
        expect(request.url.path, '/api/contracts/42/cancellation-request');
        expect(jsonDecode(utf8.decode(request.bodyBytes)), {'reason': 'Đổi kế hoạch'});
        return http.Response('{"success":true,"cancellationRequested":true}', 200);
      }
      expect(request.url.path, '/api/contracts');
      return http.Response.bytes(utf8.encode(jsonEncode([
        {'id': '42', 'statusCode': 0, 'cancellationRequested': true,
         'cancellationReason': 'Đổi kế hoạch'},
        {'id': '43', 'statusCode': 3},
        {'id': '44', 'statusCode': 4},
        {'id': '45', 'statusCode': 2},
      ])), 200);
    }));
  });

  test('Mobile confirms the server quote and submits only order inputs', () async {
    SharedPreferences.setMockInitialValues({
      ApiSession.tokenKey: jsonEncode({
        'accessToken': 'rs1.booking-fixture',
        'expiresIn': DateTime.now().add(const Duration(hours: 1)).toIso8601String(),
      }),
    });
    final request = RentalRequestModel(
      id: 'local',
      customerId: '2',
      items: [RentalRequestItem(deviceId: '1', deviceName: 'Cached name',
          quantity: 1, rentalPrice: 123, subtotal: 123)],
      rentalType: 'Theo tháng',
      startDate: DateTime(2026, 11, 7, 16),
      endDate: DateTime(2026, 11, 14, 9),
      deliveryAddress: 'Địa chỉ thử',
      note: '',
      promoCode: 'DEMO20',
      estimatedAmount: 123,
      status: RentalStatus.pending,
      createdAt: DateTime(2026, 11, 7),
    );
    final paths = <String>[];
    await http.runWithClient(() async {
      final source = RemoteRentalDataSource(baseUrl: 'https://test.invalid/api');
      final quote = await source.quoteRental(request);
      expect(quote.rentalDays, 7);
      expect(quote.items.single.rentalPrice, 170000);
      expect(quote.estimatedAmount, 952000);
      expect(quote.discountAmount, 238000);
      final saved = await source.createRental(quote);
      expect(saved.id, '42');
      expect(saved.estimatedAmount, 952000);
      expect(paths, ['/api/contracts/quote', '/api/contracts']);
    }, () => MockClient((request) async {
      paths.add(request.url.path);
      final body = jsonDecode(request.body) as Map<String, dynamic>;
      expect(body['startDate'], '2026-11-07');
      expect(body['endDate'], '2026-11-14');
      expect(body['promoCode'], 'DEMO20');
      expect(body['items'], [{'productId': 1, 'quantity': 1}]);
      expect(body.keys, isNot(contains('estimatedAmount')));
      expect(body.keys, isNot(contains('rentalType')));
      if (request.url.path.endsWith('/quote')) {
        return http.Response(jsonEncode({
          'rentalDays': 7, 'totalAmount': 952000,
          'discountAmount': 238000, 'promoCode': 'DEMO20',
          'items': [{'productId': 1, 'productName': 'Laptop', 'quantity': 1,
              'dailyPrice': 170000, 'subtotal': 1190000}],
        }), 200);
      }
      expect(body['expectedTotal'], 952000);
      return http.Response(jsonEncode({
        'success': true, 'contractId': '42', 'contractCode': 'HD-0042',
        'customerId': '2', 'rentalDays': 7, 'totalAmount': 952000,
        'discountAmount': 238000,
      }), 200);
    }));
  });
}
