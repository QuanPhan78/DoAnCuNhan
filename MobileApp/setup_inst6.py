import os

path = "lib/screens/contracts/contract_detail_screen.dart"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

imports = """
import '../../providers/auth_provider.dart';
import '../../providers/contract_provider.dart';
"""
content = content.replace("import '../../models/permission_enum.dart';", imports.strip() + "\nimport '../../models/permission_enum.dart';")
with open(path, "w", encoding="utf-8") as f:
    f.write(content)