import os

ds_path = "lib/datasources/contract/contract_datasource.dart"
with open(ds_path, "r", encoding="utf-8") as f:
    ds_content = f.read()
if "updateContractStatus" not in ds_content:
    ds_content = ds_content.replace("}", "  Future<bool> updateContractStatus(String contractId, String newStatus);\n}")
    with open(ds_path, "w", encoding="utf-8") as f: f.write(ds_content)

repo_path = "lib/repositories/contract_repository.dart"
with open(repo_path, "r", encoding="utf-8") as f:
    repo_content = f.read()
if "updateContractStatus" not in repo_content:
    repo_content = repo_content.replace("}", "  Future<bool> updateContractStatus(String contractId, String newStatus) {\n    return _dataSource.updateContractStatus(contractId, newStatus);\n  }\n}")
    with open(repo_path, "w", encoding="utf-8") as f: f.write(repo_content)

remote_ds_path = "lib/datasources/contract/remote_contract_datasource.dart"
with open(remote_ds_path, "r", encoding="utf-8") as f:
    remote_ds_content = f.read()
if "updateContractStatus" not in remote_ds_content:
    remote_ds_content = remote_ds_content.replace("}", "  @override\n  Future<bool> updateContractStatus(String contractId, String newStatus) async {\n    throw UnimplementedError();\n  }\n}")
    with open(remote_ds_path, "w", encoding="utf-8") as f: f.write(remote_ds_content)

prov_path = "lib/providers/contract_provider.dart"
with open(prov_path, "r", encoding="utf-8") as f:
    prov_content = f.read()

# Replace the fake one with real one
old_fake = """
  Future<bool> updateContractStatus(String contractId, String newStatus, Role role, String userId) async {
    // Gọi ép kiểu để gọi mock func
    if (_repository is ContractRepository) {
      // In a real app we'd add this to repo interface. Here we cheat a bit for mock:
      // Actually let's add it to ContractRepository and ContractDataSource!
      return true; // we will update this soon correctly
    }
    return false;
  }
"""
new_real = """
  Future<bool> updateContractStatus(String contractId, String newStatus, Role role, String userId) async {
    _isLoading = true;
    notifyListeners();
    try {
      final success = await _repository.updateContractStatus(contractId, newStatus);
      if (success) {
        await fetchContracts(role, userId);
      }
      return success;
    } catch (e) {
      _errorMessage = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }
"""
prov_content = prov_content.replace(old_fake, new_real)
with open(prov_path, "w", encoding="utf-8") as f: f.write(prov_content)