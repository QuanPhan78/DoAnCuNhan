import os
import re

p = "lib/widgets/core/custom_textfield.dart"
with open(p, "r", encoding="utf-8") as f:
    c = f.read()

# Add final bool enabled;
c = c.replace("final void Function(String)? onChanged;", "final void Function(String)? onChanged;\n  final bool enabled;")
# Add this.enabled = true
c = c.replace("this.onChanged,", "this.onChanged,\n    this.enabled = true,")
# Pass enabled to TextFormField
c = c.replace("keyboardType: keyboardType,", "keyboardType: keyboardType,\n          enabled: enabled,")

with open(p, "w", encoding="utf-8") as f:
    f.write(c)