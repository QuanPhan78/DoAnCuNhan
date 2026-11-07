import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:http/http.dart' as http;
import 'package:provider/provider.dart';
import 'package:printing/printing.dart';
import 'package:quan_ly_cho_thue_thiet_bi/main.dart' as app;
import 'package:quan_ly_cho_thue_thiet_bi/models/device_model.dart';
import 'package:quan_ly_cho_thue_thiet_bi/providers/auth_provider.dart';
import 'package:quan_ly_cho_thue_thiet_bi/providers/rental_provider.dart';
import 'package:quan_ly_cho_thue_thiet_bi/providers/contract_provider.dart';
import 'package:quan_ly_cho_thue_thiet_bi/services/api_session.dart';
import 'package:quan_ly_cho_thue_thiet_bi/services/api_config.dart';
import 'package:quan_ly_cho_thue_thiet_bi/widgets/core/custom_button.dart';
import 'package:quan_ly_cho_thue_thiet_bi/screens/requests/rental_confirm_screen.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  testWidgets('Android device: real booking, connectivity recovery, PDF and incident', (tester) async {
    Future<Map<String,dynamic>> control(String path) async {
      final r=await http.get(Uri.parse('http://127.0.0.1:5109$path'));
      expect(r.statusCode,200);
      return jsonDecode(r.body) as Map<String,dynamic>;
    }
    Future<void> waitFor(bool Function() ready,{int seconds=50}) async {
      final end=DateTime.now().add(Duration(seconds:seconds));
      while(!ready() && DateTime.now().isBefore(end)) {
        await tester.pump(const Duration(milliseconds:200));
        await Future<void>.delayed(const Duration(milliseconds:100));
      }
      expect(ready(),isTrue,reason:'Physical UI condition timed out');
    }
    Future<void> tap(Finder f) async {
      ScaffoldMessenger.maybeOf(tester.element(find.byType(Navigator).first))?.clearSnackBars();
      FocusManager.instance.primaryFocus?.unfocus();
      await SystemChannels.textInput.invokeMethod<void>('TextInput.hide');
      await Future<void>.delayed(const Duration(milliseconds:500));
      await tester.pumpAndSettle();
      await tester.ensureVisible(f);await tester.pumpAndSettle();
      await tester.tap(f);await tester.pump(const Duration(milliseconds:200));
    }
    app.main();await tester.pump();
    await tester.pump(const Duration(seconds:3));
    await Future<void>.delayed(const Duration(seconds:1));await tester.pump();
    NavigatorState nav()=>tester.state<NavigatorState>(find.byType(Navigator).first);
    void route(String name,{Object? arguments}) {nav().pushNamedAndRemoveUntil(name,(r)=>false,arguments:arguments);}
    route('/login');await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextFormField).at(0),'phone@demo.invalid');
    await tester.enterText(find.byType(TextFormField).at(1),'Demo@123');
    expect(tester.widget<TextFormField>(find.byType(TextFormField).at(1)).controller!.text,'Demo@123');
    await tap(find.widgetWithText(CustomButton,'Đăng nhập'));
    await waitFor(()=>find.text('Phone QA').evaluate().isNotEmpty);
    await control('/capture?name=login');
    final context=tester.element(find.byType(Navigator).first);
    final auth=context.read<AuthProvider>();
    expect(auth.isAuthenticated,isTrue);
    final products=jsonDecode((await ApiSession.get(Uri.parse('${ApiConfig.baseUrl}/devices'))).body) as List;
    final device=DeviceModel.fromJson(Map<String,dynamic>.from(products.firstWhere((e)=>e['name']=='Phone Fixture Laptop')));
    final baseline=await control('/state');
    Future<void> bookingForm() async {
      route('/rental_form',arguments:device);await tester.pumpAndSettle();
      await tester.enterText(find.byType(TextFormField).at(0),'Phone connection test address');
      await tap(find.widgetWithText(CustomButton,'TIẾP TỤC'));
      await waitFor(()=>find.byType(RentalConfirmScreen).evaluate().isNotEmpty);
    }
    Future<void> failBooking(String mode,String capture) async {
      await bookingForm();await control('/mode?value=$mode');
      await tap(find.widgetWithText(CustomButton,'XÁC NHẬN THUÊ'));
      final ctx=tester.element(find.byType(RentalConfirmScreen));
      await waitFor(()=>find.textContaining('chưa xác định yêu cầu').evaluate().isNotEmpty,seconds:45);
      expect(ctx.read<RentalProvider>().isLoading,isFalse);
      expect(find.text('Phone connection test address'),findsOneWidget);
      expect(auth.isAuthenticated,isTrue);
      await control('/capture?name=$capture');
    }
    await failBooking('before','offline-before');
    expect((await control('/state'))['contracts'],baseline['contracts']);
    await failBooking('during','offline-during');
    expect((await control('/state'))['contracts'],baseline['contracts']);
    await bookingForm();
    await tap(find.widgetWithText(CustomButton,'XÁC NHẬN THUÊ'));
    await waitFor(()=>find.text('Đã gửi yêu cầu thuê').evaluate().isNotEmpty);
    expect((await control('/state'))['contracts'],(baseline['contracts'] as int)+1);
    await control('/capture?name=booking-created');
    await failBooking('after','offline-after-commit');
    expect((await control('/state'))['contracts'],(baseline['contracts'] as int)+2);
    expect(auth.isAuthenticated,isTrue);
    // No automatic retry occurs after the committed response is dropped.
    await Future<void>.delayed(const Duration(seconds:2));
    expect((await control('/state'))['contracts'],(baseline['contracts'] as int)+2);
    route('/contracts');await tester.pumpAndSettle();
    await control('/capture?name=contracts-recovered');
    final contract=await context.read<ContractProvider>().getContract('12',auth.currentUser!.id,auth.currentUser!.role);
    route('/contract_detail',arguments:contract);await tester.pumpAndSettle();
    await tap(find.byTooltip('Xem file PDF'));
    await waitFor(()=>find.byType(PdfPreview).evaluate().isNotEmpty);
    await tester.pump(const Duration(seconds:3));
    await control('/capture?name=contract-pdf');

    route('/create_incident');await tester.pumpAndSettle();
    await waitFor(()=>find.text('Chọn hợp đồng của bạn').evaluate().isNotEmpty);
    await tap(find.byType(DropdownButtonFormField<String>).at(0));await tester.pumpAndSettle();
    await tap(find.text('HD-0012').last);await tester.pumpAndSettle();
    await tap(find.byType(DropdownButtonFormField<String>).at(1));await tester.pumpAndSettle();
    await tap(find.textContaining('DEBT-FIXTURE').last);await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextFormField).last,'Phone QA: device loses display signal');
    await control('/mode?value=before');
    await tap(find.widgetWithText(CustomButton,'Gửi yêu cầu'));
    await waitFor(()=>find.textContaining('chưa xác định yêu cầu').evaluate().isNotEmpty);
    expect(find.text('Phone QA: device loses display signal'),findsOneWidget);
    expect((await control('/state'))['incidents'],0);
    expect(auth.isAuthenticated,isTrue);
    await control('/capture?name=incident-preserved');
    await tap(find.widgetWithText(CustomButton,'Gửi yêu cầu'));
    await waitFor(()=>find.text('Đã gửi báo cáo sự cố.').evaluate().isNotEmpty);
    expect((await control('/state'))['incidents'],1);
    await control('/capture?name=incident-created');
    final returned=await control('/sync-return');expect(returned['status'],4);
    final refreshed=await context.read<ContractProvider>().getContract('12',auth.currentUser!.id,auth.currentUser!.role);
    expect(refreshed.statusCode,4);
    route('/contract_detail',arguments:refreshed);await tester.pumpAndSettle();
    await control('/capture?name=web-mobile-sync');
  },timeout:const Timeout(Duration(minutes:12)));
}
