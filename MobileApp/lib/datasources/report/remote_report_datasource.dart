import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../models/report_model.dart';
import 'report_datasource.dart';

class RemoteReportDataSource implements ReportDataSource {
  final String baseUrl;

  RemoteReportDataSource({this.baseUrl = 'http://10.0.2.2:5000/api'});

  @override
  Future<ReportModel> getReports(String timeFilter) async {
    try {
      final url = Uri.parse('$baseUrl/reports?timeFilter=$timeFilter');
      final response = await http.get(url);

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
