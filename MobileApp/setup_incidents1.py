import os
import json

# Create incidents JSON
os.makedirs("assets/mock", exist_ok=True)
incidents = [
    {
        "id": "I001",
        "code": "INC-2026-001",
        "contractId": "C001",
        "deviceId": "1",
        "issueType": "Không lên nguồn",
        "description": "Bật máy không thấy màn hình sáng, quạt không quay.",
        "severity": "Nghiêm trọng",
        "occurrenceTime": "05/09/2026 08:00",
        "status": "Chờ xử lý",
        "assignedStaff": "",
        "createdAt": "05/09/2026 08:30",
        "attachments": []
    },
    {
        "id": "I002",
        "code": "INC-2026-002",
        "contractId": "C001",
        "deviceId": "2",
        "issueType": "Lỗi phần mềm",
        "description": "Máy in không nhận lệnh in từ Windows 11.",
        "severity": "Trung bình",
        "occurrenceTime": "10/09/2026 14:00",
        "status": "Đang xử lý",
        "assignedStaff": "Trần Nhân Viên",
        "createdAt": "10/09/2026 14:15",
        "attachments": [
            {
                "id": "A001",
                "localPath": "assets/images/placeholder.png",
                "url": "",
                "type": "image"
            }
        ]
    }
]
with open("assets/mock/incidents.json", "w", encoding="utf-8") as f:
    json.dump(incidents, f, ensure_ascii=False, indent=2)

# Models
os.makedirs("lib/models", exist_ok=True)
att_model = """class AttachmentModel {
  final String id;
  final String? localPath;
  final String? url;
  final String type; // 'image', 'document', etc.

  AttachmentModel({
    required this.id,
    this.localPath,
    this.url,
    this.type = 'image',
  });

  factory AttachmentModel.fromJson(Map<String, dynamic> json) {
    return AttachmentModel(
      id: json['id'],
      localPath: json['localPath'],
      url: json['url'],
      type: json['type'] ?? 'image',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'localPath': localPath,
      'url': url,
      'type': type,
    };
  }
}
"""
with open("lib/models/attachment_model.dart", "w", encoding="utf-8") as f: f.write(att_model.strip())

inc_model = """import 'attachment_model.dart';

class IncidentModel {
  final String id;
  final String code;
  final String contractId;
  final String deviceId;
  final String issueType;
  final String description;
  final String severity;
  final String occurrenceTime;
  final String status; // Chờ xử lý, Đang xử lý, Đã hoàn thành
  final String? assignedStaff;
  final String createdAt;
  final List<AttachmentModel> attachments;

  IncidentModel({
    required this.id,
    required this.code,
    required this.contractId,
    required this.deviceId,
    required this.issueType,
    required this.description,
    required this.severity,
    required this.occurrenceTime,
    required this.status,
    this.assignedStaff,
    required this.createdAt,
    this.attachments = const [],
  });

  factory IncidentModel.fromJson(Map<String, dynamic> json) {
    return IncidentModel(
      id: json['id'],
      code: json['code'],
      contractId: json['contractId'],
      deviceId: json['deviceId'],
      issueType: json['issueType'],
      description: json['description'],
      severity: json['severity'],
      occurrenceTime: json['occurrenceTime'],
      status: json['status'],
      assignedStaff: json['assignedStaff'],
      createdAt: json['createdAt'],
      attachments: (json['attachments'] as List?)
              ?.map((e) => AttachmentModel.fromJson(e))
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'code': code,
      'contractId': contractId,
      'deviceId': deviceId,
      'issueType': issueType,
      'description': description,
      'severity': severity,
      'occurrenceTime': occurrenceTime,
      'status': status,
      'assignedStaff': assignedStaff,
      'createdAt': createdAt,
      'attachments': attachments.map((e) => e.toJson()).toList(),
    };
  }
}
"""
with open("lib/models/incident_model.dart", "w", encoding="utf-8") as f: f.write(inc_model.strip())

