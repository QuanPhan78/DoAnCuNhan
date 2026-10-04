import '../models/role_enum.dart';
import '../models/permission_enum.dart';

class PermissionManager {
  static final Map<Role, List<AppPermission>> _rolePermissions = {
    Role.customer: [
      AppPermission.viewDevices,
      AppPermission.viewOwnContracts,
      AppPermission.viewRentalHistory,
      AppPermission.requestExtension,
      AppPermission.reportIssue,
      AppPermission.trackMaintenance,
      AppPermission.submitFeedback,
      AppPermission.viewPromotions,
    ],
    Role.staff: [
      AppPermission.viewAssignedTasks,
      AppPermission.viewAssignedMaintenance,
      AppPermission.updateTaskStatus,
    ],
    Role.admin: [
      AppPermission.manageDevices,
      AppPermission.manageContracts,
      AppPermission.manageMaintenance,
      AppPermission.viewReports,
      // Admin có thể xem thiết bị như khách để quản lý
      AppPermission.viewDevices, 
    ],
  };

  static List<AppPermission> getPermissionsForRole(Role role) {
    return _rolePermissions[role] ?? [];
  }

  static bool hasPermission(Role role, AppPermission permission) {
    final perms = getPermissionsForRole(role);
    return perms.contains(permission);
  }
}