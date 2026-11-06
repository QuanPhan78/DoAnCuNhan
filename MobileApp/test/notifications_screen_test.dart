import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:quan_ly_cho_thue_thiet_bi/screens/notifications/notifications_screen.dart';
import 'package:quan_ly_cho_thue_thiet_bi/services/api_config.dart';
import 'package:quan_ly_cho_thue_thiet_bi/services/api_session.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  testWidgets('Notification list renders server data and marks an item as read', (tester) async {
    SharedPreferences.setMockInitialValues({
      ApiSession.tokenKey: jsonEncode({
        'accessToken': 'rs1.notifications-fixture',
        'expiresIn': DateTime.now().add(const Duration(hours: 1)).toIso8601String(),
      }),
    });
    ApiConfig.setBaseUrl('https://test.invalid/api');
    addTearDown(ApiConfig.reset);
    var isRead = false;
    await http.runWithClient(() async {
      await tester.pumpWidget(const MaterialApp(home: Scaffold(body: NotificationsScreen())));
      await tester.pumpAndSettle();
      expect(find.text('Bạn được giao công việc'), findsOneWidget);
      expect(find.text('Kiểm kê kho'), findsOneWidget);
      await tester.tap(find.byTooltip('Đánh dấu đã đọc'));
      await tester.pumpAndSettle();
      expect(isRead, isTrue);
      expect(find.byTooltip('Đánh dấu đã đọc'), findsNothing);
      expect(find.text('Kiểm kê kho'), findsOneWidget);
    }, () => MockClient((request) async {
      expect(request.headers['authorization'], 'Bearer rs1.notifications-fixture');
      if (request.method == 'PUT') {
        expect(request.url.path, '/api/notifications/7/read');
        isRead = true;
        return http.Response('', 204);
      }
      expect(request.url.path, '/api/notifications');
      return http.Response.bytes(utf8.encode(jsonEncode([
        {'id': 7, 'title': 'Bạn được giao công việc', 'content': 'Kiểm kê kho',
         'type': 'PhanCong', 'createdAt': '2026-11-01T10:00:00', 'isRead': isRead},
      ])), 200);
    }));
  });
}
