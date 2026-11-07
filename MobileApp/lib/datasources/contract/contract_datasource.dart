import '../../models/contract_model.dart';
import '../../models/role_enum.dart';

abstract class ContractDataSource {
  Future<List<ContractModel>> getContracts(Role role, String userId);
  Future<ContractModel> getContract(String contractId, String userId, Role role);
}
