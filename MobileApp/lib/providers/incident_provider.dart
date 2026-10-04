import 'package:flutter/material.dart';
import '../models/incident_model.dart';
import '../models/role_enum.dart';
import '../repositories/incident_repository.dart';
import '../providers/contract_provider.dart'; // Để tra cứu contract nếu cần

class IncidentProvider with ChangeNotifier {
  final IncidentRepository _repository;
  IncidentProvider(this._repository);

  List<IncidentModel> _incidents = [];
  bool _isLoading = false;
  String? _errorMessage;

  List<IncidentModel> get incidents => _incidents;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  Future<void> fetchIncidents(String userId, Role role, ContractProvider contractProvider) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final all = await _repository.getIncidents(userId, role.toString());
      if (role == Role.customer) {
        // Chỉ lấy các sự cố thuộc về hợp đồng của customer này.
        // Thực tế backend sẽ handle. Ở mock, ta filter thông qua contractProvider
        final customerContractIds = contractProvider.contracts.where((c) => c.customerId == userId).map((c) => c.id).toList();
        _incidents = all.where((i) => customerContractIds.contains(i.contractId)).toList();
      } else {
        _incidents = all;
      }
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> createIncident(IncidentModel incident) async {
    try {
      await _repository.createIncident(incident);
      // add locally to avoid re-fetch if we want
      _incidents.insert(0, incident);
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }
}