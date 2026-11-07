import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:quan_ly_cho_thue_thiet_bi/datasources/remote/remote_auth_datasource.dart';
import 'package:quan_ly_cho_thue_thiet_bi/datasources/renewal/remote_renewal_datasource.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/device_model.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/renewal_model.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/role_enum.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/user_model.dart';
import 'package:quan_ly_cho_thue_thiet_bi/providers/cart_provider.dart';
import 'package:quan_ly_cho_thue_thiet_bi/screens/contracts/debt_screen.dart';
import 'package:quan_ly_cho_thue_thiet_bi/services/api_session.dart';
import 'package:quan_ly_cho_thue_thiet_bi/services/customer_contract_service.dart';
import 'package:quan_ly_cho_thue_thiet_bi/widgets/photo_field.dart';
import 'package:quan_ly_cho_thue_thiet_bi/widgets/signature_pad.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  setUp(() {
    SharedPreferences.setMockInitialValues({ApiSession.tokenKey: jsonEncode({
      'accessToken': 'rs1.parity-fixture', 'expiresIn': DateTime.now().add(const Duration(hours: 1)).toIso8601String(),
    })});
  });

  test('Canonical server role takes precedence over the common employee display label', () {
    expect(UserModel.fromJson({'id': 1, 'roleCode': 'KyThuat', 'role': 'Nhân viên'}).role, Role.staff);
    expect(UserModel.fromJson({'id': 2, 'roleCode': 'KinhDoanh', 'role': 'Nhân viên'}).role, Role.unavailable);
    expect(UserModel.fromJson({'id': 3, 'roleCode': 'Unknown', 'role': 'Khách hàng'}).role, Role.unavailable);
    final restored = UserModel.fromJson(UserModel(id: '1', name: 'Tech', email: '', role: Role.staff).toJson());
    expect(restored.role, Role.staff);
    expect(restored.role.displayName, 'Kỹ thuật');
  });

  test('Business and administrator accounts receive a Web-only message before saving a session', () async {
    for (final role in ['KinhDoanh', 'Admin']) {
      await http.runWithClient(() async {
        await expectLater(RemoteAuthDataSource().login('fixture@example.invalid', 'fixture'),
          throwsA(predicate((e) => e.toString().contains('vui lòng sử dụng Web'))));
      }, () => MockClient((_) async => http.Response(jsonEncode({'user': {'id': '1', 'roleCode': role}}), 200)));
    }
  });

  test('Cart supports multiple products and cannot cross account boundaries', () {
    final cart = CartProvider()..setOwner('customer-a');
    final laptop = DeviceModel(id: '1', name: 'Laptop', type: 'Laptop');
    final monitor = DeviceModel(id: '2', name: 'Monitor', type: 'Monitor');
    cart.add(laptop); cart.add(monitor); cart.add(laptop);
    expect(cart.count, 3); expect(cart.lines.length, 2);
    cart.setOwner('customer-a'); expect(cart.count, 3);
    cart.change('1', 1); expect(cart.count, 2);
    cart.setOwner('customer-b'); expect(cart.lines, isEmpty);
  });

  test('Renewal uses numeric days and preserves the server conflict message', () async {
    await http.runWithClient(() async {
      final request = RenewalModel(id: '', contractId: '42', customerId: '1', duration: '7', notes: 'More time',
        status: '', requestedAt: '');
      await expectLater(RemoteRenewalDataSource().submitRenewalRequest(request),
        throwsA(predicate((e) => e.toString().contains('đang chờ duyệt'))));
    }, () => MockClient((request) async {
      expect(jsonDecode(request.body)['days'], 7);
      return http.Response.bytes(utf8.encode(jsonEncode({'message': 'Yêu cầu đang chờ duyệt.'})), 409);
    }));
  });

  test('Proof submission uploads only the reference and image; the server owns amounts', () async {
    await http.runWithClient(() async {
      await CustomerContractService.sendReceipt(12, 'TRANSFER-42', PickedPhoto('proof.png', base64Decode('iVBORw0KGgo=')));
    }, () => MockClient((request) async {
      expect(request.url.path, '/api/debts/12/receipt');
      expect(request.headers['Authorization'], startsWith('Bearer rs1.'));
      expect(utf8.decode(request.bodyBytes, allowMalformed: true), contains('TRANSFER-42'));
      expect(utf8.decode(request.bodyBytes, allowMalformed: true), isNot(contains('name="amount"')));
      return http.Response('{"success":true}', 200);
    }));
  });

  test('Native Android re-encoded gallery photo uses a JPEG filename with unchanged bytes', () async {
    final jpeg = await File('test/fixtures/android-picker-jpeg-with-png-name.jpg').readAsBytes();
    await http.runWithClient(() async {
      await CustomerContractService.sendReceipt(12, 'NATIVE-GALLERY', PickedPhoto('scaled_1000004049.png', jpeg));
    }, () => MockClient((request) async {
      final body = request.bodyBytes;
      final wire = latin1.decode(body);
      final filename = wire.indexOf('filename="scaled_1000004049.jpg"');
      expect(filename, greaterThan(0));
      final imageStart = wire.indexOf('\r\n\r\n', filename) + 4;
      expect(imageStart, greaterThan(0));
      expect(body.sublist(imageStart, imageStart + jpeg.length), jpeg);
      return http.Response('{"success":true}', 200);
    }));
  });

  testWidgets('Signature pad rejects a blank signature and exports actual pen strokes as PNG', (tester) async {
    final key = GlobalKey<SignaturePadState>();
    await tester.pumpWidget(MaterialApp(home: Scaffold(body: SizedBox(width: 350, child: SignaturePad(key: key)))));
    await expectLater(key.currentState!.exportPng(), throwsException);
    final gesture = await tester.startGesture(tester.getCenter(find.byKey(const ValueKey('signature-canvas'))));
    await gesture.moveBy(const Offset(30, 1));
    await gesture.moveBy(const Offset(30, 12));
    await gesture.moveBy(const Offset(20, -12));
    await gesture.up();
    await tester.pump();
    final encoded = (await tester.runAsync(() => key.currentState!.exportPng()))!;
    final png = base64Decode(encoded.split(',').last);
    expect(png.take(8), [137, 80, 78, 71, 13, 10, 26, 10]);
  });

  testWidgets('Debt screen displays the actual server balance and pending proof', (tester) async {
    await http.runWithClient(() async {
      await tester.pumpWidget(const MaterialApp(home: DebtScreen()));
      await tester.pumpAndSettle();
      expect(find.textContaining('145.000'), findsWidgets);
      expect(find.text('Biên lai đang chờ đối soát.'), findsOneWidget);
      expect(find.text('Thanh toán VNPay'), findsNothing);
      await tester.tap(find.byTooltip('Tải lại công nợ'));
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
      expect(find.text('Biên lai đang chờ đối soát.'), findsOneWidget);
    }, () => MockClient((request) async => http.Response.bytes(utf8.encode(jsonEncode([{
      'id': 12, 'contractId': 42, 'period': 1, 'dueDate': '2026-11-07', 'balance': 145000,
      'canPay': true, 'canSendReceipt': false, 'canVnPay': false, 'isFirstPayment': true,
      'agingLabel': 'Chưa quá hạn', 'confirmationStatus': 1,
    }])), 200)));
  });
}
