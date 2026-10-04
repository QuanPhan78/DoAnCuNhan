import '../../models/user_model.dart';
import '../../models/token_model.dart';

abstract class AuthDataSource {
  Future<Map<String, dynamic>> login(String email, String password);
  Future<void> logout();
  Future<UserModel?> getCurrentUser();
  Future<TokenModel?> getToken();
  Future<void> saveSession(UserModel user, TokenModel token);
  Future<void> clearSession();
}