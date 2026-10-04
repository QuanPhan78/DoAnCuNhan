import '../../models/contract_model.dart';
import '../../models/role_enum.dart';
import 'contract_datasource.dart';

class RemoteContractDataSource implements ContractDataSource {
  @override
  Future<List<ContractModel>> getContracts(Role role, String userId) async {
    throw UnimplementedError('API chưa có sẵn');
  }

  @override
  Future<bool> updateContractStatus(String contractId, String newStatus) async {
    throw UnimplementedError();
  }
}
