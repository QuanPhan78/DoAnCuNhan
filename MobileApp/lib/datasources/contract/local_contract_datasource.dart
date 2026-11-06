import 'dart:convert';
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

  @override
  Future<ContractModel> getContract(String contractId, String userId, Role role) async {
    final contracts = await getContracts(role, userId);
    return contracts.firstWhere(
      (contract) => contract.id == contractId,
      orElse: () => throw Exception('Không tìm thấy hợp đồng.'),
    );
  }
}
