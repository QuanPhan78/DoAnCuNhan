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
}