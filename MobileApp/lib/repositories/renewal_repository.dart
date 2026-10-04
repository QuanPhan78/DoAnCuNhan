import '../models/renewal_model.dart';
import '../datasources/renewal/renewal_datasource.dart';

class RenewalRepository {
  final RenewalDataSource _dataSource;
  RenewalRepository(this._dataSource);

  Future<bool> submitRenewalRequest(RenewalModel request) {
    return _dataSource.submitRenewalRequest(request);
  }
}