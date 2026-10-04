import '../../models/contract_model.dart';
import '../../models/role_enum.dart';

abstract class ContractDataSource {
  Future<List<ContractModel>> getContracts(Role role, String userId);
  Future<bool> updateContractStatus(String contractId, String newStatus);
}
