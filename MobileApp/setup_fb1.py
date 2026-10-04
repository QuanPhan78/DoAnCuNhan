import os
import json

os.makedirs("assets/mock", exist_ok=True)
mock_feedbacks = [
    {
        "id": "F001",
        "feedbackCode": "FB-2026-001",
        "contractId": "C001",
        "maintenanceId": "",
        "content": "Thiết bị hoạt động rất tốt, tuy nhiên giao hàng hơi chậm một chút.",
        "rating": 4,
        "status": "Đã phản hồi",
        "createdAt": "12/09/2026 10:00",
        "response": "Cảm ơn quý khách đã góp ý. Chúng tôi sẽ cải thiện tốc độ giao hàng trong lần sau."
    },
    {
        "id": "F002",
        "feedbackCode": "FB-2026-002",
        "contractId": "",
        "maintenanceId": "M001",
        "content": "Nhân viên bảo trì nhiệt tình, chuyên môn tốt.",
        "rating": 5,
        "status": "Đã ghi nhận",
        "createdAt": "13/09/2026 15:30",
        "response": ""
    }
]

with open("assets/mock/feedbacks.json", "w", encoding="utf-8") as f:
    json.dump(mock_feedbacks, f, ensure_ascii=False, indent=2)

os.makedirs("lib/models", exist_ok=True)
model_code = """class FeedbackModel {
  final String id;
  final String? feedbackCode;
  final String? contractId;
  final String? maintenanceId;
  final String content;
  final int? rating;
  final String? status;
  final String? createdAt;
  final String? response;

  FeedbackModel({
    required this.id,
    this.feedbackCode,
    this.contractId,
    this.maintenanceId,
    required this.content,
    this.rating,
    this.status,
    this.createdAt,
    this.response,
  });

  factory FeedbackModel.fromJson(Map<String, dynamic> json) {
    return FeedbackModel(
      id: json['id'],
      feedbackCode: json['feedbackCode'],
      contractId: json['contractId'],
      maintenanceId: json['maintenanceId'],
      content: json['content'] ?? '',
      rating: json['rating'],
      status: json['status'],
      createdAt: json['createdAt'],
      response: json['response'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'feedbackCode': feedbackCode,
      'contractId': contractId,
      'maintenanceId': maintenanceId,
      'content': content,
      'rating': rating,
      'status': status,
      'createdAt': createdAt,
      'response': response,
    };
  }
}
"""
with open("lib/models/feedback_model.dart", "w", encoding="utf-8") as f: f.write(model_code.strip())

os.makedirs("lib/datasources/feedback", exist_ok=True)
ds_abs = """import '../../models/feedback_model.dart';

abstract class FeedbackDataSource {
  Future<List<FeedbackModel>> getFeedbacks();
  Future<bool> createFeedback(FeedbackModel feedback);
}
"""
with open("lib/datasources/feedback/feedback_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_abs.strip())

ds_loc = """import 'dart:convert';
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
    return _inMemoryData!;
  }

  @override
  Future<bool> createFeedback(FeedbackModel feedback) async {
    await Future.delayed(const Duration(milliseconds: 500));
    await _initData();
    _inMemoryData!.insert(0, feedback);
    return true;
  }
}
"""
with open("lib/datasources/feedback/local_feedback_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_loc.strip())

ds_rem = """import '../../models/feedback_model.dart';
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
"""
with open("lib/datasources/feedback/remote_feedback_datasource.dart", "w", encoding="utf-8") as f: f.write(ds_rem.strip())

os.makedirs("lib/repositories", exist_ok=True)
repo = """import '../models/feedback_model.dart';
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
"""
with open("lib/repositories/feedback_repository.dart", "w", encoding="utf-8") as f: f.write(repo.strip())

os.makedirs("lib/providers", exist_ok=True)
prov = """import 'package:flutter/material.dart';
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
        _feedbacks.insert(0, feedback);
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
"""
with open("lib/providers/feedback_provider.dart", "w", encoding="utf-8") as f: f.write(prov.strip())

print("Feedback layer data created.")