import os

def insert_provider(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "InstallationProvider" not in content:
        import_str = "import 'package:quan_ly_cho_thue_thiet_bi/providers/installation_provider.dart';\nimport 'package:quan_ly_cho_thue_thiet_bi/repositories/installation_repository.dart';\nimport 'package:quan_ly_cho_thue_thiet_bi/datasources/installation/local_installation_datasource.dart';\n"
        
        if "package:quan_ly_cho_thue_thiet_bi" not in content and "main.dart" in file_path:
            import_str = "import 'providers/installation_provider.dart';\nimport 'repositories/installation_repository.dart';\nimport 'datasources/installation/local_installation_datasource.dart';\n"
            
        content = import_str + content
        
        provider_str = """
          ChangeNotifierProvider(
            create: (_) => InstallationProvider(
              InstallationRepository(LocalInstallationDataSource()),
            ),
          ),"""
        
        content = content.replace("providers: [", "providers: [" + provider_str)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

insert_provider("lib/main.dart")
insert_provider("test/widget_test.dart")