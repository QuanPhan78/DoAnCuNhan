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

  Future<UserModel> register({
    required String name,
    required String phone,
    required String email,
    required String password,
    String? address,
    String? cccd,
  }) async {
    final result = await _dataSource.register(
      name: name,
      phone: phone,
      email: email,
      password: password,
      address: address,
      cccd: cccd,
    );
    final UserModel user = result['user'];
    final TokenModel token = result['token'];

    await _dataSource.saveSession(user, token);
    return user;
  }

  Future<UserModel> updateProfile(String userId, {String? name, String? phone, String? address, String? cccd}) async {
    return await _dataSource.updateProfile(userId, name: name, phone: phone, address: address, cccd: cccd);
  }

  Future<void> logout() async {
    await _dataSource.logout();
  }

  Future<UserModel?> checkSession() async {
    return await _dataSource.getCurrentUser();
  }
}