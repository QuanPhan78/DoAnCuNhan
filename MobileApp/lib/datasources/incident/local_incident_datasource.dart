import 'dart:convert';
import 'package:flutter/services.dart';
import '../../models/incident_model.dart';
import 'incident_datasource.dart';

class LocalIncidentDataSource implements IncidentDataSource {
  static List<IncidentModel>? _inMemoryData;

  Future<void> _initData() async {
    if (_inMemoryData == null) {
      final String response = await rootBundle.loadString('assets/mock/incidents.json');
      final List<dynamic> data = json.decode(response);
      _inMemoryData = data.map((json) => IncidentModel.fromJson(json)).toList();
    }
  }

  @override
  Future<List<IncidentModel>> getIncidents(String userId, String role) async {
    await Future.delayed(const Duration(milliseconds: 500));
    await _initData();
    // For mock: customer sees their own (filtering in provider or here, we do it in provider)
    return _inMemoryData!;
  }

  @override
  Future<IncidentModel> createIncident(IncidentModel incident) async {
    await Future.delayed(const Duration(milliseconds: 500));
    await _initData();
    _inMemoryData!.insert(0, incident); // Thêm vào đầu
    return incident;
  }

  @override
  Future<IncidentModel> getIncident(String id) async {
    await _initData();
    return _inMemoryData!.firstWhere((incident) => incident.id == id);
  }

  @override
  Future<IncidentReview> acceptIncident(String id, bool accepted, String feedback) async {
    final incident = await getIncident(id);
    if (incident.statusCode != 3) throw StateError('Phiếu chưa chờ nghiệm thu.');
    if (!accepted && feedback.trim().isEmpty) throw ArgumentError('Nhập lý do từ chối.');
    return _replace(incident, (
      statusCode: accepted ? 5 : 2,
      status: accepted ? 'Đã nghiệm thu' : 'Đang xử lý',
      rating: incident.rating, feedback: incident.feedback,
    ));
  }

  @override
  Future<IncidentReview> rateIncident(String id, int rating, String feedback) async {
    final incident = await getIncident(id);
    if (incident.statusCode != 3 && incident.statusCode != 5) throw StateError('Phiếu chưa sửa xong.');
    if (rating < 1 || rating > 5) throw ArgumentError('Điểm đánh giá từ 1 đến 5 sao.');
    return _replace(incident, (statusCode: incident.statusCode!, status: incident.status,
      rating: rating, feedback: feedback.trim().isEmpty ? incident.feedback : feedback));
  }

  IncidentReview _replace(IncidentModel incident, IncidentReview review) {
    _inMemoryData![_inMemoryData!.indexOf(incident)] = incident.withReview(review);
    return review;
  }
}
