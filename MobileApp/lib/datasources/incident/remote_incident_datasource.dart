import 'dart:convert';

import 'package:http/http.dart' as http;

import '../../models/attachment_model.dart';
import '../../models/incident_model.dart';
import '../../services/api_config.dart';
import '../../services/api_session.dart';
import 'incident_datasource.dart';

class RemoteIncidentDataSource implements IncidentDataSource {
  final String? _baseUrl;
  String get baseUrl => _baseUrl ?? ApiConfig.baseUrl;

  RemoteIncidentDataSource({String? baseUrl}) : _baseUrl = baseUrl;

  @override
  Future<List<IncidentModel>> getIncidents(String userId, String role) async {
    final response = await ApiSession.get(Uri.parse('$baseUrl/maintenance'));
    return (_read(response) as List).map((row) => _parse(row)).toList();
  }

  @override
  Future<IncidentModel> getIncident(String id) async {
    final response = await ApiSession.get(Uri.parse('$baseUrl/maintenance/$id'));
    return _parse(_read(response));
  }

  @override
  Future<IncidentModel> createIncident(IncidentModel incident) async {
    final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/maintenance'));
    request.fields.addAll({
      'contractId': incident.contractId,
      'deviceId': incident.deviceId,
      'issueType': incident.issueType,
      'description': incident.description,
      'severity': incident.severity,
    });
    for (final attachment in incident.attachments) {
      final bytes = attachment.bytes;
      if (bytes == null || bytes.isEmpty || attachment.fileName == null) {
        throw Exception('Không đọc được ảnh đính kèm.');
      }
      request.files.add(http.MultipartFile.fromBytes('images', bytes, filename: attachment.fileName));
    }
    final data = _read(await ApiSession.send(request)) as Map<String, dynamic>;
    return _parse({...incident.toJson(), ...data});
  }

  @override
  Future<IncidentReview> acceptIncident(String id, bool accepted, String feedback) =>
      _review(id, 'acceptance', {'accepted': accepted, 'feedback': feedback});

  @override
  Future<IncidentReview> rateIncident(String id, int rating, String feedback) =>
      _review(id, 'rating', {'rating': rating, 'feedback': feedback});

  Future<IncidentReview> _review(String id, String action, Map<String, dynamic> payload) async {
    final response = await ApiSession.put(
      Uri.parse('$baseUrl/maintenance/$id/$action'),
      headers: {'Content-Type': 'application/json; charset=utf-8'},
      body: jsonEncode(payload),
    );
    final update = _read(response) as Map<String, dynamic>;
    return (
      status: update['status'] as String,
      statusCode: update['statusCode'] as int,
      rating: update['rating'] as int?,
      feedback: update['feedback'] as String?,
    );
  }

  dynamic _read(http.Response response) {
    dynamic data;
    try {
      data = jsonDecode(utf8.decode(response.bodyBytes));
    } on FormatException {
      if (response.statusCode >= 200 && response.statusCode < 300) rethrow;
    }
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception(data is Map && data['message'] is String
          ? data['message'] : 'Không thể xử lý yêu cầu (${response.statusCode}).');
    }
    return data;
  }

  IncidentModel _parse(Map<String, dynamic> data) {
    final images = (data['imagePaths'] as List? ?? []).cast<String>();
    return IncidentModel(
      id: data['id']?.toString() ?? '',
      code: data['code'] ?? 'SC-${data['id']}',
      contractId: data['contractId']?.toString() ?? '',
      deviceId: data['deviceId']?.toString() ?? '',
      deviceName: data['deviceName'],
      issueType: data['issueType'] ?? 'Sự cố',
      description: data['description'] ?? '',
      severity: data['severity'] ?? 'Trung bình',
      occurrenceTime: data['occurrenceTime'] ?? '',
      status: data['status'] ?? 'Chờ xử lý',
      statusCode: data['statusCode'],
      rating: data['rating'],
      feedback: data['feedback'],
      result: data['result'],
      assignedStaff: data['assignedStaff'],
      createdAt: data['createdAt'] ?? '',
      attachments: images.map((path) => AttachmentModel(
        id: path, url: Uri.parse(baseUrl).resolve(path).toString(),
      )).toList(),
    );
  }
}
