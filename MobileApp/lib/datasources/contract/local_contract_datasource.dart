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
