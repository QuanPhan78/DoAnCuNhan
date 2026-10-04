import '../../models/renewal_model.dart';

abstract class RenewalDataSource {
  Future<bool> submitRenewalRequest(RenewalModel request);
}