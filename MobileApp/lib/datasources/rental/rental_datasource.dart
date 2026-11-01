import '../../models/rental_request_model.dart';

abstract class RentalDataSource {
  Future<List<RentalRequestModel>> getRentals({String? userId});
  Future<RentalRequestModel> createRental(RentalRequestModel request);
  Future<bool> cancelRental(String id);
}
