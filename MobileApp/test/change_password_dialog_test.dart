import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:quan_ly_cho_thue_thiet_bi/datasources/local/local_auth_datasource.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/role_enum.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/user_model.dart';
import 'package:quan_ly_cho_thue_thiet_bi/providers/auth_provider.dart';
import 'package:quan_ly_cho_thue_thiet_bi/repositories/auth_repository.dart';
import 'package:quan_ly_cho_thue_thiet_bi/screens/account/security_permissions_screen.dart';

class _PendingPasswordDataSource extends LocalAuthDataSource {
  final requests = <(String, String, String, String)>[];
  final responses = <Completer<void>>[];

  @override
  Future<UserModel?> getCurrentUser() async =>
      UserModel(id: '42', email: 'test@example.invalid', name: 'Test', role: Role.customer);

  @override
  Future<void> changePassword(String userId, String current, String next, String confirmation) {
    requests.add((userId, current, next, confirmation));
    final response = Completer<void>();
    responses.add(response);
    return response.future;
  }
}

void main() {
  testWidgets('Password dialog stays open after failure and closes after a successful retry', (tester) async {
    final source = _PendingPasswordDataSource();
    final auth = AuthProvider(AuthRepository(source));
    addTearDown(auth.dispose);
    await auth.checkSession();
    await tester.pumpWidget(
      ChangeNotifierProvider.value(
        value: auth,
        child: const MaterialApp(home: SecurityPermissionsScreen()),
      ),
    );

    await tester.tap(find.text('Đổi mật khẩu'));
    await tester.pumpAndSettle();
    final fields = find.descendant(of: find.byType(AlertDialog), matching: find.byType(TextField));
    await tester.enterText(fields.at(0), 'old-password');
    await tester.enterText(fields.at(1), 'new-password');
    await tester.enterText(fields.at(2), 'new-password');

    final button = find.byType(ElevatedButton);
    await tester.tap(button);
    await tester.pump();
    expect(tester.widget<ElevatedButton>(button).onPressed, isNull);
    expect(source.requests.single, ('42', 'old-password', 'new-password', 'new-password'));
    expect(find.text('Đổi mật khẩu thành công.'), findsNothing);

    source.responses.single.completeError(Exception('Mật khẩu hiện tại không đúng.'));
    await tester.pumpAndSettle();
    expect(find.byType(AlertDialog), findsOneWidget);
    expect(find.text('Mật khẩu hiện tại không đúng.'), findsOneWidget);
    expect(find.text('Đổi mật khẩu thành công.'), findsNothing);

    await tester.tap(button);
    await tester.pump();
    source.responses.last.complete();
    await tester.pumpAndSettle();
    expect(find.byType(AlertDialog), findsNothing);
    expect(find.text('Đổi mật khẩu thành công.'), findsOneWidget);
  });
}
