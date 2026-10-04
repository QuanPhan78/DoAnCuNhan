import os
import re
p = "lib/widgets/custom_image_widget.dart"
with open(p, "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace("import '../theme/app_radius.dart';", "")
with open(p, "w", encoding="utf-8") as f:
    f.write(c)