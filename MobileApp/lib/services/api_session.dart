import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../models/token_model.dart';

class ApiSession {
  static const userKey = 'USER_SESSION';
  static const tokenKey = 'TOKEN_SESSION';
  static final _expired = StreamController<void>.broadcast();
  static Stream<void> get expired => _expired.stream;

  static TokenModel? parseToken(String? stored) {
    if (stored == null) return null;
    try {
      final token = TokenModel.fromJson(jsonDecode(stored));
      return token.accessToken.startsWith('rs1.') &&
              token.expiresIn.isAfter(DateTime.now())
          ? token
          : null;
    } on FormatException {
      return null;
    } on TypeError {
      return null;
    }
  }

  static Future<http.Response> get(Uri uri) => _send('GET', uri);

  static Future<http.Response> post(Uri uri,
          {Map<String, String>? headers, String? body}) =>
      _send('POST', uri, headers: headers, body: body);

  static Future<http.Response> put(Uri uri,
          {Map<String, String>? headers, String? body}) =>
      _send('PUT', uri, headers: headers, body: body);

  static Future<http.Response> _send(String method, Uri uri,
      {Map<String, String>? headers, String? body}) {
    final request = http.Request(method, uri)..headers.addAll(headers ?? {});
    if (body != null) request.body = body;
    return send(request);
  }

  static Future<http.Response> send(http.BaseRequest request) async {
    final prefs = await SharedPreferences.getInstance();
    final stored = prefs.getString(tokenKey);
    final token = parseToken(stored);
    if (token == null) {
      await _invalidate(prefs, stored);
      throw Exception('Phiên đăng nhập đã hết. Vui lòng đăng nhập lại.');
    }

    request.followRedirects = false;
    request.headers['Authorization'] = 'Bearer ${token.accessToken}';
    final client = http.Client();
    try {
      final response = await http.Response.fromStream(await client.send(request));
      if (response.statusCode == 401) {
        await _invalidate(prefs, stored);
        throw Exception('Phiên đăng nhập đã hết. Vui lòng đăng nhập lại.');
      }
      return response;
    } finally {
      client.close();
    }
  }

  static Future<void> _invalidate(SharedPreferences prefs, String? rejected) async {
    if (prefs.getString(tokenKey) != rejected) return;
    await Future.wait([prefs.remove(tokenKey), prefs.remove(userKey)]);
    if (prefs.getString(tokenKey) == null) _expired.add(null);
  }
}
