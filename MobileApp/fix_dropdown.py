import os

p = "lib/screens/incidents/create_incident_screen.dart"
with open(p, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace("""    return DropdownButtonFormField<String>(
      value: value,
      hint: Text(hint, style: AppTextStyles.bodySecondary),""", """    return DropdownButtonFormField<String>(
      initialValue: value,
      hint: Text(hint, style: AppTextStyles.bodySecondary),""")

with open(p, "w", encoding="utf-8") as f:
    f.write(c)