# DataSource
os.makedirs("lib/datasources/incident", exist_ok=True)
ds_abs = """import '../../models/incident_model.dart';

abstract class IncidentDataSource {
  Future<List<IncidentModel>> getIncidents(String userId, String role);
  Future<IncidentModel> createIncident(IncidentModel incident);
}
"""
with open("lib/datasources/incident/incident_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_abs.strip())

ds_loc = """import 'dart:convert';
import 'package:flutter/services.dart';
import '../../models/incident_model.dart';
import 'incident_datasource.dart';

class LocalIncidentDataSource implements IncidentDataSource {
  static List<IncidentModel>? _inMemoryData;

  Future<void> _initData() async {
    if (_inMemoryData == null) {
      final String response = await rootBundle.loadString('assets/mock/incidents.json');
      final List<dynamic> data = json.decode(response);
      _inMemoryData = data.map((json) => IncidentModel.fromJson(json)).toList();
    }
  }

  @override
  Future<List<IncidentModel>> getIncidents(String userId, String role) async {
    await Future.delayed(const Duration(milliseconds: 500));
    await _initData();
    // For mock: customer sees their own (filtering in provider or here, we do it in provider)
    return _inMemoryData!;
  }

  @override
  Future<IncidentModel> createIncident(IncidentModel incident) async {
    await Future.delayed(const Duration(milliseconds: 500));
    await _initData();
    _inMemoryData!.insert(0, incident); // Thêm vào đầu
    return incident;
  }
}
"""
with open("lib/datasources/incident/local_incident_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_loc.strip())

ds_rem = """import '../../models/incident_model.dart';
import 'incident_datasource.dart';

class RemoteIncidentDataSource implements IncidentDataSource {
  @override
  Future<List<IncidentModel>> getIncidents(String userId, String role) async {
    throw UnimplementedError('API chưa có sẵn');
  }

  @override
  Future<IncidentModel> createIncident(IncidentModel incident) async {
    throw UnimplementedError();
  }
}
"""
with open("lib/datasources/incident/remote_incident_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_rem.strip())

# Repo
os.makedirs("lib/repositories", exist_ok=True)
repo = """import '../models/incident_model.dart';
import '../datasources/incident/incident_datasource.dart';

class IncidentRepository {
  final IncidentDataSource _dataSource;
  IncidentRepository(this._dataSource);

  Future<List<IncidentModel>> getIncidents(String userId, String role) {
    return _dataSource.getIncidents(userId, role);
  }

  Future<IncidentModel> createIncident(IncidentModel incident) {
    return _dataSource.createIncident(incident);
  }
}
"""
with open("lib/repositories/incident_repository.dart", "w", encoding="utf-8") as f: f.write(repo.strip())

# Provider
os.makedirs("lib/providers", exist_ok=True)
prov = """import 'package:flutter/material.dart';
import '../models/incident_model.dart';
import '../models/role_enum.dart';
import '../repositories/incident_repository.dart';
import '../providers/contract_provider.dart'; // Để tra cứu contract nếu cần

class IncidentProvider with ChangeNotifier {
  final IncidentRepository _repository;
  IncidentProvider(this._repository);

  List<IncidentModel> _incidents = [];
  bool _isLoading = false;
  String? _errorMessage;

  List<IncidentModel> get incidents => _incidents;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  Future<void> fetchIncidents(String userId, Role role, ContractProvider contractProvider) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final all = await _repository.getIncidents(userId, role.toString());
      if (role == Role.customer) {
        // Chỉ lấy các sự cố thuộc về hợp đồng của customer này.
        // Thực tế backend sẽ handle. Ở mock, ta filter thông qua contractProvider
        final customerContractIds = contractProvider.contracts.where((c) => c.customerId == userId).map((c) => c.id).toList();
        _incidents = all.where((i) => customerContractIds.contains(i.contractId)).toList();
      } else {
        _incidents = all;
      }
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> createIncident(IncidentModel incident) async {
    try {
      await _repository.createIncident(incident);
      // add locally to avoid re-fetch if we want
      _incidents.insert(0, incident);
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }
}
"""
with open("lib/providers/incident_provider.dart", "w", encoding="utf-8") as f: f.write(prov.strip())

print("Incident layer models setup complete")