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
  List<ContractModel> get allContracts => _allContracts;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  static const List<String> _defaultStatuses = [
    'Chờ duyệt',
    'Yêu cầu hủy',
    'Đang hiệu lực',
    'Đã trả máy (Chờ quyết toán)',
    'Hoàn thành',
    'Đã hủy',
  ];

  List<String> get availableStatuses {
    final set = <String>{..._defaultStatuses};
    set.addAll(_allContracts.map((c) => c.status ?? 'Khác'));
    return set.toList();
  }
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

  Future<ContractModel> getContract(String contractId, String userId, Role role) {
    return _repository.getContract(contractId, userId, role);
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
