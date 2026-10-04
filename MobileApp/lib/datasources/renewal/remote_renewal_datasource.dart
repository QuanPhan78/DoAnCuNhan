import '../../models/renewal_model.dart';
import 'renewal_datasource.dart';

class RemoteRenewalDataSource implements RenewalDataSource {
  @override
  Future<bool> submitRenewalRequest(RenewalModel request) async {
    throw UnimplementedError('API chưa có sẵn');
  }
}