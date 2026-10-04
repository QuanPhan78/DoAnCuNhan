import '../../models/dashboard_model.dart';
import '../../models/role_enum.dart';

abstract class DashboardDataSource {
  Future<DashboardData> getDashboardData(Role role);
}

class LocalDashboardDataSource implements DashboardDataSource {
  @override
  Future<DashboardData> getDashboardData(Role role) async {
    // Simulate network delay
    await Future.delayed(const Duration(seconds: 1));

    switch (role) {
      case Role.customer:
        return DashboardData(
          customerStats: CustomerStats(
            activeContracts: 2,
            expiringContracts: 1,
            processingMaintenance: 0,
            notificationsCount: 3,
            promotions: ['Giảm 20% thuê Laptop', 'Tặng chuột quang khi thuê PC'],
          ),
        );
      case Role.staff:
        return DashboardData(
          staffStats: StaffStats(
            assignedTasks: 5,
            pendingRequests: 2,
            processingRequests: 3,
            completedRequests: 10,
          ),
        );
      case Role.admin:
        return DashboardData(
          adminStats: AdminStats(
            totalDevices: 150,
            rentedDevices: 85,
            totalContracts: 45,
            maintenanceRequests: 4,
            processingTasks: 12,
          ),
        );
    }
  }
}

class DashboardRepository {
  final DashboardDataSource _dataSource;
  DashboardRepository(this._dataSource);

  Future<DashboardData> getDashboardData(Role role) {
    return _dataSource.getDashboardData(role);
  }
}