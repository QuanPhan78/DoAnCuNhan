import 'package:quan_ly_cho_thue_thiet_bi/models/user_model.dart';
import 'package:quan_ly_cho_thue_thiet_bi/models/token_model.dart';
import '../auth_datasource.dart';

// Class này dùng để chuẩn bị cho API thật sau này.
class RemoteAuthDataSource implements AuthDataSource {
  @override
  Future<Map<String, dynamic>> login(String email, String password) async {
    throw UnimplementedError('API chưa có sẵn');
  }

  @override
  Future<void> logout() async {
    throw UnimplementedError('API chưa có sẵn');
  }

  @override
  Future<UserModel?> getCurrentUser() async {
    throw UnimplementedError();
  }

  @override
  Future<TokenModel?> getToken() async {
    throw UnimplementedError();
  }

  @override
  Future<void> saveSession(UserModel user, TokenModel token) async {
    throw UnimplementedError();
  }

  @override
  Future<void> clearSession() async {
    throw UnimplementedError();
  }
}