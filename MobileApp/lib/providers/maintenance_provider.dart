import 'package:flutter/material.dart';
import '../models/maintenance_model.dart';
import '../models/role_enum.dart';
import '../repositories/maintenance_repository.dart';

class MaintenanceProvider with ChangeNotifier {
  final MaintenanceRepository _repository;
  MaintenanceProvider(this._repository);

  List<MaintenanceModel> _maintenances = [];
  bool _isLoading = false;
  String? _errorMessage;

  List<MaintenanceModel> get maintenances => _maintenances;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  Future<void> fetchMaintenances(String userId, Role role, String userName) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    try {
      _maintenances = await _repository.getMaintenances(userId, role, userName);
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> updateMaintenance(MaintenanceModel updated) async {
    try {
      final success = await _repository.updateMaintenance(updated);
      if (success) {
        final index = _maintenances.indexWhere((m) => m.id == updated.id);
        if (index >= 0) {
          _maintenances[index] = updated;
          notifyListeners();
        }
      }
      return success;
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }
}