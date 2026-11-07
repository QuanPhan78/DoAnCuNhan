import 'package:flutter/foundation.dart';
import '../models/rental_request_model.dart';
import '../models/rental_status.dart';
import '../repositories/rental_repository.dart';

class RentalProvider with ChangeNotifier {
  final RentalRepository _repository;
  
  List<RentalRequestModel> _requests = [];
  List<RentalRequestModel> get requests => _requests;
  List<RentalRequestModel> get rentals => _requests;
  
  bool _isLoading = false;
  bool get isLoading => _isLoading;
  
  String? _error;
  String? get error => _error;

  RentalProvider(this._repository);

  Future<RentalRequestModel> quoteRental(RentalRequestModel request) =>
      _repository.quoteRental(request);

  Future<void> loadRequests({String? userId}) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _requests = await _repository.getRentals(userId: userId);
    } catch (e) {
      _error = 'Lỗi tải danh sách đơn thuê: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<RentalRequestModel> createRental(RentalRequestModel request) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final newReq = await _repository.createRental(request);
      _requests.insert(0, newReq);
      return newReq;
    } catch (e) {
      _error = 'Lỗi tạo đơn thuê: $e';
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> requestCancellation(String id, String reason) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await _repository.requestCancellation(id, reason);
      _requests = _requests.map((request) => request.id == id
          ? request.copyWith(status: RentalStatus.cancellationRequested, cancellationReason: reason)
          : request).toList();
      await loadRequests();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
