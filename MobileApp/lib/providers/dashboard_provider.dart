import 'package:flutter/material.dart';
import '../models/dashboard_model.dart';
import '../models/role_enum.dart';
import '../repositories/dashboard_repository.dart';

class DashboardProvider with ChangeNotifier {
  final DashboardRepository _repository;

  DashboardProvider(this._repository);

  DashboardData? _data;
  bool _isLoading = false;
  String? _errorMessage;

  DashboardData? get data => _data;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get isEmpty => _data == null && !_isLoading && _errorMessage == null;

  Future<void> loadDashboard(Role role) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _data = await _repository.getDashboardData(role);
    } catch (e) {
      _errorMessage = e.toString();
      _data = null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}