import 'package:flutter/material.dart';
import '../models/contract_model.dart';
import '../models/role_enum.dart';
import '../repositories/contract_repository.dart';

class ContractProvider with ChangeNotifier {
  final ContractRepository _repository;

  ContractProvider(this._repository);

  List<ContractModel> _allContracts = [];
  List<ContractModel> _filteredContracts = [];
  
  bool _isLoading = false;
  String? _errorMessage;
  
  String _searchQuery = '';
  String? _selectedStatus;

  List<ContractModel> get contracts => _filteredContracts;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  List<String> get availableStatuses => _allContracts.map((c) => c.status ?? 'Khác').toSet().toList();
  String? get selectedStatus => _selectedStatus;

  Future<void> fetchContracts(Role role, String userId) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _allContracts = await _repository.getContracts(role, userId);
      _applyFilters();
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> updateContractStatus(String contractId, String newStatus, Role role, String userId) async {
    _isLoading = true;
    notifyListeners();
    try {
      final success = await _repository.updateContractStatus(contractId, newStatus);
      if (success) {
        await fetchContracts(role, userId);
      }
      return success;
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  void search(String query) {
    _searchQuery = query;
    _applyFilters();
  }

  void setStatusFilter(String? status) {
    _selectedStatus = status;
    _applyFilters();
  }

  void _applyFilters() {
    _filteredContracts = _allContracts.where((contract) {
      final matchesSearch = (contract.contractCode?.toLowerCase().contains(_searchQuery.toLowerCase()) ?? false) ||
                            (contract.customerName?.toLowerCase().contains(_searchQuery.toLowerCase()) ?? false);
      final matchesStatus = _selectedStatus == null || contract.status == _selectedStatus;
      
      return matchesSearch && matchesStatus;
    }).toList();
    notifyListeners();
  }
}
