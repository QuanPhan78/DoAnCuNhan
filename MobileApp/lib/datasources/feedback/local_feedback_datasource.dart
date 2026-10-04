import 'dart:convert';
import 'package:flutter/services.dart';
import '../../models/feedback_model.dart';
import 'feedback_datasource.dart';

class LocalFeedbackDataSource implements FeedbackDataSource {
  static List<FeedbackModel>? _inMemoryData;

  Future<void> _initData() async {
    if (_inMemoryData == null) {
      final String response = await rootBundle.loadString('assets/mock/feedbacks.json');
      final List<dynamic> data = json.decode(response);
      _inMemoryData = data.map((json) => FeedbackModel.fromJson(json)).toList();
    }
  }

  @override
  Future<List<FeedbackModel>> getFeedbacks() async {
    await Future.delayed(const Duration(milliseconds: 500));
    await _initData();
    return List.from(_inMemoryData!);
  }

  @override
  Future<bool> createFeedback(FeedbackModel feedback) async {
    await Future.delayed(const Duration(milliseconds: 500));
    await _initData();
    _inMemoryData!.insert(0, feedback);
    return true;
  }
}