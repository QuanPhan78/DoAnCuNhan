import 'dart:convert';
import '../services/api_session.dart';
import '../../models/dashboard_model.dart';
import '../../models/role_enum.dart';
import '../services/api_config.dart';

abstract class DashboardDataSource {
  Future<DashboardData> getDashboardData(Role role, {String? userId});
}

class RemoteDashboardDataSource implements DashboardDataSource {
  final String? _baseUrl;
  String get baseUrl => _baseUrl ?? ApiConfig.baseUrl;

  RemoteDashboardDataSource({String? baseUrl}) : _baseUrl = baseUrl;

  @override
  Future<DashboardData> getDashboardData(Role role, {String? userId}) async {
    try {
      final url = Uri.parse('$baseUrl/dashboard/stats');
      final response = await ApiSession.get(url);

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        final c = data['customerStats'] ?? {};
        final s = data['staffStats'] ?? {};
        final a = data['adminStats'] ?? {};

        final promoList = (c['promotions'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [];

        return DashboardData(
          customerStats: CustomerStats(
            activeContracts: c['activeContracts'] ?? 0,
            expiringContracts: c['expiringContracts'] ?? 0,
            processingMaintenance: c['processingMaintenance'] ?? 0,
            notificationsCount: c['notificationsCount'] ?? 0,
            promotions: promoList,
          ),
          staffStats: StaffStats(
            assignedTasks: s['assignedTasks'] ?? 0,
            pendingRequests: s['pendingRequests'] ?? 0,
            processingRequests: s['processingRequests'] ?? 0,
            completedRequests: s['completedRequests'] ?? 0,
          ),
          adminStats: AdminStats(
            totalDevices: a['totalDevices'] ?? 0,
            rentedDevices: a['rentedDevices'] ?? 0,
            totalContracts: a['totalContracts'] ?? 0,
            maintenanceRequests: a['maintenanceRequests'] ?? 0,
            processingTasks: a['processingTasks'] ?? 0,
          ),
        );
      }
    } catch (_) {}
    return LocalDashboardDataSource().getDashboardData(role, userId: userId);
  }
}

class LocalDashboardDataSource implements DashboardDataSource {
  @override
  Future<DashboardData> getDashboardData(Role role, {String? userId}) async {
    await Future.delayed(const Duration(milliseconds: 300));

    switch (role) {
      case Role.customer:
        return DashboardData(
          customerStats: CustomerStats(
            activeContracts: 0,
            expiringContracts: 0,
            processingMaintenance: 0,
            notificationsCount: 0,
            promotions: ['Giảm 20% thuê Laptop', 'Tặng chuột quang khi thuê PC'],
          ),
        );
      case Role.staff:
        return DashboardData(
          staffStats: StaffStats(
            assignedTasks: 2,
            pendingRequests: 2,
            processingRequests: 0,
            completedRequests: 0,
          ),
        );
      case Role.admin:
        return DashboardData(
          adminStats: AdminStats(
            totalDevices: 11,
            rentedDevices: 0,
            totalContracts: 4,
            maintenanceRequests: 1,
            processingTasks: 2,
          ),
        );
    }
  }
}

class DashboardRepository {
  final DashboardDataSource _dataSource;
  DashboardRepository(this._dataSource);

  Future<DashboardData> getDashboardData(Role role, {String? userId}) {
    return _dataSource.getDashboardData(role, userId: userId);
  }
}
