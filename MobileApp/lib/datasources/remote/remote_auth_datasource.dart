import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../../models/user_model.dart';
import '../../models/token_model.dart';
import '../../models/role_enum.dart';
import '../../services/api_config.dart';
import '../auth_datasource.dart';

class RemoteAuthDataSource implements AuthDataSource {
  static const String _userKey = 'USER_SESSION';
  static const String _tokenKey = 'TOKEN_SESSION';

  final String? _baseUrl;
  String get baseUrl => _baseUrl ?? ApiConfig.baseUrl;

  RemoteAuthDataSource({String? baseUrl}) : _baseUrl = baseUrl;

  @override
  Future<Map<String, dynamic>> login(String email, String password) async {
    final url = Uri.parse('$baseUrl/auth/login');
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email.trim(),
          'emailOrPhone': email.trim(),
          'username': email.trim(),
          'password': password,
        }),
      );

      final data = json.decode(utf8.decode(response.bodyBytes));

      if (response.statusCode >= 200 && response.statusCode < 300 && data['user'] != null) {
        final user = UserModel.fromJson(data['user']);
        final token = TokenModel.fromJson(data['token']);
        return {
          'user': user,
          'token': token,
        };
      } else {
        String message = data['message'] ?? data['Message'] ?? data['title'] ?? '';
        if (message.isEmpty && data['errors'] != null) {
          final errors = data['errors'] as Map<String, dynamic>;
          final errorList = errors.values.expand((v) => (v as List).map((e) => e.toString())).toList();
          message = errorList.join(', ');
        }
        if (message.isEmpty) {
          message = 'Đăng nhập không thành công (${response.statusCode})';
        }
        throw Exception(message);
      }
    } catch (e) {
      if (e is Exception) rethrow;
      throw Exception('Lỗi kết nối máy chủ: $e');
    }
  }

  @override
  Future<Map<String, dynamic>> register({
    required String name,
    required String phone,
    required String email,
    required String password,
    String? address,
    String? cccd,
  }) async {
    final url = Uri.parse('$baseUrl/auth/register');
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'name': name.trim(),
          'phone': phone.trim(),
          'email': email.trim(),
          'password': password,
          'address': address?.trim(),
          'cccd': cccd?.trim(),
          'hoTen': name.trim(),
          'soDienThoai': phone.trim(),
          'matKhau': password,
          'diaChi': address?.trim(),
        }),
      );

      final data = json.decode(utf8.decode(response.bodyBytes));

      if (response.statusCode >= 200 && response.statusCode < 300 && data['user'] != null) {
        final user = UserModel.fromJson(data['user']);
        final token = TokenModel.fromJson(data['token']);
        return {
          'user': user,
          'token': token,
        };
      } else {
        String message = data['message'] ?? data['Message'] ?? data['title'] ?? '';
        if (message.isEmpty && data['errors'] != null) {
          final errors = data['errors'] as Map<String, dynamic>;
          final errorList = errors.values.expand((v) => (v as List).map((e) => e.toString())).toList();
          message = errorList.join(', ');
        }
        if (message.isEmpty) {
          message = 'Đăng ký không thành công (${response.statusCode})';
        }
        throw Exception(message);
      }
    } catch (e) {
      if (e is Exception) rethrow;
      throw Exception('Lỗi kết nối máy chủ: $e');
    }
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
      try {
        return UserModel.fromJson(jsonDecode(userStr));
      } catch (_) {
        return null;
      }
    }
    return null;
  }

  @override
  Future<TokenModel?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    final tokenStr = prefs.getString(_tokenKey);
    if (tokenStr != null) {
      try {
        return TokenModel.fromJson(jsonDecode(tokenStr));
      } catch (_) {
        return null;
      }
    }
    return null;
  }

  @override
  Future<UserModel> updateProfile(String userId, {String? name, String? phone, String? address, String? cccd}) async {
    final url = Uri.parse('$baseUrl/auth/profile/$userId');
    final response = await http.put(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'name': name,
        'phone': phone,
        'address': address,
        'cccd': cccd,
      }),
    );

    if (response.statusCode >= 200 && response.statusCode < 300) {
      final currentUser = await getCurrentUser();
      final updated = UserModel(
        id: userId,
        name: name ?? currentUser?.name ?? '',
        email: currentUser?.email ?? '',
        phone: phone ?? currentUser?.phone ?? '',
        role: currentUser?.role ?? Role.customer,
        address: address ?? currentUser?.address,
        cccd: cccd ?? currentUser?.cccd,
      );
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_userKey, jsonEncode(updated.toJson()));
      return updated;
    } else {
      throw Exception('Cập nhật thông tin thất bại (${response.statusCode})');
    }
  }

  @override
  Future<void> logout() async {
    await clearSession();
  }
}
