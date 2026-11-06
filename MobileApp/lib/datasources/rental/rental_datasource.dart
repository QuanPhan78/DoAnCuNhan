import '../../models/rental_request_model.dart';

abstract class RentalDataSource {
  Future<List<RentalRequestModel>> getRentals({String? userId});
  Future<RentalRequestModel> quoteRental(RentalRequestModel request);
  Future<RentalRequestModel> createRental(RentalRequestModel request);
  Future<void> requestCancellation(String id, String reason);
}
