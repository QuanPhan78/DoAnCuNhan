import os
import re

p = "lib/theme/app_theme.dart"
with open(p, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace("CupertinoPageTransitionsBuilder()", "ZoomPageTransitionsBuilder()")

with open(p, "w", encoding="utf-8") as f:
    f.write(c)