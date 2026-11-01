import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../models/maintenance_model.dart';
import '../../models/role_enum.dart';
import 'maintenance_datasource.dart';

class RemoteMaintenanceDataSource implements MaintenanceDataSource {
  final String baseUrl;

  RemoteMaintenanceDataSource({this.baseUrl = 'http://10.0.2.2:5000/api'});

  @override
  Future<List<MaintenanceModel>> getMaintenances(String userId, Role role, String userName) async {
    try {
      final roleStr = role == Role.admin ? 'Admin' : (role == Role.staff ? 'Staff' : 'KhachHang');
      final url = Uri.parse('$baseUrl/maintenance?userId=$userId&role=$roleStr');
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        return data.map((item) {
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
            createdAt: item['createdAt'],
            completedAt: item['completedAt'],
            result: item['result'],
            notes: notes,
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
        'status': maintenance.status,
        'result': maintenance.result,
        'notes': maintenance.notes.isNotEmpty ? maintenance.notes.last.content : '',
      };

      final response = await http.put(
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
