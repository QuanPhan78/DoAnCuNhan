import 'dart:convert';
import '../../services/api_session.dart';
import '../../models/report_model.dart';
import '../../services/api_config.dart';
import 'report_datasource.dart';

class RemoteReportDataSource implements ReportDataSource {
  final String? _baseUrl;
  String get baseUrl => _baseUrl ?? ApiConfig.baseUrl;

  RemoteReportDataSource({String? baseUrl}) : _baseUrl = baseUrl;

  @override
  Future<ReportModel> getReports(String timeFilter) async {
    try {
      final url = Uri.parse('$baseUrl/reports').replace(queryParameters: {'timeFilter': timeFilter});
      final response = await ApiSession.get(url);

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return ReportModel.fromJson(data);
      } else {
        throw Exception('Không thể tải dữ liệu báo cáo: ${response.statusCode}');
      }
    } catch (e) {
      if (e is Exception) rethrow;
      throw Exception('Lỗi kết nối máy chủ: $e');
    }
  }
}
