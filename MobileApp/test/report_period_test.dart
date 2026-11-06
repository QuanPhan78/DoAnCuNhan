import 'dart:async';
import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:quan_ly_cho_thue_thiet_bi/datasources/report/remote_report_datasource.dart';
import 'package:quan_ly_cho_thue_thiet_bi/providers/report_provider.dart';
import 'package:quan_ly_cho_thue_thiet_bi/repositories/report_repository.dart';
import 'package:quan_ly_cho_thue_thiet_bi/services/api_session.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('Reports query each selected period and ignore a stale response', () async {
    SharedPreferences.setMockInitialValues({
      ApiSession.tokenKey: jsonEncode({
        'accessToken': 'rs1.report-fixture',
        'expiresIn': DateTime.now().add(const Duration(hours: 1)).toIso8601String(),
      }),
    });
    final provider = ReportProvider(ReportRepository(
      RemoteReportDataSource(baseUrl: 'https://test.invalid/api'),
    ));
    addTearDown(provider.dispose);
    final weekStarted = Completer<void>();
    final weekResult = Completer<http.Response>();
    final filters = <String>[];
    await http.runWithClient(() async {
      await provider.fetchReports();
      expect(provider.currentTimeFilter, 'all');
      final week = provider.fetchReports(timeFilter: 'week');
      await weekStarted.future;
      await provider.fetchReports(timeFilter: 'month');
      weekResult.complete(http.Response('{"revenue": 10}', 200));
      await week;
      expect(provider.currentTimeFilter, 'month');
      expect(provider.reportData!.revenue, 20);
      expect(provider.reportData!.fromDate, DateTime(2026, 11));
      await provider.fetchReports();
      expect(filters, ['all', 'week', 'month', 'month']);
    }, () => MockClient((request) {
      final filter = request.url.queryParameters['timeFilter']!;
      filters.add(filter);
      if (filter == 'week') {
        weekStarted.complete();
        return weekResult.future;
      }
      return Future.value(http.Response('{"revenue":20,"fromDate":"2026-11-01"}', 200));
    }));
  });
}
