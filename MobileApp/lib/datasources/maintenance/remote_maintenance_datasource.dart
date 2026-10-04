import '../../models/maintenance_model.dart';
import '../../models/role_enum.dart';
import 'maintenance_datasource.dart';

class RemoteMaintenanceDataSource implements MaintenanceDataSource {
  @override
  Future<List<MaintenanceModel>> getMaintenances(String userId, Role role, String userName) async {
    throw UnimplementedError('API chưa có sẵn');
  }
  @override
  Future<bool> updateMaintenance(MaintenanceModel maintenance) async {
    throw UnimplementedError('API chưa có sẵn');
  }
}