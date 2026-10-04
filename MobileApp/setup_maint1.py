import os
import json

os.makedirs("assets/mock", exist_ok=True)
mock_maintenances = [
    {
        "id": "M001",
        "requestCode": "INC-2026-001",
        "contractId": "C001",
        "deviceId": "1",
        "customer": "Nguyễn Khách Hàng",
        "description": "Bật máy không thấy màn hình sáng, quạt không quay.",
        "status": "Đang xử lý",
        "assignedEmployee": "Trần Nhân Viên",
        "createdAt": "05/09/2026 09:00",
        "completedAt": "",
        "result": "",
        "notes": [
            {"time": "05/09/2026 09:15", "content": "Đã tiếp nhận yêu cầu", "author": "Trần Nhân Viên"},
            {"time": "05/09/2026 10:00", "content": "Kiểm tra thấy cháy nguồn, cần thay thế", "author": "Trần Nhân Viên"}
        ]
    },
    {
        "id": "M002",
        "requestCode": "INC-2026-002",
        "contractId": "C001",
        "deviceId": "2",
        "customer": "Nguyễn Khách Hàng",
        "description": "Máy in không nhận lệnh in từ Windows 11.",
        "status": "Chờ tiếp nhận",
        "assignedEmployee": "",
        "createdAt": "10/09/2026 14:30",
        "completedAt": "",
        "result": "",
        "notes": []
    }
]

with open("assets/mock/maintenances.json", "w", encoding="utf-8") as f:
    json.dump(mock_maintenances, f, ensure_ascii=False, indent=2)

os.makedirs("lib/models", exist_ok=True)
model_code = """class MaintenanceNote {
  final String time;
  final String content;
  final String author;

  MaintenanceNote({required this.time, required this.content, required this.author});

  factory MaintenanceNote.fromJson(Map<String, dynamic> json) {
    return MaintenanceNote(
      time: json['time'] ?? '',
      content: json['content'] ?? '',
      author: json['author'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {'time': time, 'content': content, 'author': author};
  }
}

class MaintenanceModel {
  final String id;
  final String? requestCode;
  final String? contractId;
  final String? deviceId;
  final String? customer;
  final String? description;
  String? status;
  String? assignedEmployee;
  final String? createdAt;
  String? completedAt;
  String? result;
  List<MaintenanceNote> notes;

  MaintenanceModel({
    required this.id,
    this.requestCode,
    this.contractId,
    this.deviceId,
    this.customer,
    this.description,
    this.status,
    this.assignedEmployee,
    this.createdAt,
    this.completedAt,
    this.result,
    this.notes = const [],
  });

  factory MaintenanceModel.fromJson(Map<String, dynamic> json) {
    return MaintenanceModel(
      id: json['id'],
      requestCode: json['requestCode'],
      contractId: json['contractId'],
      deviceId: json['deviceId'],
      customer: json['customer'],
      description: json['description'],
      status: json['status'],
      assignedEmployee: json['assignedEmployee'],
      createdAt: json['createdAt'],
      completedAt: json['completedAt'],
      result: json['result'],
      notes: (json['notes'] as List?)?.map((n) => MaintenanceNote.fromJson(n)).toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'requestCode': requestCode,
      'contractId': contractId,
      'deviceId': deviceId,
      'customer': customer,
      'description': description,
      'status': status,
      'assignedEmployee': assignedEmployee,
      'createdAt': createdAt,
      'completedAt': completedAt,
      'result': result,
      'notes': notes.map((n) => n.toJson()).toList(),
    };
  }
}
"""
with open("lib/models/maintenance_model.dart", "w", encoding="utf-8") as f: f.write(model_code.strip())

