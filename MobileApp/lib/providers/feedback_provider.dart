import 'package:flutter/material.dart';
import '../models/feedback_model.dart';
import '../repositories/feedback_repository.dart';

class FeedbackProvider with ChangeNotifier {
  final FeedbackRepository _repository;
  FeedbackProvider(this._repository);

  List<FeedbackModel> _feedbacks = [];
  bool _isLoading = false;
  String? _errorMessage;

  List<FeedbackModel> get feedbacks => _feedbacks;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  Future<void> fetchFeedbacks() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();
    try {
      _feedbacks = await _repository.getFeedbacks();
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> createFeedback(FeedbackModel feedback) async {
    try {
      final success = await _repository.createFeedback(feedback);
      if (success) {

        notifyListeners();
      }
      return success;
    } catch (e) {
      _errorMessage = e.toString();
      notifyListeners();
      return false;
    }
  }
}