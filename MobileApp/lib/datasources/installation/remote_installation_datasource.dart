import 'dart:convert';

import '../../models/installation_model.dart';
import '../../services/api_config.dart';
import '../../services/api_session.dart';
import 'installation_datasource.dart';

class RemoteInstallationDataSource implements InstallationDataSource {
  @override
  Future<InstallationModel?> getInstallationByContractId(String contractId) async {
    final uri = Uri.parse('${ApiConfig.baseUrl}/tasks/installation/$contractId');
    final response = await ApiSession.get(uri);
    if (response.statusCode == 404) return null;
    if (response.statusCode != 200) {
      throw Exception('Không tải được tiến độ lắp đặt (${response.statusCode}).');
    }
    return InstallationModel.fromJson(jsonDecode(utf8.decode(response.bodyBytes)));
  }
}
