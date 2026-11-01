import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../models/feedback_model.dart';
import 'feedback_datasource.dart';

class RemoteFeedbackDataSource implements FeedbackDataSource {
  final String baseUrl;

  RemoteFeedbackDataSource({this.baseUrl = 'http://10.0.2.2:5000/api'});

  @override
  Future<List<FeedbackModel>> getFeedbacks() async {
    try {
      final url = Uri.parse('$baseUrl/maintenance');
      final response = await http.get(url);

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(utf8.decode(response.bodyBytes));
        return data.where((item) => item['rating'] != null).map((item) => FeedbackModel(
          id: item['id']?.toString() ?? '',
          feedbackCode: 'FB-${item['id']}',
          contractId: item['contractCode'] ?? 'HD-${item['contractId']}',
          maintenanceId: item['code'] ?? 'SC-${item['id']}',
          content: item['result']?.toString().isNotEmpty == true ? item['result'] : 'Đánh giá dịch vụ thiết bị',
          rating: item['rating'] as int?,
          status: 'Đã phản hồi',
          createdAt: item['createdAt'],
          response: 'Cảm ơn bạn đã phản hồi đánh giá dịch vụ!',
        )).toList();
      }
      return [];
    } catch (_) {
      return [];
    }
  }

  @override
  Future<bool> createFeedback(FeedbackModel feedback) async {
    try {
      final ticketId = feedback.maintenanceId?.replaceAll('SC-', '') ?? feedback.id;
      final url = Uri.parse('$baseUrl/maintenance/$ticketId/rating');
      final payload = {
        'rating': feedback.rating ?? 5,
        'feedback': feedback.content,
      };

      final response = await http.put(
        url,
        headers: {'Content-Type': 'application/json; charset=utf-8'},
        body: json.encode(payload),
      );

      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
