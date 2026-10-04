import os

ds_abs = """import '../../models/contract_model.dart';
import '../../models/role_enum.dart';

abstract class ContractDataSource {
  Future<List<ContractModel>> getContracts(Role role, String userId);
  Future<bool> updateContractStatus(String contractId, String newStatus);
}
"""
with open("lib/datasources/contract/contract_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_abs)

ds_remote = """import '../../models/contract_model.dart';
import '../../models/role_enum.dart';
import 'contract_datasource.dart';

class RemoteContractDataSource implements ContractDataSource {
  @override
  Future<List<ContractModel>> getContracts(Role role, String userId) async {
    throw UnimplementedError('API chưa có sẵn');
  }

  @override
  Future<bool> updateContractStatus(String contractId, String newStatus) async {
    throw UnimplementedError();
  }
}
"""
with open("lib/datasources/contract/remote_contract_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_remote)

repo = """import '../models/contract_model.dart';
import '../models/role_enum.dart';
import '../datasources/contract/contract_datasource.dart';

class ContractRepository {
  final ContractDataSource _dataSource;
  ContractRepository(this._dataSource);

  Future<List<ContractModel>> getContracts(Role role, String userId) {
    return _dataSource.getContracts(role, userId);
  }

  Future<bool> updateContractStatus(String contractId, String newStatus) {
    return _dataSource.updateContractStatus(contractId, newStatus);
  }
}
"""
with open("lib/repositories/contract_repository.dart", "w", encoding="utf-8") as f: f.write(repo)

prov = """import 'package:flutter/material.dart';
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
"""
with open("lib/providers/contract_provider.dart", "w", encoding="utf-8") as f: f.write(prov)

# Fix async BuildContext gaps in contract_detail_screen
path_detail = "lib/screens/contracts/contract_detail_screen.dart"
with open(path_detail, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace(
    "final success = await context.read<InstallationProvider>().confirmInstallation(contractId);",
    "if (!context.mounted) return;\n      final success = await context.read<InstallationProvider>().confirmInstallation(contractId);"
)
c = c.replace(
    "final success = await context.read<InstallationProvider>().completeInstallation(contractId);",
    "if (!context.mounted) return;\n      final success = await context.read<InstallationProvider>().completeInstallation(contractId);"
)
c = c.replace(
    "final success = await context.read<ContractProvider>().updateContractStatus(",
    "if (!context.mounted) return;\n      final success = await context.read<ContractProvider>().updateContractStatus("
)

with open(path_detail, "w", encoding="utf-8") as f: f.write(c)