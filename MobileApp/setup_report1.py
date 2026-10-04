import os
import json

os.makedirs("assets/mock", exist_ok=True)
mock_reports = {
  "deviceStats": {
    "total": 120,
    "available": 50,
    "rented": 60,
    "maintenance": 8,
    "broken": 2
  },
  "contractStats": {
    "total": 60,
    "active": 45,
    "completed": 15
  },
  "maintenanceStats": {
    "total": 25,
    "processing": 5,
    "completed": 20
  },
  "revenue": 150000000, 
  "revenueChart": [
    {"label": "T1", "value": 15000000},
    {"label": "T2", "value": 18000000},
    {"label": "T3", "value": 22000000},
    {"label": "T4", "value": 20000000},
    {"label": "T5", "value": 25000000},
    {"label": "T6", "value": 30000000}
  ]
}

with open("assets/mock/reports.json", "w", encoding="utf-8") as f:
    json.dump(mock_reports, f, ensure_ascii=False, indent=2)

os.makedirs("lib/models", exist_ok=True)
model_code = """class ChartData {
  final String label;
  final double value;

  ChartData({required this.label, required this.value});

  factory ChartData.fromJson(Map<String, dynamic> json) {
    return ChartData(
      label: json['label'] ?? '',
      value: (json['value'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class ReportModel {
  final int totalDevices;
  final int availableDevices;
  final int rentedDevices;
  final int maintenanceDevices;
  final int brokenDevices;

  final int totalContracts;
  final int activeContracts;
  final int completedContracts;

  final int totalMaintenances;
  final int processingMaintenances;
  final int completedMaintenances;

  final double? revenue;
  final List<ChartData> revenueChart;

  ReportModel({
    required this.totalDevices,
    required this.availableDevices,
    required this.rentedDevices,
    required this.maintenanceDevices,
    required this.brokenDevices,
    required this.totalContracts,
    required this.activeContracts,
    required this.completedContracts,
    required this.totalMaintenances,
    required this.processingMaintenances,
    required this.completedMaintenances,
    this.revenue,
    this.revenueChart = const [],
  });

  factory ReportModel.fromJson(Map<String, dynamic> json) {
    final dev = json['deviceStats'] ?? {};
    final con = json['contractStats'] ?? {};
    final main = json['maintenanceStats'] ?? {};
    
    return ReportModel(
      totalDevices: dev['total'] ?? 0,
      availableDevices: dev['available'] ?? 0,
      rentedDevices: dev['rented'] ?? 0,
      maintenanceDevices: dev['maintenance'] ?? 0,
      brokenDevices: dev['broken'] ?? 0,
      
      totalContracts: con['total'] ?? 0,
      activeContracts: con['active'] ?? 0,
      completedContracts: con['completed'] ?? 0,
      
      totalMaintenances: main['total'] ?? 0,
      processingMaintenances: main['processing'] ?? 0,
      completedMaintenances: main['completed'] ?? 0,
      
      revenue: (json['revenue'] as num?)?.toDouble(),
      revenueChart: (json['revenueChart'] as List?)?.map((e) => ChartData.fromJson(e)).toList() ?? [],
    );
  }
}
"""
with open("lib/models/report_model.dart", "w", encoding="utf-8") as f: f.write(model_code.strip())

os.makedirs("lib/datasources/report", exist_ok=True)
ds_abs = """import '../../models/report_model.dart';

abstract class ReportDataSource {
  Future<ReportModel> getReports(String timeFilter);
}
"""
with open("lib/datasources/report/report_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_abs.strip())

ds_loc = """import 'dart:convert';
import 'package:flutter/services.dart';
import '../../models/report_model.dart';
import 'report_datasource.dart';

class LocalReportDataSource implements ReportDataSource {
  @override
  Future<ReportModel> getReports(String timeFilter) async {
    await Future.delayed(const Duration(milliseconds: 600)); // Mock network
    final String response = await rootBundle.loadString('assets/mock/reports.json');
    final data = json.decode(response);
    
    // Simulate filtering by time
    if (timeFilter == 'Tháng này') {
      // Return data as is
      return ReportModel.fromJson(data);
    } else if (timeFilter == 'Năm nay') {
      // Modify data slightly to mock year filter
      data['revenue'] = (data['revenue'] as num?) == null ? null : (data['revenue'] as num) * 5;
      data['deviceStats']['rented'] = 80;
      return ReportModel.fromJson(data);
    }
    
    return ReportModel.fromJson(data);
  }
}
"""
with open("lib/datasources/report/local_report_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_loc.strip())

ds_rem = """import '../../models/report_model.dart';
import 'report_datasource.dart';

class RemoteReportDataSource implements ReportDataSource {
  @override
  Future<ReportModel> getReports(String timeFilter) async {
    throw UnimplementedError('API chưa có sẵn');
  }
}
"""
with open("lib/datasources/report/remote_report_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_rem.strip())

os.makedirs("lib/repositories", exist_ok=True)
repo = """import '../models/report_model.dart';
import '../datasources/report/report_datasource.dart';

class ReportRepository {
  final ReportDataSource _dataSource;
  ReportRepository(this._dataSource);

  Future<ReportModel> getReports(String timeFilter) {
    return _dataSource.getReports(timeFilter);
  }
}
"""
with open("lib/repositories/report_repository.dart", "w", encoding="utf-8") as f: f.write(repo.strip())

os.makedirs("lib/providers", exist_ok=True)
prov = """import 'package:flutter/material.dart';
import '../models/report_model.dart';
import '../repositories/report_repository.dart';

class ReportProvider with ChangeNotifier {
  final ReportRepository _repository;
  ReportProvider(this._repository);

  ReportModel? _reportData;
  bool _isLoading = false;
  String? _errorMessage;
  String _currentTimeFilter = 'Tháng này';

  ReportModel? get reportData => _reportData;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  String get currentTimeFilter => _currentTimeFilter;

  Future<void> fetchReports({String? timeFilter}) async {
    if (timeFilter != null) {
      _currentTimeFilter = timeFilter;
    }
    
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _reportData = await _repository.getReports(_currentTimeFilter);
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
"""
with open("lib/providers/report_provider.dart", "w", encoding="utf-8") as f: f.write(prov.strip())

def insert_provider(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "ReportProvider" not in content:
        import_str = "import 'package:quan_ly_cho_thue_thiet_bi/providers/report_provider.dart';\nimport 'package:quan_ly_cho_thue_thiet_bi/repositories/report_repository.dart';\nimport 'package:quan_ly_cho_thue_thiet_bi/datasources/report/local_report_datasource.dart';\n"
        if "package:quan_ly_cho_thue_thiet_bi" not in content and "main.dart" in file_path:
            import_str = "import 'providers/report_provider.dart';\nimport 'repositories/report_repository.dart';\nimport 'datasources/report/local_report_datasource.dart';\n"
        content = import_str + content
        provider_str = """
          ChangeNotifierProvider(
            create: (_) => ReportProvider(
              ReportRepository(LocalReportDataSource()),
            ),
          ),"""
        content = content.replace("providers: [", "providers: [" + provider_str)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

insert_provider("lib/main.dart")
insert_provider("test/widget_test.dart")

print("Report Layer Generated Successfully")