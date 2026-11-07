import '../../models/rental_request_model.dart';
import '../../datasources/rental/rental_datasource.dart';

class RentalRepository {
  final RentalDataSource _dataSource;

  RentalRepository(this._dataSource);

  Future<List<RentalRequestModel>> getRentals({String? userId}) async {
    return await _dataSource.getRentals(userId: userId);
  }

  Future<RentalRequestModel> createRental(RentalRequestModel request) async {
    return await _dataSource.createRental(request);
  }

  Future<RentalRequestModel> quoteRental(RentalRequestModel request) =>
      _dataSource.quoteRental(request);

  Future<void> requestCancellation(String id, String reason) async {
    await _dataSource.requestCancellation(id, reason);
  }
}
