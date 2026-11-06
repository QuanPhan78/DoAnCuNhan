import '../../models/user_model.dart';
import '../../models/token_model.dart';

abstract class AuthDataSource {
  Future<Map<String, dynamic>> login(String email, String password);
  Future<Map<String, dynamic>> register({
    required String name,
    required String phone,
    required String email,
    required String password,
    String? address,
    String? cccd,
  });
  Future<UserModel> updateProfile(String userId, {String? name, String? phone, String? address, String? cccd});
  Future<void> logout();
  Future<UserModel?> getCurrentUser();
  Future<TokenModel?> getToken();
  Future<void> saveSession(UserModel user, TokenModel token);
  Future<void> clearSession();
}
