import os

path = "lib/screens/feedbacks/create_feedback_screen.dart"
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace("value: _selectedType,", "initialValue: _selectedType,")
c = c.replace("'Mã ${_selectedType} liên quan'", "'Mã $_selectedType liên quan'")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)