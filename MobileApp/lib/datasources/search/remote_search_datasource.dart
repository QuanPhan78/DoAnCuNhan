import 'dart:convert';
import '../../services/api_session.dart';
import '../../models/search/search_result_model.dart';
import '../../models/device_model.dart';
import '../../models/contract_model.dart';
import '../../models/incident_model.dart';
import '../../models/maintenance_model.dart';
import '../../models/role_enum.dart';
import '../../services/api_config.dart';
import 'search_datasource.dart';

class RemoteSearchDataSource implements SearchDataSource {
  final String? _baseUrl;
  String get baseUrl => _baseUrl ?? ApiConfig.baseUrl;

  RemoteSearchDataSource({String? baseUrl}) : _baseUrl = baseUrl;

  @override
  Future<List<SearchResultModel>> search(String query, {String filterType = 'all', String? userId, Role? role}) async {
    try {
      final url = Uri.parse('$baseUrl/search?q=${Uri.encodeComponent(query)}&type=$filterType');
      final response = await ApiSession.get(url);

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        return data.map((item) {
          final type = item['type'] as String;
          final orig = item['originalData'] as Map<String, dynamic>;

          dynamic originalModel;
          if (type == 'device') {
            final idStr = orig['id']?.toString() ?? '';
            final codeVal = orig['code'] ?? (idStr.isNotEmpty ? 'SP-${int.tryParse(idStr) != null ? int.parse(idStr).toString().padLeft(4, '0') : idStr}' : null);
            final imgVal = (orig['imageUrl'] != null && orig['imageUrl'].toString().isNotEmpty)
                ? orig['imageUrl']
                : ((orig['image'] != null && orig['image'].toString().isNotEmpty) ? orig['image'] : null);
            originalModel = DeviceModel(
              id: idStr,
              code: codeVal,
              name: orig['name'] ?? '',
              type: orig['type'] ?? 'Thiết bị',
              brand: orig['brand'] ?? 'Chính hãng',
              model: orig['model'] ?? orig['name'] ?? '',
              serialNumber: orig['serialNumber'] ?? (idStr.isNotEmpty ? 'SN-$idStr' : null),
              specifications: orig['specifications'] ?? orig['specs'] ?? '',
              condition: orig['condition'] ?? 'Mới 100%',
              rentalStatus: orig['rentalStatus'] ?? 'Sẵn sàng',
              rentalPrice: (orig['rentalPrice'] as num?)?.toDouble() ?? 
                           (orig['price'] as num?)?.toDouble() ?? 
                           (orig['pricePerDay'] as num?)?.toDouble(),
              description: orig['description'] ?? '',
              imageUrl: imgVal,
              imageAsset: orig['imageAsset'],
            );
          } else if (type == 'contract') {
            originalModel = ContractModel.fromJson(orig);
          } else if (type == 'incident') {
            originalModel = IncidentModel(
              id: orig['id']?.toString() ?? '',
              code: orig['code'] ?? '',
              contractId: orig['contractId'] ?? '',
              deviceId: orig['deviceId'] ?? '',
              issueType: orig['issueType'] ?? '',
              description: orig['description'] ?? '',
              severity: orig['severity'] ?? 'Trung bình',
              occurrenceTime: orig['occurrenceTime'] ?? '',
              status: orig['status'] ?? 'Chờ xử lý',
              statusCode: orig['statusCode'],
              createdAt: orig['createdAt'] ?? '',
            );
          } else if (type == 'maintenance') {
            originalModel = MaintenanceModel(
              id: orig['id']?.toString() ?? '',
              requestCode: orig['code'] ?? '',
              contractId: orig['contractId'] ?? '',
              deviceId: orig['deviceId'] ?? '',
              description: orig['description'] ?? '',
              status: orig['status'] ?? 'Chờ xử lý',
              statusCode: orig['statusCode'],
              createdAt: orig['createdAt'] ?? '',
            );
          }

          return SearchResultModel(
            id: item['id']?.toString() ?? '',
            type: type,
            title: item['title'] ?? '',
            subtitle: item['subtitle'] ?? '',
            status: item['status'],
            originalData: originalModel,
          );
        }).toList();
      }
    } catch (_) {}
    return [];
  }
}
