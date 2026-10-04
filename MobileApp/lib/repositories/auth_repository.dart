import '../models/user_model.dart';
import '../models/token_model.dart';
import '../datasources/auth_datasource.dart';

class AuthRepository {
  final AuthDataSource _dataSource;

  AuthRepository(this._dataSource);

  Future<UserModel> login(String email, String password) async {
    final result = await _dataSource.login(email, password);
    final UserModel user = result['user'];
    final TokenModel token = result['token'];

    await _dataSource.saveSession(user, token);
    return user;
  }

  Future<void> logout() async {
    await _dataSource.logout();
  }

  Future<UserModel?> checkSession() async {
    return await _dataSource.getCurrentUser();
  }
}