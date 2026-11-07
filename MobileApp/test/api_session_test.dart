import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:quan_ly_cho_thue_thiet_bi/services/api_session.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  String storedToken(String value, DateTime expires) => jsonEncode({
        'accessToken': value,
        'expiresIn': expires.toIso8601String(),
      });

  test('legacy, malformed and expired tokens require sign-in', () {
    final now = DateTime.now();
    expect(ApiSession.parseToken(storedToken('token_old', now.add(const Duration(hours: 1)))), isNull);
    expect(ApiSession.parseToken(storedToken('rs1.expired', now.subtract(const Duration(hours: 1)))), isNull);
    expect(ApiSession.parseToken('invalid JSON'), isNull);
  });

  test('protected requests send bearer and only 401 invalidates the session', () async {
    final stored = storedToken('rs1.fixture', DateTime.now().add(const Duration(hours: 1)));
    SharedPreferences.setMockInitialValues({
      ApiSession.tokenKey: stored,
      ApiSession.userKey: '{}',
    });
    final url = Uri.parse('https://test.invalid/api/contracts');
    var status = 403;
    final prefs = await SharedPreferences.getInstance();
    await http.runWithClient(() async {
      expect((await ApiSession.get(url)).statusCode, 403);
      expect(prefs.getString(ApiSession.tokenKey), stored);

      final expired = expectLater(ApiSession.expired, emits(null));
      status = 401;
      await expectLater(ApiSession.get(url), throwsException);
      await expired;
      expect(prefs.getString(ApiSession.tokenKey), isNull);
      expect(prefs.getString(ApiSession.userKey), isNull);
    }, () => MockClient((request) async {
          expect(request.headers['authorization'], 'Bearer rs1.fixture');
          expect(request.followRedirects, isFalse);
          return http.Response('{}', status);
        }));
  });
}
