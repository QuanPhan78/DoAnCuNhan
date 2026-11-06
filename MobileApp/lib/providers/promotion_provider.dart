import 'package:flutter/material.dart';
import '../models/promotion_model.dart';
import '../repositories/promotion_repository.dart';

class PromotionProvider with ChangeNotifier {
  final PromotionRepository _repository;
  PromotionProvider(this._repository);

  List<PromotionModel> _promotions = [];
  bool _isLoading = false;
  String? _errorMessage;

  List<PromotionModel> get promotions => _promotions;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  Future<void> fetchPromotions() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _promotions = await _repository.getPromotions();
    } catch (e) {
      _errorMessage = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}