import os

# Update app_router.dart
router_path = "lib/routes/app_router.dart"
with open(router_path, "r", encoding="utf-8") as f:
    content = f.read()

if "/contract_detail" not in content:
    content = content.replace("import '../screens/devices/device_detail_screen.dart';", "import '../screens/devices/device_detail_screen.dart';\nimport '../screens/contracts/contract_detail_screen.dart';\nimport '../models/contract_model.dart';")
    
    route_case = """
          case '/contract_detail':
            final contract = settings.arguments as ContractModel;
            return ContractDetailScreen(contract: contract);
"""
    content = content.replace("case '/device_detail':", route_case + "          case '/device_detail':")
    
    with open(router_path, "w", encoding="utf-8") as f:
        f.write(content)


# Insert ContractProvider into main.dart and test/widget_test.dart
def insert_provider(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "ContractProvider" not in content:
        import_str = "import 'package:quan_ly_cho_thue_thiet_bi/providers/contract_provider.dart';\nimport 'package:quan_ly_cho_thue_thiet_bi/repositories/contract_repository.dart';\nimport 'package:quan_ly_cho_thue_thiet_bi/datasources/contract/local_contract_datasource.dart';\n"
        
        if "package:quan_ly_cho_thue_thiet_bi" not in content and "main.dart" in file_path:
            import_str = "import 'providers/contract_provider.dart';\nimport 'repositories/contract_repository.dart';\nimport 'datasources/contract/local_contract_datasource.dart';\n"
            
        content = import_str + content
        
        provider_str = """
          ChangeNotifierProvider(
            create: (_) => ContractProvider(
              ContractRepository(LocalContractDataSource()),
            ),
          ),"""
        
        content = content.replace("providers: [", "providers: [" + provider_str)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

insert_provider("lib/main.dart")
insert_provider("test/widget_test.dart")
print("Completed phase 2")