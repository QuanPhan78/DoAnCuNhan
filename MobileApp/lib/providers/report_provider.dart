import 'package:flutter/material.dart';
import '../models/report_model.dart';
import '../repositories/report_repository.dart';

class ReportProvider with ChangeNotifier {
  final ReportRepository _repository;
  ReportProvider(this._repository);

  ReportModel? _reportData;
  bool _isLoading = false;
  String? _errorMessage;
  String _currentTimeFilter = 'all';
  int _request = 0;

  ReportModel? get reportData => _reportData;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  String get currentTimeFilter => _currentTimeFilter;

  Future<void> fetchReports({String? timeFilter}) async {
    final request = ++_request;
    if (timeFilter != null) {
      _currentTimeFilter = timeFilter;
    }
    
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final report = await _repository.getReports(_currentTimeFilter);
      if (request == _request) _reportData = report;
    } catch (e) {
      if (request == _request) _errorMessage = e.toString();
    } finally {
      if (request == _request) {
        _isLoading = false;
        notifyListeners();
      }
    }
  }
}
