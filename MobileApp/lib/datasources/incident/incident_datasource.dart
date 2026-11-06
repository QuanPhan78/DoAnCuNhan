import '../../models/incident_model.dart';

abstract class IncidentDataSource {
  Future<List<IncidentModel>> getIncidents(String userId, String role);
  Future<IncidentModel> createIncident(IncidentModel incident);
}