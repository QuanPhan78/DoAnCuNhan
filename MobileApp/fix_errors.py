import os

p_card = "lib/widgets/maintenance_card.dart"
with open(p_card, "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace("BadgeStatus.info", "BadgeStatus.neutral")
with open(p_card, "w", encoding="utf-8") as f:
    f.write(c)

p_update = "lib/screens/maintenance/maintenance_update_screen.dart"
with open(p_update, "r", encoding="utf-8") as f:
    c2 = f.read()
c2 = c2.replace("value: _status,", "initialValue: _status,")
with open(p_update, "w", encoding="utf-8") as f:
    f.write(c2)

print("Fixed errors.")