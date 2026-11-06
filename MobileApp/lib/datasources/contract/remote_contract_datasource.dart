import 'dart:convert';
import '../../services/api_session.dart';
import '../../models/contract_model.dart';
import '../../models/role_enum.dart';
import '../../services/api_config.dart';
import 'contract_datasource.dart';

class RemoteContractDataSource implements ContractDataSource {
  final String? _baseUrl;
  String get baseUrl => _baseUrl ?? ApiConfig.baseUrl;

  RemoteContractDataSource({String? baseUrl}) : _baseUrl = baseUrl;

  @override
  Future<List<ContractModel>> getContracts(Role role, String userId) async {
    try {

      final url = Uri.parse('$baseUrl/contracts');
      final response = await ApiSession.get(url);

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        return data.map((jsonItem) => ContractModel.fromJson(jsonItem)).toList();
      } else {
        throw Exception('Không thể tải danh sách hợp đồng (${response.statusCode})');
      }
    } catch (e) {
      if (e is Exception) rethrow;
      throw Exception('Lỗi kết nối máy chủ: $e');
    }
  }

  @override
  Future<ContractModel> getContract(String contractId, String userId, Role role) async {
    try {

      final numericId = contractId.replaceAll(RegExp(r'[^0-9]'), '');
      final idParam = numericId.isNotEmpty ? int.parse(numericId).toString() : contractId;

      final url = Uri.parse('$baseUrl/contracts/$idParam');
      final response = await ApiSession.get(url);

      if (response.statusCode == 200) {
        return ContractModel.fromJson(jsonDecode(utf8.decode(response.bodyBytes)));
      } else if (response.statusCode == 403) {
        throw Exception('BẢO MẬT: Bạn không có quyền xem hợp đồng của khách hàng khác.');
      } else if (response.statusCode == 404) {
        throw Exception('Hợp đồng không tồn tại trong hệ thống.');
      } else {
        throw Exception('Không thể tải chi tiết hợp đồng (Mã lỗi: ${response.statusCode})');
      }
    } catch (e) {
      if (e is Exception) rethrow;
      throw Exception('Lỗi kết nối máy chủ: $e');
    }
  }
}
