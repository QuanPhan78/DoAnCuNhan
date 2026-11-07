import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:provider/provider.dart';
import 'package:quan_ly_cho_thue_thiet_bi/main.dart' as app;
import 'package:quan_ly_cho_thue_thiet_bi/models/contract_model.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/device_model.dart';
import 'package:quan_ly_cho_thue_thiet_bi/providers/auth_provider.dart';
import 'package:quan_ly_cho_thue_thiet_bi/screens/contracts/debt_screen.dart';
import 'package:quan_ly_cho_thue_thiet_bi/screens/contracts/sign_contract_screen.dart';
import 'package:quan_ly_cho_thue_thiet_bi/screens/dashboard/dashboard_screen.dart';
import 'package:quan_ly_cho_thue_thiet_bi/screens/requests/rental_confirm_screen.dart';
import 'package:quan_ly_cho_thue_thiet_bi/screens/tasks/handover_screen.dart';
import 'package:quan_ly_cho_thue_thiet_bi/services/api_session.dart';
import 'package:quan_ly_cho_thue_thiet_bi/services/customer_contract_service.dart';
import 'package:quan_ly_cho_thue_thiet_bi/widgets/core/custom_button.dart';
import 'package:quan_ly_cho_thue_thiet_bi/widgets/photo_field.dart';

