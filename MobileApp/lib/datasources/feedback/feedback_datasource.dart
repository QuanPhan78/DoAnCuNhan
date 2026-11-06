import '../../models/feedback_model.dart';

abstract class FeedbackDataSource {
  Future<List<FeedbackModel>> getFeedbacks();
  Future<bool> createFeedback(FeedbackModel feedback);
}