import 'package:flutter/material.dart';
import '../models/incident_model.dart';
import '../models/role_enum.dart';
import '../repositories/incident_repository.dart';

class IncidentProvider with ChangeNotifier {
  final IncidentRepository _repository;
  IncidentProvider(this._repository);

  List<IncidentModel> _incidents = [];
  bool _isLoading = false;
  String? _errorMessage;

  List<IncidentModel> get incidents => _incidents;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  Future<void> fetchIncidents(String userId, Role role) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _incidents = await _repository.getIncidents(userId, role.toString());
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> createIncident(IncidentModel incident) async {
    final saved = await _repository.createIncident(incident);
    _errorMessage = null;
    _incidents = [saved, ..._incidents];
    notifyListeners();
  }

  Future<IncidentModel> getIncident(String id) async {
    final incident = await _repository.getIncident(id);
    _replace(incident);
    return incident;
  }

  Future<IncidentModel> acceptIncident(IncidentModel incident, bool accepted, String feedback) async =>
      _replace(incident.withReview(await _repository.acceptIncident(incident.id, accepted, feedback)));

  Future<IncidentModel> rateIncident(IncidentModel incident, int rating, String feedback) async =>
      _replace(incident.withReview(await _repository.rateIncident(incident.id, rating, feedback)));

  IncidentModel _replace(IncidentModel incident) {
    _incidents = _incidents.map((item) => item.id == incident.id ? incident : item).toList();
    notifyListeners();
    return incident;
  }
}