void main() {
  final binding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets('Physical Android customer cart, signing, proof, renewal and technician handover', (tester) async {
    Future<void> waitFor(bool Function() ready, {int seconds = 45}) async {
      final end = DateTime.now().add(Duration(seconds: seconds));
      while (!ready() && DateTime.now().isBefore(end)) {
        await tester.pump(const Duration(milliseconds: 200));
        await Future<void>.delayed(const Duration(milliseconds: 100));
      }
      expect(ready(), isTrue, reason: 'Physical UI condition timed out');
    }
    NavigatorState nav() => tester.state<NavigatorState>(find.byType(Navigator).first);
    BuildContext root() => tester.element(find.byType(Navigator).first);
    Future<void> route(String name, {Object? arguments}) async {
      nav().pushNamedAndRemoveUntil(name, (_) => false, arguments: arguments);
      await tester.pump(const Duration(milliseconds: 300));
    }
    Future<void> tap(Finder finder) async {
      ScaffoldMessenger.maybeOf(root())?.clearSnackBars();
      FocusManager.instance.primaryFocus?.unfocus();
      await SystemChannels.textInput.invokeMethod<void>('TextInput.hide');
      await tester.pump(const Duration(milliseconds: 300));
      if (finder.evaluate().isEmpty) {
        await tester.scrollUntilVisible(finder, 220, scrollable: find.byType(Scrollable).first);
      }
      await tester.ensureVisible(finder);
      await tester.pump(const Duration(milliseconds: 300));
      await tester.tap(finder);
      await tester.pump(const Duration(milliseconds: 300));
    }
    Future<void> login(String email) async {
      await route('/login');
      await tester.pumpAndSettle();
      await tester.enterText(find.byType(TextFormField).at(0), email);
      await tester.enterText(find.byType(TextFormField).at(1), 'Demo@123');
      await tap(find.widgetWithText(CustomButton, 'Đăng nhập'));
    }
    Future<void> capture(String name) async {
      await tester.pump(const Duration(milliseconds: 500));
      await binding.takeScreenshot(name);
    }
    Future<dynamic> get(String path) async => CustomerContractService.decode(await ApiSession.get(CustomerContractService.url(path)));

    app.main(); await tester.pump();
    await Future<void>.delayed(const Duration(seconds: 2)); await tester.pump();
    await binding.convertFlutterSurfaceToImage();
    await login('mobile@demo.invalid');
    await waitFor(() => find.byType(DashboardScreen).evaluate().isNotEmpty);
    await capture('03-customer-dashboard');
    final products = (await get('/devices')) as List;
    for (final name in ['Phone Tablet', 'Phone Projector']) {
      final product = DeviceModel.fromJson(Map<String, dynamic>.from(products.firstWhere((p) => p['name'] == name)));
      await route('/device_detail', arguments: product); await tester.pumpAndSettle();
      await tap(find.text('Thêm vào giỏ hàng'));
    }
    await route('/cart'); await tester.pumpAndSettle();
    expect(find.text('Phone Tablet'), findsOneWidget);
    expect(find.text('Phone Projector'), findsOneWidget);
    await capture('04-two-device-cart');
    await tap(find.widgetWithText(CustomButton, 'Xem báo giá'));
    await waitFor(() => find.byType(RentalConfirmScreen).evaluate().isNotEmpty);
    await tap(find.widgetWithText(CustomButton, 'XÁC NHẬN THUÊ'));
    await waitFor(() => find.text('Đã gửi yêu cầu thuê').evaluate().isNotEmpty);
    final contracts = (await get('/contracts')) as List;
    final newId = contracts.map((c) => int.parse(c['id'])).reduce((a, b) => a > b ? a : b);
    final detail = ContractModel.fromJson(Map<String, dynamic>.from(await get('/contracts/$newId')));
    await route('/contract_detail', arguments: detail); await tester.pump(const Duration(seconds: 1));
    await tap(find.widgetWithText(CustomButton, 'Ký hợp đồng'));
    await waitFor(() => find.byType(PhotoField).evaluate().length == 2);
    final png = base64Decode('iVBORw0KGgoAAAANSUhEUgAAACAAAAAUCAIAAABj86gYAAAAIklEQVR4nGO48+wDTRHDqAWjFoxaMGrBqAWjFoxacIcICwB2m71bwEJcewAAAABJRU5ErkJggg==');
    // Synthetic picker results exercise real rendering and multipart upload without using personal photos.
    tester.widget<PhotoField>(find.byType(PhotoField).at(0)).onChanged(PickedPhoto('front.png', png));
    tester.widget<PhotoField>(find.byType(PhotoField).at(1)).onChanged(PickedPhoto('back.png', png));
    await tester.pump();
    await tester.ensureVisible(find.byKey(const ValueKey('signature-canvas'))); await tester.pump();
    final gesture = await tester.startGesture(tester.getCenter(find.byKey(const ValueKey('signature-canvas'))));
    await gesture.moveBy(const Offset(35, 0)); await gesture.moveBy(const Offset(35, 20));
    await gesture.moveBy(const Offset(20, -15)); await gesture.up(); await tester.pump();
    await tap(find.byType(CheckboxListTile));
    await capture('05-customer-signature');
    await tap(find.widgetWithText(CustomButton, 'Ký và lưu hợp đồng'));
    await waitFor(() => find.byType(SignContractScreen).evaluate().isEmpty);
    expect((await get('/contracts/$newId'))['customerSigned'], isTrue);
    await tap(find.widgetWithText(CustomButton, 'Công nợ và thanh toán'));
    await waitFor(() => find.text('VietQR / Biên lai').evaluate().isNotEmpty);
    await capture('06-customer-debt');
    await tap(find.text('VietQR / Biên lai'));
    await waitFor(() => find.byType(PhotoField).evaluate().isNotEmpty);
    await tester.enterText(find.byType(TextField).first, 'PHONE-PROOF');
    tester.widget<PhotoField>(find.byType(PhotoField).first).onChanged(PickedPhoto('proof.png', png));
    await tester.pump();
    await tap(find.widgetWithText(CustomButton, 'Gửi biên lai để đối soát'));
    await waitFor(() => find.byType(DebtScreen).evaluate().isNotEmpty && find.text('Biên lai đang chờ đối soát.').evaluate().isNotEmpty);
    await capture('07-proof-pending');
    final debt = (await CustomerContractService.debts()).firstWhere((r) => '${r['contractId']}' == '$newId');
    expect(debt['amountPaid'], 0);
    expect(debt['confirmationStatus'], 1);
    final active = contracts.firstWhere((c) => c['statusCode'] == 1);
    final activeContract = ContractModel.fromJson(Map<String, dynamic>.from(await get('/contracts/${active['id']}')));
    await route('/contract_detail', arguments: activeContract); await tester.pump(const Duration(seconds: 1));
    await tap(find.widgetWithText(CustomButton, 'Gia hạn hợp đồng'));
    await tester.enterText(find.byType(TextField).first, '2');
    await tap(find.widgetWithText(CustomButton, 'Gửi yêu cầu'));
    await waitFor(() => find.byType(AlertDialog).evaluate().isEmpty);
    await Future<void>.delayed(const Duration(seconds: 1)); await tester.pump();
    final history = await CustomerContractService.renewals(active['id']);
    expect(history.first['days'], 2); expect(history.first['statusCode'], 0);
    await capture('08-renewal-request');
    await root().read<AuthProvider>().logout();
    await login('tech@demo.invalid');
    await waitFor(() => find.byType(DashboardScreen).evaluate().isNotEmpty);
    expect(find.byTooltip('Giỏ hàng'), findsNothing);
    expect(find.byTooltip('Sổ công nợ'), findsNothing);
    await capture('09-technician-dashboard');
    await route('/tasks');
    await waitFor(() => find.text('Lắp đặt').evaluate().isNotEmpty);
    await tap(find.text('Lắp đặt').first);
    await tap(find.text('Biên bản giao nhận'));
    await waitFor(() => find.byType(HandoverScreen).evaluate().isNotEmpty && find.text('Loại biên bản').evaluate().isNotEmpty);
    final condition = find.byWidgetPredicate((w) => w is TextField && w.decoration?.labelText == 'Tình trạng sau kiểm tra');
    await tester.scrollUntilVisible(condition, 200, scrollable: find.byType(Scrollable).first);
    await tester.enterText(condition, 'Phone checked equipment');
    await tester.scrollUntilVisible(find.byType(PhotoField).first, 200, scrollable: find.byType(Scrollable).first);
    tester.widget<PhotoField>(find.byType(PhotoField).first).onChanged(PickedPhoto('equipment.png', png));
    await tester.pump();
    await capture('10-technician-handover');
    await tap(find.widgetWithText(CustomButton, 'Lưu biên bản'));
    await waitFor(() => find.byType(HandoverScreen).evaluate().isEmpty);
    await root().read<AuthProvider>().logout();
    await login('sales@demo.invalid');
    await waitFor(() => find.textContaining('vui lòng sử dụng Web').evaluate().isNotEmpty);
    expect(root().read<AuthProvider>().isAuthenticated, isFalse);
    await capture('11-sales-web-only');
    binding.reportData ??= {};
    binding.reportData!.addAll({'customerContract': newId, 'realBackend': true,
      'syntheticPickerPhotos': true, 'customerAndTechnicianFlows': 'passed'});
  });
}
