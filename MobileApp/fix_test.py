import os
import re

p = "test/widget_test.dart"
with open(p, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace("Chào mừng đến với hệ thống", "Quản lý thiết bị điện tử")

with open(p, "w", encoding="utf-8") as f:
    f.write(c)