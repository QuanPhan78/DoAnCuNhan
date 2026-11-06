import 'dart:convert';
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