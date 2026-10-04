import 'dart:convert';
import 'package:flutter/services.dart';
import '../../models/installation_model.dart';
import 'installation_datasource.dart';

class LocalInstallationDataSource implements InstallationDataSource {
  static List<InstallationModel>? _inMemoryData;

  Future<void> _initData() async {
    if (_inMemoryData == null) {
      final String response = await rootBundle.loadString('assets/mock/installations.json');
      final List<dynamic> data = json.decode(response);
      _inMemoryData = data.map((json) => InstallationModel.fromJson(json)).toList();
    }
  }

  @override
  Future<InstallationModel?> getInstallationByContractId(String contractId) async {
    await Future.delayed(const Duration(milliseconds: 500));
    await _initData();
    try {
      return _inMemoryData!.firstWhere((i) => i.contractId == contractId);
    } catch (_) {
      return null;
    }
  }

  @override
  Future<bool> updateInstallationStatus(String contractId, String status) async {
    await Future.delayed(const Duration(milliseconds: 500));
    await _initData();
    final index = _inMemoryData!.indexWhere((i) => i.contractId == contractId);
    if (index >= 0) {
      _inMemoryData![index].status = status;
      if (status == 'Đã hoàn thành') {
        _inMemoryData![index].actualDate = DateTime.now().toString().split(' ')[0];
      }
      return true;
    }
    return false;
  }

  @override
  Future<bool> completeContract(String contractId) async {
    await Future.delayed(const Duration(milliseconds: 500));
    // Ở mock này chúng ta trả về true. Trạng thái Contract sẽ do ContractProvider xử lý.
    return true;
  }
}