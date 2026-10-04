import 'dart:async';
import 'package:flutter/material.dart';
import '../models/search/search_result_model.dart';
import '../models/role_enum.dart';
import '../repositories/search_repository.dart';

class SearchProvider with ChangeNotifier {
  final SearchRepository _repository;
  SearchProvider(this._repository);

  List<SearchResultModel> _results = [];
  bool _isLoading = false;
  String? _errorMessage;
  String _currentQuery = '';
  String _currentFilter = 'all';

  Timer? _debounce;

  List<SearchResultModel> get results => _results;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  String get currentQuery => _currentQuery;
  String get currentFilter => _currentFilter;

  void setFilter(String filter, String? userId, Role? role) {
    _currentFilter = filter;
    if (_currentQuery.isNotEmpty) {
      search(_currentQuery, userId: userId, role: role);
    } else {
      _results = [];
      notifyListeners();
    }
  }

  void onSearchChanged(String query, String? userId, Role? role) {
    _currentQuery = query;
    if (_debounce?.isActive ?? false) _debounce!.cancel();
    
    if (query.trim().isEmpty) {
      _results = [];
      _isLoading = false;
      _errorMessage = null;
      notifyListeners();
      return;
    }

    _debounce = Timer(const Duration(milliseconds: 500), () {
      search(query, userId: userId, role: role);
    });
  }

  Future<void> search(String query, {String? userId, Role? role}) async {
    if (query.trim().isEmpty) return;
    
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _results = await _repository.search(query, filterType: _currentFilter, userId: userId, role: role);
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void clearSearch() {
    if (_debounce?.isActive ?? false) _debounce!.cancel();
    _currentQuery = '';
    _results = [];
    _isLoading = false;
    _errorMessage = null;
    notifyListeners();
  }
}