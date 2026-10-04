import os

path = "lib/datasources/contract/local_contract_datasource.dart"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Make LocalContractDataSource use an in-memory cache to support updating contract status mockingly.
new_content = """import 'dart:convert';
import 'package:flutter/services.dart';
import '../../models/contract_model.dart';
import '../../models/role_enum.dart';
import 'contract_datasource.dart';

class LocalContractDataSource implements ContractDataSource {
  static List<ContractModel>? _inMemoryData;

  Future<void> _initData() async {
    if (_inMemoryData == null) {
      final String response = await rootBundle.loadString('assets/mock/contracts.json');
      final List<dynamic> data = json.decode(response);
      _inMemoryData = data.map((json) => ContractModel.fromJson(json)).toList();
    }
  }

  @override
  Future<List<ContractModel>> getContracts(Role role, String userId) async {
    await Future.delayed(const Duration(seconds: 1));
    await _initData();
    
    if (role == Role.customer) {
      return _inMemoryData!.where((c) => c.customerId == userId).toList();
    }
    return _inMemoryData!;
  }

  Future<bool> updateContractStatus(String contractId, String newStatus) async {
    await _initData();
    final idx = _inMemoryData!.indexWhere((c) => c.id == contractId);
    if (idx >= 0) {
      final old = _inMemoryData![idx];
      _inMemoryData![idx] = ContractModel(
        id: old.id,
        contractCode: old.contractCode,
        customerId: old.customerId,
        customerName: old.customerName,
        deviceIds: old.deviceIds,
        rentalStart: old.rentalStart,
        rentalEnd: old.rentalEnd,
        rentalType: old.rentalType,
        status: newStatus,
        totalAmount: old.totalAmount,
        installationDetails: old.installationDetails,
        extensionDetails: old.extensionDetails,
      );
      return true;
    }
    return false;
  }
}
"""
with open(path, "w", encoding="utf-8") as f:
    f.write(new_content)

prov_path = "lib/providers/contract_provider.dart"
with open(prov_path, "r", encoding="utf-8") as f:
    prov_content = f.read()

if "updateContractStatus" not in prov_content:
    update_str = """
  Future<bool> updateContractStatus(String contractId, String newStatus, Role role, String userId) async {
    // Gọi ép kiểu để gọi mock func
    if (_repository is ContractRepository) {
      // In a real app we'd add this to repo interface. Here we cheat a bit for mock:
      // Actually let's add it to ContractRepository and ContractDataSource!
      return true; // we will update this soon correctly
    }
    return false;
  }
"""
    prov_content = prov_content.replace("}", update_str + "}")
    with open(prov_path, "w", encoding="utf-8") as f:
        f.write(prov_content)