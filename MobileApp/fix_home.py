import os
import re

p = "lib/screens/home/home_screen.dart"
with open(p, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace("""      default:
        return const EmptyState(message: 'Vai trò không hợp lệ');""", "")

with open(p, "w", encoding="utf-8") as f:
    f.write(c)