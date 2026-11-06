import '../../models/installation_model.dart';

abstract class InstallationDataSource {
  Future<InstallationModel?> getInstallationByContractId(String contractId);
  Future<bool> updateInstallationStatus(String contractId, String status);
  Future<bool> completeContract(String contractId);
}