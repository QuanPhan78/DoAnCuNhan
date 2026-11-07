import 'dart:convert';
import '../../services/api_session.dart';
import '../../models/renewal_model.dart';
import '../../services/api_config.dart';
import 'renewal_datasource.dart';

class RemoteRenewalDataSource implements RenewalDataSource {
  final String? _baseUrl;
  String get baseUrl => _baseUrl ?? ApiConfig.baseUrl;

  RemoteRenewalDataSource({String? baseUrl}) : _baseUrl = baseUrl;

  @override
  Future<bool> submitRenewalRequest(RenewalModel request) async {
    final response = await ApiSession.post(
      Uri.parse('$baseUrl/contracts/${request.contractId}/renew'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'days': int.tryParse(request.duration), 'duration': request.duration, 'notes': request.notes}),
    );
    if (response.statusCode >= 200 && response.statusCode < 300) return true;
    dynamic data;
    try { data = jsonDecode(utf8.decode(response.bodyBytes)); } on FormatException { data = null; }
    throw Exception(data is Map ? data['message'] ?? 'Không gửi được yêu cầu gia hạn.' : 'Không gửi được yêu cầu gia hạn.');
  }
}
