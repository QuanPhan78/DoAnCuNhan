import 'dart:convert';
import '../../services/api_session.dart';
import '../../models/maintenance_model.dart';
import '../../models/role_enum.dart';
import '../../services/api_config.dart';
import 'maintenance_datasource.dart';

class RemoteMaintenanceDataSource implements MaintenanceDataSource {
  final String? _baseUrl;
  String get baseUrl => _baseUrl ?? ApiConfig.baseUrl;

  RemoteMaintenanceDataSource({String? baseUrl}) : _baseUrl = baseUrl;

  @override
  Future<List<MaintenanceModel>> getMaintenances(String userId, Role role, String userName) async {
    try {
      final url = Uri.parse('$baseUrl/maintenance');
      final response = await ApiSession.get(url);

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        return data.where((item) => role != Role.staff ||
            item['assignedStaffId']?.toString() == userId).map((item) {
          final notesRaw = (item['notes'] as List<dynamic>?) ?? [];
          final notes = notesRaw.map((n) => MaintenanceNote(
            time: n['time'] ?? '',
            content: n['content'] ?? '',
            author: n['author'] ?? '',
          )).toList();

          return MaintenanceModel(
            id: item['id']?.toString() ?? '',
            requestCode: item['requestCode'] ?? 'SC-${item['id']}',
            contractId: item['contractCode'] ?? 'HD-${item['contractId']}',
            deviceId: item['deviceName'] ?? item['deviceId']?.toString() ?? '',
            customer: item['customer'] ?? 'Khách hàng',
            description: item['description'] ?? '',
            status: item['status'] ?? 'Chờ xử lý',
            assignedEmployee: item['assignedEmployee'],
            assignedStaffId: item['assignedStaffId']?.toString(),
            statusCode: (item['statusCode'] as num?)?.toInt(),
            createdAt: item['createdAt'],
            completedAt: item['completedAt'],
            result: item['result'],
            notes: notes,
            imageUrls: (item['imagePaths'] as List? ?? []).cast<String>()
                .map((path) => Uri.parse(baseUrl).resolve(path).toString()).toList(),
          );
        }).toList();
      } else {
        throw Exception('Không thể tải danh sách bảo trì (${response.statusCode})');
      }
    } catch (e) {
      if (e is Exception) rethrow;
      throw Exception('Lỗi kết nối máy chủ: $e');
    }
  }

  @override
  Future<bool> updateMaintenance(MaintenanceModel maintenance) async {
    try {
      final url = Uri.parse('$baseUrl/maintenance/${maintenance.id}/status');
      final payload = {
        'statusCode': maintenance.statusCode,
        if (maintenance.statusCode == 3) 'result': maintenance.result,
        if (maintenance.updateNote?.isNotEmpty == true) 'notes': maintenance.updateNote,
      };

      final response = await ApiSession.put(
        url,
        headers: {'Content-Type': 'application/json; charset=utf-8'},
        body: json.encode(payload),
      );

      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}
