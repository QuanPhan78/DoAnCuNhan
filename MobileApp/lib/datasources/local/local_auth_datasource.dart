import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../../models/user_model.dart';
import '../../models/token_model.dart';
import '../auth_datasource.dart';

class LocalAuthDataSource implements AuthDataSource {
  static const String _userKey = 'USER_SESSION';
  static const String _tokenKey = 'TOKEN_SESSION';

  // Mock Data
  final List<Map<String, dynamic>> _mockUsers = [
    {
      'id': '1',
      'email': 'customer@test.com',
      'password': '123456',
      'name': 'Nguyễn Khách Hàng',
      'role': 'Khách hàng'
    },
    {
      'id': '2',
      'email': 'staff@test.com',
      'password': '123456',
      'name': 'Trần Nhân Viên',
      'role': 'Nhân viên'
    },
    {
      'id': '3',
      'email': 'admin@test.com',
      'password': '123456',
      'name': 'Lê Quản Lý',
      'role': 'Quản lý'
    }
  ];

  @override
  Future<Map<String, dynamic>> login(String email, String password) async {
    // Simulate delay
    await Future.delayed(const Duration(seconds: 1));

    if (email.isEmpty || password.isEmpty) {
      throw Exception('Email hoặc mật khẩu không được để trống.');
    }

    final user = _mockUsers.firstWhere(
      (u) => u['email'] == email,
      orElse: () => <String, dynamic>{},
    );

    if (user.isEmpty) {
      throw Exception('Tài khoản không tồn tại.');
    }

    if (user['password'] != password) {
      throw Exception('Sai mật khẩu.');
    }

    // Generate mock token
    final token = TokenModel(
      accessToken: 'mock_access_token_',
      refreshToken: 'mock_refresh_token_',
      expiresIn: DateTime.now().add(const Duration(days: 1)),
    );

    final userModel = UserModel.fromJson(user);

    return {
      'user': userModel,
      'token': token,
    };
  }

  @override
  Future<void> saveSession(UserModel user, TokenModel token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_userKey, jsonEncode(user.toJson()));
    await prefs.setString(_tokenKey, jsonEncode(token.toJson()));
  }

  @override
  Future<void> clearSession() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_userKey);
    await prefs.remove(_tokenKey);
  }

  @override
  Future<UserModel?> getCurrentUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userStr = prefs.getString(_userKey);
    if (userStr != null) {
      return UserModel.fromJson(jsonDecode(userStr));
    }
    return null;
  }

  @override
  Future<TokenModel?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    final tokenStr = prefs.getString(_tokenKey);
    if (tokenStr != null) {
      return TokenModel.fromJson(jsonDecode(tokenStr));
    }
    return null;
  }

  @override
  Future<void> logout() async {
    await clearSession();
  }
}