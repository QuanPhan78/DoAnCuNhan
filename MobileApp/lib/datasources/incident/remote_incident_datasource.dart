import '../../models/incident_model.dart';
import 'incident_datasource.dart';

class RemoteIncidentDataSource implements IncidentDataSource {
  @override
  Future<List<IncidentModel>> getIncidents(String userId, String role) async {
    throw UnimplementedError('API chưa có sẵn');
  }

  @override
  Future<IncidentModel> createIncident(IncidentModel incident) async {
    throw UnimplementedError();
  }
}