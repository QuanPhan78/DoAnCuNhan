import '../../models/incident_model.dart';

abstract class IncidentDataSource {
  Future<List<IncidentModel>> getIncidents(String userId, String role);
  Future<IncidentModel> getIncident(String id);
  Future<IncidentModel> createIncident(IncidentModel incident);
  Future<IncidentReview> acceptIncident(String id, bool accepted, String feedback);
  Future<IncidentReview> rateIncident(String id, int rating, String feedback);
}
