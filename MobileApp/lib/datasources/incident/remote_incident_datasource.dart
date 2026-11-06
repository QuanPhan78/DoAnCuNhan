import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../models/incident_model.dart';
import '../../services/api_config.dart';
import 'incident_datasource.dart';

class RemoteIncidentDataSource implements IncidentDataSource {
  final String? _baseUrl;
  String get baseUrl => _baseUrl ?? ApiConfig.baseUrl;

  RemoteIncidentDataSource({String? baseUrl}) : _baseUrl = baseUrl;

  @override
  Future<List<IncidentModel>> getIncidents(String userId, String role) async {
    try {
      final url = Uri.parse('$baseUrl/maintenance?userId=$userId&role=$role');
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        return data.map((item) => IncidentModel(
          id: item['id']?.toString() ?? '',
          code: item['code'] ?? 'SC-${item['id']}',
          contractId: item['contractId']?.toString() ?? '',
          deviceId: item['deviceName'] ?? item['deviceId']?.toString() ?? '',
          issueType: item['issueType'] ?? 'Sự cố',
          description: item['description'] ?? '',
          severity: item['severity'] ?? 'Trung bình',
          occurrenceTime: item['occurrenceTime'] ?? '',
          status: item['status'] ?? 'Chờ xử lý',
          assignedStaff: item['assignedStaff'],
          createdAt: item['createdAt'] ?? '',
          attachments: const [],
        )).toList();
      } else {
        throw Exception('Không thể tải danh sách sự cố (${response.statusCode})');
      }
    } catch (e) {
      if (e is Exception) rethrow;
      throw Exception('Lỗi kết nối máy chủ: $e');
    }
  }

  @override
  Future<IncidentModel> createIncident(IncidentModel incident) async {
    try {
      final url = Uri.parse('$baseUrl/maintenance');
      final payload = {
        'contractId': incident.contractId,
        'deviceId': incident.deviceId,
        'issueType': incident.issueType,
        'description': incident.description,
        'severity': incident.severity,
      };

      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json; charset=utf-8'},
        body: json.encode(payload),
      );

      if (response.statusCode >= 200 && response.statusCode < 300) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return IncidentModel(
          id: data['id']?.toString() ?? incident.id,
          code: data['code'] ?? incident.code,
          contractId: incident.contractId,
          deviceId: incident.deviceId,
          issueType: incident.issueType,
          description: incident.description,
          severity: incident.severity,
          occurrenceTime: incident.occurrenceTime,
          status: 'Chờ xử lý',
          createdAt: incident.createdAt,
          attachments: incident.attachments,
        );
      } else {
        throw Exception('Lỗi tạo sự cố: ${response.statusCode}');
      }
    } catch (e) {
      if (e is Exception) rethrow;
      throw Exception('Lỗi kết nối máy chủ: $e');
    }
  }
}
