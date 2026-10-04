import os

p_create = "lib/screens/feedbacks/create_feedback_screen.dart"
with open(p_create, "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace("value: _selectedType,", "initialValue: _selectedType,")
with open(p_create, "w", encoding="utf-8") as f:
    f.write(c)

p_detail = "lib/screens/feedbacks/feedback_detail_screen.dart"
with open(p_detail, "r", encoding="utf-8") as f:
    c2 = f.read()
c2 = c2.replace("AppRadius.fullRadius", "BorderRadius.circular(100)")
with open(p_detail, "w", encoding="utf-8") as f:
    f.write(c2)

print("Fixed errors.")