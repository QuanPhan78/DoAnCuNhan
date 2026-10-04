import 'package:flutter/material.dart';
import '../models/renewal_model.dart';
import '../repositories/renewal_repository.dart';

class RenewalProvider with ChangeNotifier {
  final RenewalRepository _repository;
  RenewalProvider(this._repository);

  bool _isSubmitting = false;
  bool get isSubmitting => _isSubmitting;

  Future<bool> submitRenewalRequest({
    required String contractId,
    required String customerId,
    required String duration,
    required String notes,
  }) async {
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
      return false;
    } finally {
      _isSubmitting = false;
      notifyListeners();
    }
  }
}