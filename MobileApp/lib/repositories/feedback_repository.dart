import '../models/feedback_model.dart';
import '../datasources/feedback/feedback_datasource.dart';

class FeedbackRepository {
  final FeedbackDataSource _dataSource;
  FeedbackRepository(this._dataSource);

  Future<List<FeedbackModel>> getFeedbacks() {
    return _dataSource.getFeedbacks();
  }

  Future<bool> createFeedback(FeedbackModel feedback) {
    return _dataSource.createFeedback(feedback);
  }
}