import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:quan_ly_cho_thue_thiet_bi/services/api_session.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  setUp(() => SharedPreferences.setMockInitialValues({
    ApiSession.tokenKey: jsonEncode({'accessToken':'rs1.connection-fixture',
      'expiresIn':DateTime.now().add(const Duration(hours:1)).toIso8601String()}),
    ApiSession.userKey: 'kept-user',
  }));

  test('connection failure preserves sign-in and does not retry writes', () async {
    var calls=0;
    await http.runWithClient(() async {
      await expectLater(ApiSession.post(Uri.parse('http://test.invalid/api/contracts')),
        throwsA(isA<ApiConnectionException>().having((e)=>e.outcomeUnknown,'unknown write outcome',true)));
    },()=>MockClient((r) async {calls++;throw http.ClientException('offline');}));
    expect(calls,1);
    final prefs=await SharedPreferences.getInstance();
    expect(prefs.getString(ApiSession.tokenKey),isNotNull);
    expect(prefs.getString(ApiSession.userKey),'kept-user');
  });

  test('bounded read timeout reports connectivity without expiring session', () async {
    await http.runWithClient(() async {
      await expectLater(ApiSession.send(http.Request('GET',Uri.parse('http://test.invalid/api/contracts')),
        timeout:const Duration(milliseconds:5)),throwsA(isA<ApiConnectionException>()
          .having((e)=>e.outcomeUnknown,'read outcome',false)));
    },()=>MockClient((r) async {await Future<void>.delayed(const Duration(milliseconds:25));return http.Response('[]',200);}));
    expect((await SharedPreferences.getInstance()).getString(ApiSession.tokenKey),isNotNull);
  });
}
