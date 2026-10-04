import os

router_path = "lib/routes/app_router.dart"
with open(router_path, "r", encoding="utf-8") as f:
    content = f.read()

if "/maintenance_detail" not in content:
    imports = """import '../screens/maintenance/maintenance_list_screen.dart';
import '../screens/maintenance/maintenance_detail_screen.dart';
import '../screens/maintenance/maintenance_update_screen.dart';
import '../models/maintenance_model.dart';
"""
    content = content.replace("import '../models/incident_model.dart';", "import '../models/incident_model.dart';\n" + imports)
    
    routes = """
          case '/maintenances':
            return const MaintenanceListScreen();
          case '/maintenance_detail':
            final m = settings.arguments as MaintenanceModel;
            return MaintenanceDetailScreen(maintenance: m);
          case '/maintenance_update':
            final m2 = settings.arguments as MaintenanceModel;
            return MaintenanceUpdateScreen(maintenance: m2);
"""
    content = content.replace("case '/device_detail':", routes + "          case '/device_detail':")
    with open(router_path, "w", encoding="utf-8") as f:
        f.write(content)

dash_path = "lib/screens/dashboard/dashboard_screen.dart"
with open(dash_path, "r", encoding="utf-8") as f:
    dash = f.read()

dash = dash.replace("import '../maintenance/maintenance_screen.dart';", "import '../maintenance/maintenance_list_screen.dart';")
dash = dash.replace("MaintenanceScreen()", "MaintenanceListScreen()")

with open(dash_path, "w", encoding="utf-8") as f:
    f.write(dash)

print("Router and Dashboard updated for Maintenance")