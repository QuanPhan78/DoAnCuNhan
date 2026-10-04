import os

os.makedirs("lib/models/search", exist_ok=True)
model_code = """
class SearchResultModel {
  final String id;
  final String type; // 'device', 'contract', 'incident', 'maintenance'
  final String title;
  final String subtitle;
  final String? status;
  final dynamic originalData; // The actual Model object

  SearchResultModel({
    required this.id,
    required this.type,
    required this.title,
    required this.subtitle,
    this.status,
    required this.originalData,
  });
}
"""
with open("lib/models/search/search_result_model.dart", "w", encoding="utf-8") as f: f.write(model_code.strip())

os.makedirs("lib/datasources/search", exist_ok=True)
ds_abs = """import '../../models/search/search_result_model.dart';
import '../../models/role_enum.dart';

abstract class SearchDataSource {
  Future<List<SearchResultModel>> search(String query, {String filterType = 'all', String? userId, Role? role});
}
"""
with open("lib/datasources/search/search_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_abs.strip())

ds_loc = """import 'dart:convert';
import 'package:flutter/services.dart';
import '../../models/search/search_result_model.dart';
import '../../models/device_model.dart';
import '../../models/contract_model.dart';
import '../../models/incident_model.dart';
import '../../models/maintenance_model.dart';
import '../../models/role_enum.dart';
import 'search_datasource.dart';

class LocalSearchDataSource implements SearchDataSource {
  @override
  Future<List<SearchResultModel>> search(String query, {String filterType = 'all', String? userId, Role? role}) async {
    await Future.delayed(const Duration(milliseconds: 400));
    final String lowerQuery = query.toLowerCase().trim();
    List<SearchResultModel> results = [];

    // 1. Load Data
    final devicesRaw = json.decode(await rootBundle.loadString('assets/mock/devices.json')) as List;
    final contractsRaw = json.decode(await rootBundle.loadString('assets/mock/contracts.json')) as List;
    final incidentsRaw = json.decode(await rootBundle.loadString('assets/mock/incidents.json')) as List;
    final maintenancesRaw = json.decode(await rootBundle.loadString('assets/mock/maintenances.json')) as List;

    // 2. Parse & Filter Devices
    if (filterType == 'all' || filterType == 'device') {
      for (var raw in devicesRaw) {
        final d = DeviceModel.fromJson(raw);
        final match = d.name.toLowerCase().contains(lowerQuery) ||
            d.code.toLowerCase().contains(lowerQuery) ||
            (d.type?.toLowerCase().contains(lowerQuery) ?? false) ||
            (d.brand?.toLowerCase().contains(lowerQuery) ?? false) ||
            (d.model?.toLowerCase().contains(lowerQuery) ?? false) ||
            (d.rentalStatus?.toLowerCase().contains(lowerQuery) ?? false);
        
        if (match) {
          results.add(SearchResultModel(
            id: d.id,
            type: 'device',
            title: d.name,
            subtitle: 'Mã: ${d.code} - ${d.brand ?? ''}',
            status: d.rentalStatus,
            originalData: d,
          ));
        }
      }
    }

    // 3. Parse & Filter Contracts
    if (filterType == 'all' || filterType == 'contract') {
      for (var raw in contractsRaw) {
        final c = ContractModel.fromJson(raw);
        // Security check for Customer
        if (role == Role.customer && c.customerId != userId) continue;

        final match = (c.contractCode?.toLowerCase().contains(lowerQuery) ?? false) ||
            (c.customerName?.toLowerCase().contains(lowerQuery) ?? false) ||
            (c.deviceIds?.any((id) => id.toLowerCase().contains(lowerQuery)) ?? false);
        
        if (match) {
          results.add(SearchResultModel(
            id: c.id,
            type: 'contract',
            title: c.contractCode ?? 'Hợp đồng vô danh',
            subtitle: 'KH: ${c.customerName ?? 'N/A'}',
            status: c.status,
            originalData: c,
          ));
        }
      }
    }

    // 4. Parse & Filter Incidents
    if (filterType == 'all' || filterType == 'incident') {
      for (var raw in incidentsRaw) {
        final inc = IncidentModel.fromJson(raw);
        // Customer check (Assuming contract IDs would be checked in a real app, here we just allow it for mock or strict filter)
        // Simplified mock security
        final match = inc.code.toLowerCase().contains(lowerQuery) ||
            inc.issueType.toLowerCase().contains(lowerQuery) ||
            inc.description.toLowerCase().contains(lowerQuery) ||
            inc.contractId.toLowerCase().contains(lowerQuery);
        
        if (match) {
          results.add(SearchResultModel(
            id: inc.id,
            type: 'incident',
            title: inc.code,
            subtitle: inc.issueType,
            status: inc.status,
            originalData: inc,
          ));
        }
      }
    }

    // 5. Parse & Filter Maintenances
    if (filterType == 'all' || filterType == 'maintenance') {
      for (var raw in maintenancesRaw) {
        final m = MaintenanceModel.fromJson(raw);
        final match = (m.requestCode?.toLowerCase().contains(lowerQuery) ?? false) ||
            (m.customer?.toLowerCase().contains(lowerQuery) ?? false) ||
            (m.description?.toLowerCase().contains(lowerQuery) ?? false) ||
            (m.assignedEmployee?.toLowerCase().contains(lowerQuery) ?? false);
        
        if (match) {
          results.add(SearchResultModel(
            id: m.id,
            type: 'maintenance',
            title: m.requestCode ?? 'N/A',
            subtitle: 'KH: ${m.customer ?? 'N/A'}',
            status: m.status,
            originalData: m,
          ));
        }
      }
    }

    return results;
  }
}
"""
with open("lib/datasources/search/local_search_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_loc.strip().replace(r'${', '${'))

ds_rem = """import '../../models/search/search_result_model.dart';
import '../../models/role_enum.dart';
import 'search_datasource.dart';

class RemoteSearchDataSource implements SearchDataSource {
  @override
  Future<List<SearchResultModel>> search(String query, {String filterType = 'all', String? userId, Role? role}) async {
    throw UnimplementedError('API chưa có sẵn');
  }
}
"""
with open("lib/datasources/search/remote_search_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_rem.strip())

os.makedirs("lib/repositories", exist_ok=True)
repo = """import '../models/search/search_result_model.dart';
import '../models/role_enum.dart';
import '../datasources/search/search_datasource.dart';

class SearchRepository {
  final SearchDataSource _dataSource;
  SearchRepository(this._dataSource);

  Future<List<SearchResultModel>> search(String query, {String filterType = 'all', String? userId, Role? role}) {
    return _dataSource.search(query, filterType: filterType, userId: userId, role: role);
  }
}
"""
with open("lib/repositories/search_repository.dart", "w", encoding="utf-8") as f: f.write(repo.strip())

os.makedirs("lib/providers", exist_ok=True)
prov = """import 'dart:async';
import 'package:flutter/material.dart';
import '../models/search/search_result_model.dart';
import '../models/role_enum.dart';
import '../repositories/search_repository.dart';

class SearchProvider with ChangeNotifier {
  final SearchRepository _repository;
  SearchProvider(this._repository);

  List<SearchResultModel> _results = [];
  bool _isLoading = false;
  String? _errorMessage;
  String _currentQuery = '';
  String _currentFilter = 'all';

  Timer? _debounce;

  List<SearchResultModel> get results => _results;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  String get currentQuery => _currentQuery;
  String get currentFilter => _currentFilter;

  void setFilter(String filter, String? userId, Role? role) {
    _currentFilter = filter;
    if (_currentQuery.isNotEmpty) {
      search(_currentQuery, userId: userId, role: role);
    } else {
      _results = [];
      notifyListeners();
    }
  }

  void onSearchChanged(String query, String? userId, Role? role) {
    _currentQuery = query;
    if (_debounce?.isActive ?? false) _debounce!.cancel();
    
    if (query.trim().isEmpty) {
      _results = [];
      _isLoading = false;
      _errorMessage = null;
      notifyListeners();
      return;
    }

    _debounce = Timer(const Duration(milliseconds: 500), () {
      search(query, userId: userId, role: role);
    });
  }

  Future<void> search(String query, {String? userId, Role? role}) async {
    if (query.trim().isEmpty) return;
    
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _results = await _repository.search(query, filterType: _currentFilter, userId: userId, role: role);
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void clearSearch() {
    if (_debounce?.isActive ?? false) _debounce!.cancel();
    _currentQuery = '';
    _results = [];
    _isLoading = false;
    _errorMessage = null;
    notifyListeners();
  }
}
"""
with open("lib/providers/search_provider.dart", "w", encoding="utf-8") as f: f.write(prov.strip())

def insert_provider(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "SearchProvider" not in content:
        import_str = "import 'package:quan_ly_cho_thue_thiet_bi/providers/search_provider.dart';\nimport 'package:quan_ly_cho_thue_thiet_bi/repositories/search_repository.dart';\nimport 'package:quan_ly_cho_thue_thiet_bi/datasources/search/local_search_datasource.dart';\n"
        if "package:quan_ly_cho_thue_thiet_bi" not in content and "main.dart" in file_path:
            import_str = "import 'providers/search_provider.dart';\nimport 'repositories/search_repository.dart';\nimport 'datasources/search/local_search_datasource.dart';\n"
        content = import_str + content
        provider_str = """
          ChangeNotifierProvider(
            create: (_) => SearchProvider(
              SearchRepository(LocalSearchDataSource()),
            ),
          ),"""
        content = content.replace("providers: [", "providers: [" + provider_str)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

insert_provider("lib/main.dart")
insert_provider("test/widget_test.dart")

print("Search Layer Generated Successfully")