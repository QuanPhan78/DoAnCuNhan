import 'dart:async';

import 'package:flutter/material.dart';
import '../models/user_model.dart';
import '../repositories/auth_repository.dart';

class AuthProvider with ChangeNotifier {
  final AuthRepository _repository;
  StreamSubscription<void>? _sessionExpiry;

  UserModel? _currentUser;
  bool _isLoading = false;
  String? _errorMessage;

  AuthProvider(this._repository, {Stream<void>? sessionExpired}) {
    _sessionExpiry = sessionExpired?.listen((_) {
      _currentUser = null;
      _errorMessage = 'Phiên đăng nhập đã hết. Vui lòng đăng nhập lại.';
      notifyListeners();
    });
  }

  @override
  void dispose() {
    _sessionExpiry?.cancel();
    super.dispose();
  }

  UserModel? get currentUser => _currentUser;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get isAuthenticated => _currentUser != null;

  Future<void> checkSession() async {
    _isLoading = true;
    notifyListeners();
    try {
      _currentUser = await _repository.checkSession();
    } catch (e) {
      _currentUser = null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _currentUser = await _repository.login(email, password);
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _currentUser = null;
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> register({
    required String name,
    required String phone,
    required String email,
    required String password,
    String? address,
    required String cccd,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _currentUser = await _repository.register(
        name: name,
        phone: phone,
        email: email,
        password: password,
        address: address,
        cccd: cccd,
      );
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _currentUser = null;
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> updateProfile({
    String? name,
    String? phone,
    String? address,
    String? cccd,
  }) async {
    if (_currentUser == null) return false;
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final updated = await _repository.updateProfile(
        _currentUser!.id,
        name: name,
        phone: phone,
        address: address,
        cccd: cccd,
      );
      _currentUser = updated;
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<String?> changePassword(String current, String next, String confirmation) async {
    final user = _currentUser;
    if (user == null) return 'Phiên đăng nhập đã hết. Vui lòng đăng nhập lại.';

    try {
      await _repository.changePassword(user.id, current, next, confirmation);
      return null;
    } catch (e) {
      return e.toString().replaceFirst('Exception: ', '');
    }
  }

  Future<void> logout() async {
    _isLoading = true;
    notifyListeners();

    try {
      await _repository.logout();
      _currentUser = null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
