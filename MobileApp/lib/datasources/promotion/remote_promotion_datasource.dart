import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../models/promotion_model.dart';
import 'promotion_datasource.dart';

class RemotePromotionDataSource implements PromotionDataSource {
  final String baseUrl;

  RemotePromotionDataSource({this.baseUrl = 'http://10.0.2.2:5000/api'});

  @override
  Future<List<PromotionModel>> getPromotions() async {
    try {
      final url = Uri.parse('$baseUrl/promotions');
      final response = await http.get(url);

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
