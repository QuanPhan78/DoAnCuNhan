import 'package:flutter/foundation.dart';
import '../models/rental_request_model.dart';
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

  Future<bool> cancelRental(String id) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final success = await _repository.cancelRental(id);
      if (success) {
        final index = _requests.indexWhere((r) => r.id == id);
        if (index != -1) {
          _requests[index] = _requests[index].copyWith(status: _requests[index].status);
        }
        await loadRequests();
      }
      return success;
    } catch (e) {
      _error = 'Lỗi huỷ đơn thuê: $e';
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
