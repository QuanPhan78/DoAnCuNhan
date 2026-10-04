import os
path = "lib/screens/maintenance/maintenance_update_screen.dart"
with open(path, "r", encoding="utf-8") as f: c = f.read()
c = c.replace("value: _status,", "initialValue: _status,")
with open(path, "w", encoding="utf-8") as f: f.write(c)