os.makedirs("lib/datasources/maintenance", exist_ok=True)
ds_abs = """import '../../models/maintenance_model.dart';
import '../../models/role_enum.dart';

abstract class MaintenanceDataSource {
  Future<List<MaintenanceModel>> getMaintenances(String userId, Role role, String userName);
  Future<bool> updateMaintenance(MaintenanceModel maintenance);
}
"""
with open("lib/datasources/maintenance/maintenance_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_abs.strip())

ds_loc = """import 'dart:convert';
import 'package:flutter/services.dart';
import '../../models/maintenance_model.dart';
import '../../models/role_enum.dart';
import 'maintenance_datasource.dart';

class LocalMaintenanceDataSource implements MaintenanceDataSource {
  static List<MaintenanceModel>? _inMemoryData;

  Future<void> _initData() async {
    if (_inMemoryData == null) {
      final String response = await rootBundle.loadString('assets/mock/maintenances.json');
      final List<dynamic> data = json.decode(response);
      _inMemoryData = data.map((json) => MaintenanceModel.fromJson(json)).toList();
    }
  }

  @override
  Future<List<MaintenanceModel>> getMaintenances(String userId, Role role, String userName) async {
    await Future.delayed(const Duration(milliseconds: 500));
    await _initData();
    if (role == Role.customer) {
      return _inMemoryData!.where((m) => m.customer != null && m.customer!.contains('Nguyễn Khách Hàng')).toList(); // Mock filtering
    } else if (role == Role.staff) {
      // Return all or assigned to this staff, for mock let's return all so they can take unassigned ones
      return _inMemoryData!;
    }
    return _inMemoryData!;
  }

  @override
  Future<bool> updateMaintenance(MaintenanceModel maintenance) async {
    await Future.delayed(const Duration(milliseconds: 500));
    await _initData();
    final index = _inMemoryData!.indexWhere((m) => m.id == maintenance.id);
    if (index >= 0) {
      _inMemoryData![index] = maintenance;
      return true;
    }
    return false;
  }
}
"""
with open("lib/datasources/maintenance/local_maintenance_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_loc.strip())

ds_rem = """import '../../models/maintenance_model.dart';
import '../../models/role_enum.dart';
import 'maintenance_datasource.dart';

class RemoteMaintenanceDataSource implements MaintenanceDataSource {
  @override
  Future<List<MaintenanceModel>> getMaintenances(String userId, Role role, String userName) async {
    throw UnimplementedError('API chưa có sẵn');
  }
  @override
  Future<bool> updateMaintenance(MaintenanceModel maintenance) async {
    throw UnimplementedError('API chưa có sẵn');
  }
}
"""
with open("lib/datasources/maintenance/remote_maintenance_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_rem.strip())

os.makedirs("lib/repositories", exist_ok=True)
repo = """import '../models/maintenance_model.dart';
import '../models/role_enum.dart';
import '../datasources/maintenance/maintenance_datasource.dart';

class MaintenanceRepository {
  final MaintenanceDataSource _dataSource;
  MaintenanceRepository(this._dataSource);

  Future<List<MaintenanceModel>> getMaintenances(String userId, Role role, String userName) {
    return _dataSource.getMaintenances(userId, role, userName);
  }
  Future<bool> updateMaintenance(MaintenanceModel maintenance) {
    return _dataSource.updateMaintenance(maintenance);
  }
}
"""
with open("lib/repositories/maintenance_repository.dart", "w", encoding="utf-8") as f: f.write(repo.strip())

os.makedirs("lib/providers", exist_ok=True)
prov = """import 'package:flutter/material.dart';
import '../models/maintenance_model.dart';
import '../models/role_enum.dart';
import '../repositories/maintenance_repository.dart';

class MaintenanceProvider with ChangeNotifier {
  final MaintenanceRepository _repository;
  MaintenanceProvider(this._repository);

  List<MaintenanceModel> _maintenances = [];
  bool _isLoading = false;
  String? _errorMessage;

  List<MaintenanceModel> get maintenances => _maintenances;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  Future<void> fetchMaintenances(String userId, Role role, String userName) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    try {
      _maintenances = await _repository.getMaintenances(userId, role, userName);
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> updateMaintenance(MaintenanceModel updated) async {
    try {
      final success = await _repository.updateMaintenance(updated);
      if (success) {
        final index = _maintenances.indexWhere((m) => m.id == updated.id);
        if (index >= 0) {
          _maintenances[index] = updated;
          notifyListeners();
        }
      }
      return success;
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }
}
"""
with open("lib/providers/maintenance_provider.dart", "w", encoding="utf-8") as f: f.write(prov.strip())

print("Maintenance data layer set up")