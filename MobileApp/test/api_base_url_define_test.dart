import 'package:flutter_test/flutter_test.dart';
import 'package:quan_ly_cho_thue_thiet_bi/services/api_config.dart';

void main() {
  const configured = String.fromEnvironment('API_BASE_URL');
  final expected = configured.trim().isEmpty
      ? 'http://localhost:5000/api'
      : configured.trim().replaceFirst(RegExp(r'/+$'), '');

  tearDown(ApiConfig.reset);

  test('build configuration survives a runtime override and reset', () {
    expect(ApiConfig.baseUrl, expected);
    ApiConfig.setBaseUrl(' http://192.0.2.10:5000/api/ ');
    expect(ApiConfig.baseUrl, 'http://192.0.2.10:5000/api');
    ApiConfig.reset();
    expect(ApiConfig.baseUrl, expected);
    ApiConfig.setBaseUrl('   ');
    expect(ApiConfig.baseUrl, expected);
  });
}
