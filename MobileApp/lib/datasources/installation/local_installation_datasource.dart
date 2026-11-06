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
}
