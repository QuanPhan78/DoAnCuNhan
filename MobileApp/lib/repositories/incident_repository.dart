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

  Future<IncidentModel> getIncident(String id) => _dataSource.getIncident(id);

  Future<IncidentReview> acceptIncident(String id, bool accepted, String feedback) =>
      _dataSource.acceptIncident(id, accepted, feedback);

  Future<IncidentReview> rateIncident(String id, int rating, String feedback) =>
      _dataSource.rateIncident(id, rating, feedback);
}
