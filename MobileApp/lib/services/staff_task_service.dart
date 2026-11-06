import 'dart:convert';

import 'api_config.dart';
import 'api_session.dart';

class ManualTask {
  final int id;
  final String title;
  final String description;
  final String? customer;
  final int? contractId;
  final int? ticketId;
  final String status;
  final int statusCode;
  final DateTime assignedAt;
  final DateTime? dueAt;
  final DateTime? completedAt;
  final String? notes;

  ManualTask.fromJson(Map<String, dynamic> json)
    : id = json['id'],
      title = json['title'],
      description = json['description'],
      customer = json['customer'],
      contractId = json['contractId'],
      ticketId = json['ticketId'],
      status = json['status'],
      statusCode = json['statusCode'],
      assignedAt = DateTime.parse(json['assignedAt']),
      dueAt = DateTime.tryParse(json['dueAt'] ?? ''),
      completedAt = DateTime.tryParse(json['completedAt'] ?? ''),
      notes = json['notes'];
}

class StaffTaskService {
  static Future<List<ManualTask>> list() async {
    final response = await ApiSession.get(Uri.parse('${ApiConfig.baseUrl}/tasks/mine'));
    if (response.statusCode != 200) throw Exception('Không tải được công việc (${response.statusCode}).');
    final data = jsonDecode(utf8.decode(response.bodyBytes)) as List;
    return data.map((item) => ManualTask.fromJson(item)).toList();
  }

  static Future<void> update(int id, int status, {String? notes}) async {
    final response = await ApiSession.put(Uri.parse('${ApiConfig.baseUrl}/tasks/$id/status'),
      headers: {'Content-Type': 'application/json; charset=utf-8'},
      body: jsonEncode({'statusCode': status, 'notes': notes}),
    );
    if (response.statusCode == 200) return;
    String? message;
    try {
      final data = jsonDecode(utf8.decode(response.bodyBytes));
      if (data is Map) message = data['message'] as String?;
    } on FormatException {
      // The server may reply without a JSON body.
    }
    throw Exception(message ?? 'Không cập nhật được công việc (${response.statusCode}).');
  }
}
