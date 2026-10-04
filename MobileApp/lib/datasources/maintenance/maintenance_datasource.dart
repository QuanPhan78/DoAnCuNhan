import '../../models/maintenance_model.dart';
import '../../models/role_enum.dart';

abstract class MaintenanceDataSource {
  Future<List<MaintenanceModel>> getMaintenances(String userId, Role role, String userName);
  Future<bool> updateMaintenance(MaintenanceModel maintenance);
}