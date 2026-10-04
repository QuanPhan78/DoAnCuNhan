import os

p_acc = "lib/screens/account/account_screen.dart"
with open(p_acc, "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace("ButtonType.error", "ButtonType.destructive")
with open(p_acc, "w", encoding="utf-8") as f:
    f.write(c)
print("Fixed.")