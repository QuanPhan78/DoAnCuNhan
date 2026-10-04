class DashboardData {
  final CustomerStats? customerStats;
  final StaffStats? staffStats;
  final AdminStats? adminStats;
  
  DashboardData({this.customerStats, this.staffStats, this.adminStats});
}

class CustomerStats {
  final int activeContracts;
  final int expiringContracts;
  final int processingMaintenance;
  final int notificationsCount;
  final List<String> promotions;

  CustomerStats({
    required this.activeContracts,
    required this.expiringContracts,
    required this.processingMaintenance,
    required this.notificationsCount,
    required this.promotions,
  });
}

class StaffStats {
  final int assignedTasks;
  final int pendingRequests;
  final int processingRequests;
  final int completedRequests;

  StaffStats({
    required this.assignedTasks,
    required this.pendingRequests,
    required this.processingRequests,
    required this.completedRequests,
  });
}

class AdminStats {
  final int totalDevices;
  final int rentedDevices;
  final int totalContracts;
  final int maintenanceRequests;
  final int processingTasks;

  AdminStats({
    required this.totalDevices,
    required this.rentedDevices,
    required this.totalContracts,
    required this.maintenanceRequests,
    required this.processingTasks,
  });
}