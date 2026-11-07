import '../models/contract_model.dart';
import '../models/role_enum.dart';
import '../datasources/contract/contract_datasource.dart';

class ContractRepository {
  final ContractDataSource _dataSource;
  ContractRepository(this._dataSource);

  Future<List<ContractModel>> getContracts(Role role, String userId) {
    return _dataSource.getContracts(role, userId);
  }

  Future<ContractModel> getContract(String contractId, String userId, Role role) {
    return _dataSource.getContract(contractId, userId, role);
  }
}
