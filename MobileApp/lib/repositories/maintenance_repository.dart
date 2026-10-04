import '../models/maintenance_model.dart';
import '../models/role_enum.dart';
import '../datasources/maintenance/maintenance_datasource.dart';

class MaintenanceRepository {
  final MaintenanceDataSource _dataSource;
  MaintenanceRepository(this._dataSource);

  Future<List<MaintenanceModel>> getMaintenances(String userId, Role role, String userName) {
    return _dataSource.getMaintenances(userId, role, userName);
  }
  Future<bool> updateMaintenance(MaintenanceModel maintenance) {
    return _dataSource.updateMaintenance(maintenance);
  }
}