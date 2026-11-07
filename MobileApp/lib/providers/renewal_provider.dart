import 'package:flutter/material.dart';
import '../models/renewal_model.dart';
import '../repositories/renewal_repository.dart';

class RenewalProvider with ChangeNotifier {
  final RenewalRepository _repository;
  RenewalProvider(this._repository);

  String? errorMessage;
  bool _isSubmitting = false;
  bool get isSubmitting => _isSubmitting;

  Future<bool> submitRenewalRequest({
    required String contractId,
    required String customerId,
    required String duration,
    required String notes,
  }) async {
    if (_isSubmitting) return false;
    errorMessage = null;
    final days = int.tryParse(duration);
    if (days == null || days < 1 || days > 365) { errorMessage = "Nhập số ngày gia hạn từ 1 đến 365."; return false; }
    _isSubmitting = true;
    notifyListeners();

    final request = RenewalModel(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      contractId: contractId,
      customerId: customerId,
      duration: duration,
      notes: notes,
      status: 'Chờ xử lý',
      requestedAt: DateTime.now().toString(),
    );

    try {
      final success = await _repository.submitRenewalRequest(request);
      return success;
    } catch (e) {
      errorMessage = e.toString().replaceFirst("Exception: ", "");
      return false;
    } finally {
      _isSubmitting = false;
      notifyListeners();
    }
  }
}