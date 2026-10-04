import os
p = "lib/widgets/core/state_widgets.dart"
with open(p, "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace("Thá»­ láº¡i", "Thử lại")
with open(p, "w", encoding="utf-8") as f:
    f.write(c)