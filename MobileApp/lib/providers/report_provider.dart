import 'package:flutter/material.dart';
import '../models/report_model.dart';
import '../repositories/report_repository.dart';

class ReportProvider with ChangeNotifier {
  final ReportRepository _repository;
  ReportProvider(this._repository);

  ReportModel? _reportData;
  bool _isLoading = false;
  String? _errorMessage;
  String _currentTimeFilter = 'Tháng này';

  ReportModel? get reportData => _reportData;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  String get currentTimeFilter => _currentTimeFilter;

  Future<void> fetchReports({String? timeFilter}) async {
    if (timeFilter != null) {
      _currentTimeFilter = timeFilter;
    }
    
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _reportData = await _repository.getReports(_currentTimeFilter);
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}