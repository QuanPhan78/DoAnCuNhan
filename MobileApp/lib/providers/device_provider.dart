import 'package:flutter/material.dart';
import '../models/device_model.dart';
import '../repositories/device_repository.dart';

class DeviceProvider with ChangeNotifier {
  final DeviceRepository _repository;

  DeviceProvider(this._repository);

  List<DeviceModel> _allDevices = [];
  List<DeviceModel> _filteredDevices = [];
  
  bool _isLoading = false;
  String? _errorMessage;
  
  String _searchQuery = '';
  String? _selectedType;
  String? _selectedStatus;

  List<DeviceModel> get devices => _filteredDevices;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  List<String> get availableTypes => _allDevices.map((d) => d.type).toSet().toList();
  List<String> get availableStatuses => _allDevices.map((d) => d.rentalStatus ?? 'Khác').toSet().toList();

  String? get selectedType => _selectedType;
  String? get selectedStatus => _selectedStatus;
  String get searchQuery => _searchQuery;

  Future<void> fetchDevices() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _allDevices = await _repository.getAllDevices();
      _applyFilters();
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void search(String query) {
    _searchQuery = query;
    _applyFilters();
  }

  void setTypeFilter(String? type) {
    _selectedType = type;
    _applyFilters();
  }

  void setStatusFilter(String? status) {
    _selectedStatus = status;
    _applyFilters();
  }

  void _applyFilters() {
    _filteredDevices = _allDevices.where((device) {
      final matchesSearch = device.name.toLowerCase().contains(_searchQuery.toLowerCase()) || 
                            (device.code?.toLowerCase().contains(_searchQuery.toLowerCase()) ?? false);
      final matchesType = _selectedType == null || device.type == _selectedType;
      final matchesStatus = _selectedStatus == null || device.rentalStatus == _selectedStatus;
      
      return matchesSearch && matchesType && matchesStatus;
    }).toList();
    notifyListeners();
  }
}
