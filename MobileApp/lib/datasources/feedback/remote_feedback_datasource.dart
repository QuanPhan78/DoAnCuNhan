import '../../models/feedback_model.dart';
import 'feedback_datasource.dart';

class RemoteFeedbackDataSource implements FeedbackDataSource {
  @override
  Future<List<FeedbackModel>> getFeedbacks() async {
    throw UnimplementedError('API chưa có sẵn');
  }

  @override
  Future<bool> createFeedback(FeedbackModel feedback) async {
    throw UnimplementedError('API chưa có sẵn');
  }
}