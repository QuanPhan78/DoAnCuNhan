import '../../models/role_enum.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../../models/user_model.dart';
import '../../models/token_model.dart';
import '../../services/api_config.dart';
import '../../services/api_session.dart';
import '../auth_datasource.dart';

class RemoteAuthDataSource implements AuthDataSource {
  static const String _userKey = ApiSession.userKey;
  static const String _tokenKey = ApiSession.tokenKey;

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

      if (response.statusCode == 429) {
        throw Exception('Bạn đã thử đăng nhập quá nhiều lần. Vui lòng thử lại sau.');
      }
      final data = _responseData(response);

      if (response.statusCode >= 200 && response.statusCode < 300 && data['user'] != null) {
        final user = UserModel.fromJson(data['user']);
        _requireMobileRole(user);
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
    required String cccd,
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
          'cccd': cccd.trim(),
          'hoTen': name.trim(),
          'soDienThoai': phone.trim(),
          'matKhau': password,
          'diaChi': address?.trim(),
        }),
      );

      final data = _responseData(response);

      if (response.statusCode >= 200 && response.statusCode < 300 && data['user'] != null) {
        final user = UserModel.fromJson(data['user']);
        _requireMobileRole(user);
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
    if (await getToken() == null) {
      await clearSession();
      return null;
    }
    final response = await ApiSession.get(Uri.parse('$baseUrl/auth/me'));
    if (response.statusCode != 200) throw Exception('Không thể kiểm tra phiên đăng nhập.');
    final user = UserModel.fromJson(_responseData(response));
    try { _requireMobileRole(user); } catch (_) { await clearSession(); rethrow; }
    if (user.id.isEmpty) throw Exception('Phiên đăng nhập không hợp lệ.');
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_userKey, jsonEncode(user.toJson()));
    return user;
  }

  @override
  Future<TokenModel?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return ApiSession.parseToken(prefs.getString(_tokenKey));
  }

  @override
  Future<UserModel> updateProfile(String userId, {String? name, String? phone, String? address, String? cccd}) async {
    final url = Uri.parse('$baseUrl/auth/profile/$userId');
    final response = await ApiSession.put(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'name': name,
        'phone': phone,
        'address': address,
        'cccd': cccd,
      }),
    );

    final data = _responseData(response);
    final profile = data['user'];
    if (response.statusCode >= 200 && response.statusCode < 300 &&
        profile is Map<String, dynamic>) {
      final updated = UserModel.fromJson(profile);
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_userKey, jsonEncode(updated.toJson()));
      return updated;
    } else {
      throw Exception(data['message'] ?? 'Cập nhật hồ sơ thất bại.');
    }
  }

  @override
  Future<void> changePassword(String userId, String current, String next, String confirmation) async {
    try {
      final original = await getToken();
      final response = await ApiSession.post(
        Uri.parse('$baseUrl/auth/change-password'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'oldPassword': current,
          'newPassword': next,
          'confirmPassword': confirmation,
        }),
      );
      final data = _responseData(response);
      if (response.statusCode < 200 || response.statusCode >= 300 || data['success'] != true) {
        throw Exception(data['message'] ?? 'Đổi mật khẩu thất bại.');
      }
      final token = ApiSession.parseToken(jsonEncode(data['token']));
      if (token == null) throw Exception('Mật khẩu đã đổi. Vui lòng đăng nhập lại.');

      final prefs = await SharedPreferences.getInstance();
      final activeToken = ApiSession.parseToken(prefs.getString(_tokenKey));
      if (activeToken?.accessToken == original?.accessToken) {
        await prefs.setString(_tokenKey, jsonEncode(token.toJson()));
      }
    } on http.ClientException {
      throw Exception('Không kết nối được với máy chủ.');
    }
  }

  void _requireMobileRole(UserModel user) {
    if (user.role != Role.customer && user.role != Role.staff) {
      throw Exception('Ứng dụng dành cho khách hàng và kỹ thuật. Tài khoản kinh doanh hoặc quản trị vui lòng sử dụng Web.');
    }
  }

  Map<String, dynamic> _responseData(http.Response response) {
    try {
      final data = jsonDecode(utf8.decode(response.bodyBytes));
      if (data is Map<String, dynamic>) return data;
    } on FormatException {
      // The HTTP status still indicates failure when there is no JSON body.
    }
    return {};
  }

  @override
  Future<void> logout() async {
    await clearSession();
  }
}
