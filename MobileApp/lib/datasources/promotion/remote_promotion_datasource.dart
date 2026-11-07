import 'dart:convert';
import '../../services/api_session.dart';
import '../../models/promotion_model.dart';
import '../../services/api_config.dart';
import 'promotion_datasource.dart';

class RemotePromotionDataSource implements PromotionDataSource {
  final String? _baseUrl;
  String get baseUrl => _baseUrl ?? ApiConfig.baseUrl;

  RemotePromotionDataSource({String? baseUrl}) : _baseUrl = baseUrl;

  @override
  Future<List<PromotionModel>> getPromotions() async {
    try {
      final url = Uri.parse('$baseUrl/promotions');
      final response = await ApiSession.get(url);

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        return data.map((jsonItem) => PromotionModel.fromJson(jsonItem)).toList();
      } else {
        throw Exception('Không thể tải danh sách khuyến mãi: ${response.statusCode}');
      }
    } catch (e) {
      if (e is Exception) rethrow;
      throw Exception('Lỗi kết nối máy chủ: $e');
    }
  }
}
