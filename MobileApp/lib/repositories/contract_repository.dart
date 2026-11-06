import '../models/contract_model.dart';
import '../models/role_enum.dart';
import '../datasources/contract/contract_datasource.dart';

class ContractRepository {
  final ContractDataSource _dataSource;
  ContractRepository(this._dataSource);

  Future<List<ContractModel>> getContracts(Role role, String userId) {
    return _dataSource.getContracts(role, userId);
  }

  Future<bool> updateContractStatus(String contractId, String newStatus) {
    return _dataSource.updateContractStatus(contractId, newStatus);
  }

  Future<String> getContractHtml(String contractId, String userId, Role role) {
    return _dataSource.getContractHtml(contractId, userId, role);
  }
}
