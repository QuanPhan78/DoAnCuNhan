import os

code = """
import 'package:flutter/material.dart';

class InstallationModel {
  final String contractId;
  String status;
  final String? expectedDate;
  String? actualDate;
  final String? assignedStaffName;
  final String? notes;

  InstallationModel({
    required this.contractId,
    required this.status,
    this.expectedDate,
    this.actualDate,
    this.assignedStaffName,
    this.notes,
  });

  factory InstallationModel.fromJson(Map<String, dynamic> json) {
    return InstallationModel(
      contractId: json['contractId'],
      status: json['status'],
      expectedDate: json['expectedDate'],
      actualDate: json['actualDate'],
      assignedStaffName: json['assignedStaffName'],
      notes: json['notes'],
    );
  }

  InstallationModel copyWith({
    String? status,
    String? actualDate,
  }) {
    return InstallationModel(
      contractId: contractId,
      status: status ?? this.status,
      expectedDate: expectedDate,
      actualDate: actualDate ?? this.actualDate,
      assignedStaffName: assignedStaffName,
      notes: notes,
    );
  }
}
"""
os.makedirs("lib/models", exist_ok=True)
with open("lib/models/installation_model.dart", "w", encoding="utf-8") as f:
    f.write(code.strip())

code_ds = """
import '../../models/installation_model.dart';

abstract class InstallationDataSource {
  Future<InstallationModel?> getInstallationByContractId(String contractId);
  Future<bool> updateInstallationStatus(String contractId, String status);
  Future<bool> completeContract(String contractId);
}
"""
os.makedirs("lib/datasources/installation", exist_ok=True)
with open("lib/datasources/installation/installation_datasource.dart", "w", encoding="utf-8") as f:
    f.write(code_ds.strip())

code_local_ds = """
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
"""
with open("lib/datasources/installation/local_installation_datasource.dart", "w", encoding="utf-8") as f:
    f.write(code_local_ds.strip())

code_remote_ds = """
import '../../models/installation_model.dart';
import 'installation_datasource.dart';

class RemoteInstallationDataSource implements InstallationDataSource {
  @override
  Future<InstallationModel?> getInstallationByContractId(String contractId) async {
    throw UnimplementedError();
  }

  @override
  Future<bool> updateInstallationStatus(String contractId, String status) async {
    throw UnimplementedError();
  }

  @override
  Future<bool> completeContract(String contractId) async {
    throw UnimplementedError();
  }
}
"""
with open("lib/datasources/installation/remote_installation_datasource.dart", "w", encoding="utf-8") as f:
    f.write(code_remote_ds.strip())

code_repo = """
import '../models/installation_model.dart';
import '../datasources/installation/installation_datasource.dart';

class InstallationRepository {
  final InstallationDataSource _dataSource;
  InstallationRepository(this._dataSource);

  Future<InstallationModel?> getInstallationByContractId(String contractId) {
    return _dataSource.getInstallationByContractId(contractId);
  }

  Future<bool> confirmInstallation(String contractId) {
    return _dataSource.updateInstallationStatus(contractId, 'Đang thực hiện');
  }

  Future<bool> completeInstallation(String contractId) {
    return _dataSource.updateInstallationStatus(contractId, 'Đã hoàn thành');
  }

  Future<bool> completeContract(String contractId) {
    return _dataSource.completeContract(contractId);
  }
}
"""
with open("lib/repositories/installation_repository.dart", "w", encoding="utf-8") as f:
    f.write(code_repo.strip())

code_prov = """
import 'package:flutter/material.dart';
import '../models/installation_model.dart';
import '../repositories/installation_repository.dart';

class InstallationProvider with ChangeNotifier {
  final InstallationRepository _repository;

  InstallationProvider(this._repository);

  InstallationModel? _currentInstallation;
  bool _isLoading = false;

  InstallationModel? get currentInstallation => _currentInstallation;
  bool get isLoading => _isLoading;

  Future<void> fetchInstallation(String contractId) async {
    _isLoading = true;
    notifyListeners();

    _currentInstallation = await _repository.getInstallationByContractId(contractId);
    
    _isLoading = false;
    notifyListeners();
  }

  Future<bool> confirmInstallation(String contractId) async {
    final success = await _repository.confirmInstallation(contractId);
    if (success) {
      await fetchInstallation(contractId);
    }
    return success;
  }

  Future<bool> completeInstallation(String contractId) async {
    final success = await _repository.completeInstallation(contractId);
    if (success) {
      await fetchInstallation(contractId);
    }
    return success;
  }

  Future<bool> completeContract(String contractId) async {
    return await _repository.completeContract(contractId);
  }
}
"""
os.makedirs("lib/providers", exist_ok=True)
with open("lib/providers/installation_provider.dart", "w", encoding="utf-8") as f:
    f.write(code_prov.strip())