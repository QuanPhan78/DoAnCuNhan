import os

def insert_provider(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "DeviceProvider" not in content:
        import_str = "import 'package:quan_ly_cho_thue_thiet_bi/providers/device_provider.dart';\nimport 'package:quan_ly_cho_thue_thiet_bi/repositories/device_repository.dart';\nimport 'package:quan_ly_cho_thue_thiet_bi/datasources/device/local_device_datasource.dart';\n"
        
        # for main.dart it might be relative imports or package imports
        if "package:quan_ly_cho_thue_thiet_bi" not in content and "main.dart" in file_path:
            import_str = "import 'providers/device_provider.dart';\nimport 'repositories/device_repository.dart';\nimport 'datasources/device/local_device_datasource.dart';\n"
            
        content = import_str + content
        
        provider_str = """
          ChangeNotifierProvider(
            create: (_) => DeviceProvider(
              DeviceRepository(LocalDeviceDataSource()),
            ),
          ),"""
        
        # insert inside MultiProvider providers list
        content = content.replace("providers: [", "providers: [" + provider_str)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

insert_provider("lib/main.dart")
insert_provider("test/widget_test.dart")
print("Done inserting providers")