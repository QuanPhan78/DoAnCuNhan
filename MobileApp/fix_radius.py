import os
import re

p = "lib/screens/onboarding/onboarding_screen.dart"
with open(p, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace("AppRadius.roundRadius ?? BorderRadius.circular(999)", "BorderRadius.circular(AppRadius.round)")

with open(p, "w", encoding="utf-8") as f:
    f.write(c)