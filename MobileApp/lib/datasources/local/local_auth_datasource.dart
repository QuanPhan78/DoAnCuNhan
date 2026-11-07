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
  Future<Map<String, dynamic>> register({
    required String name,
    required String phone,
    required String email,
    required String password,
    String? address,
    required String cccd,
  }) async {
    await Future.delayed(const Duration(seconds: 1));

    if (email.isEmpty || password.isEmpty || name.isEmpty || phone.isEmpty) {
      throw Exception('Vui lòng điền đầy đủ các thông tin bắt buộc.');
    }

    if (_mockUsers.any((u) => u['email'] == email)) {
      throw Exception('Email này đã được sử dụng.');
    }

    final identity = cccd.trim();
    _validateIdentity(identity);
    final newUser = {
      'id': (_mockUsers.length + 1).toString(),
      'name': name,
      'phone': phone,
      'email': email,
      'password': password,
      'address': address,
      'cccd': identity,
      'role': 'Khách hàng',
    };
    _mockUsers.add(newUser);

    final token = TokenModel(
      accessToken: 'mock_token_${newUser['id']}',
      refreshToken: 'mock_refresh_${newUser['id']}',
      expiresIn: DateTime.now().add(const Duration(days: 1)),
    );

    final userModel = UserModel.fromJson(newUser);

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
  Future<UserModel> updateProfile(String userId, {String? name, String? phone, String? address, String? cccd}) async {
    final currentUser = await getCurrentUser();
    if (currentUser != null && currentUser.id == userId) {
      final candidate = cccd?.trim() ?? '';
      final changed = cccd != null && candidate != (currentUser.cccd?.trim() ?? '');
      if (changed) _validateIdentity(candidate, exceptId: userId);
      final updated = UserModel(
        id: currentUser.id,
        name: name ?? currentUser.name,
        email: currentUser.email,
        phone: phone ?? currentUser.phone,
        role: currentUser.role,
        address: address ?? currentUser.address,
        cccd: changed ? candidate : currentUser.cccd,
      );
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_userKey, jsonEncode(updated.toJson()));
      final index = _mockUsers.indexWhere((u) => u['id'] == userId);
      if (index >= 0) _mockUsers[index].addAll(updated.toJson());
      return updated;
    }
    throw Exception('Không tìm thấy người dùng');
  }

  void _validateIdentity(String cccd, {String? exceptId}) {
    if (!RegExp(r'^[0-9]{12}$').hasMatch(cccd)) {
      throw Exception('Số CCCD phải có đúng 12 chữ số.');
    }
    if (_mockUsers.any((u) => u['id'] != exceptId && u['cccd'] == cccd)) {
      throw Exception('Số CCCD đã được sử dụng.');
    }
  }

  @override
  Future<void> changePassword(String userId, String current, String next, String confirmation) async {
    final user = _mockUsers.firstWhere((u) => u['id'] == userId, orElse: () => {});
    if (user.isEmpty) throw Exception('Không tìm thấy người dùng.');
    if (user['password'] != current) throw Exception('Mật khẩu hiện tại không đúng.');
    if (next.trim().isEmpty || next.length < 6) throw Exception('Mật khẩu mới cần ít nhất 6 ký tự.');
    if (next != confirmation) throw Exception('Mật khẩu nhập lại không khớp.');
    user['password'] = next;
  }

  @override
  Future<void> logout() async {
    await clearSession();
  }
}
