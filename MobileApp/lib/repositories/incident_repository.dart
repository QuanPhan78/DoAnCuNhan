import '../models/incident_model.dart';
import '../datasources/incident/incident_datasource.dart';

class IncidentRepository {
  final IncidentDataSource _dataSource;
  IncidentRepository(this._dataSource);

  Future<List<IncidentModel>> getIncidents(String userId, String role) {
    return _dataSource.getIncidents(userId, role);
  }

  Future<IncidentModel> createIncident(IncidentModel incident) {
    return _dataSource.createIncident(incident);
  }
}