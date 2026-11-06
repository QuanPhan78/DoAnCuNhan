import '../../models/renewal_model.dart';
import 'renewal_datasource.dart';

class LocalRenewalDataSource implements RenewalDataSource {
  // Mock in-memory storage cho các yêu cầu gia hạn
  static final List<RenewalModel> _requests = [];

  @override
  Future<bool> submitRenewalRequest(RenewalModel request) async {
    await Future.delayed(const Duration(milliseconds: 500));
    _requests.add(request);
    return true; // Luôn thành công trong mock
  }
}