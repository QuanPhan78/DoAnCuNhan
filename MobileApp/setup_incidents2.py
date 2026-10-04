import os

# 1. Update Providers in main.dart and test/widget_test.dart
def insert_provider(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "IncidentProvider" not in content:
        import_str = "import 'package:quan_ly_cho_thue_thiet_bi/providers/incident_provider.dart';\nimport 'package:quan_ly_cho_thue_thiet_bi/repositories/incident_repository.dart';\nimport 'package:quan_ly_cho_thue_thiet_bi/datasources/incident/local_incident_datasource.dart';\n"
        if "package:quan_ly_cho_thue_thiet_bi" not in content and "main.dart" in file_path:
            import_str = "import 'providers/incident_provider.dart';\nimport 'repositories/incident_repository.dart';\nimport 'datasources/incident/local_incident_datasource.dart';\n"
        content = import_str + content
        provider_str = """
          ChangeNotifierProvider(
            create: (_) => IncidentProvider(
              IncidentRepository(LocalIncidentDataSource()),
            ),
          ),"""
        content = content.replace("providers: [", "providers: [" + provider_str)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

insert_provider("lib/main.dart")
insert_provider("test/widget_test.dart")

# 2. Update Router
router_path = "lib/routes/app_router.dart"
with open(router_path, "r", encoding="utf-8") as f:
    content = f.read()

if "/incident_detail" not in content:
    content = content.replace("import '../screens/promotions/promotion_detail_screen.dart';", "import '../screens/promotions/promotion_detail_screen.dart';\nimport '../screens/incidents/incident_list_screen.dart';\nimport '../screens/incidents/incident_detail_screen.dart';\nimport '../screens/incidents/create_incident_screen.dart';\nimport '../models/incident_model.dart';")
    routes = """
          case '/incidents':
            return const IncidentListScreen();
          case '/create_incident':
            return const CreateIncidentScreen();
          case '/incident_detail':
            final inc = settings.arguments as IncidentModel;
            return IncidentDetailScreen(incident: inc);
"""
    content = content.replace("case '/device_detail':", routes + "          case '/device_detail':")
    with open(router_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Injected Provider and Router")