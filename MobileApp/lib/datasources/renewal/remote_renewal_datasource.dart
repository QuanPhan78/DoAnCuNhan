import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../models/renewal_model.dart';
import 'renewal_datasource.dart';

class RemoteRenewalDataSource implements RenewalDataSource {
  final String baseUrl;
  RemoteRenewalDataSource({this.baseUrl = 'http://10.0.2.2:5000/api'});

  @override
  Future<bool> submitRenewalRequest(RenewalModel request) async {
    try {
      final url = Uri.parse('$baseUrl/contracts/${request.contractId}/renew');
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'duration': request.duration,
          'notes': request.notes,
          'customerId': request.customerId,
        }),
      );
      return response.statusCode >= 200 && response.statusCode < 300;
    } catch (_) {
      return false;
    }
  }
}
