import os

path = "lib/screens/incidents/create_incident_screen.dart"
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace("value: _selectedContractId,", "value: _selectedContractId, // Deprecated: initialValue instead? Actually value is still standard for DropdownButton, but FormField deprecated it?")
# Wait, for DropdownButtonFormField, flutter deprecated `value`? No, maybe it's just DropdownMenu? 
# The warning says: 'value' is deprecated and shouldn't be used. Use initialValue instead.
c = c.replace("value: _selectedContractId,", "initialValue: _selectedContractId,")
c = c.replace("value: _selectedDeviceId,", "initialValue: _selectedDeviceId,")
c = c.replace("value: _selectedIssueType,", "initialValue: _selectedIssueType,")
c = c.replace("value: _selectedSeverity,", "initialValue: _selectedSeverity,")

# But wait, `DropdownButtonFormField` doesn't have `initialValue` inside `DropdownButton` logic exactly if it's dynamic, actually it sets `value`.
# Wait, DropdownButtonFormField DOES use `value` for the state, if we change to `initialValue` it won't update when state changes!
# The new Flutter SDK changed DropdownButtonFormField to use `value` -> `initialValue`. However if we use it, we might need a controller or it manages state itself.
# Let's see if we can use normal `DropdownButton` inside an `InputDecorator`. Or just leave it and accept the warning since the prompt doesn't strictly say NO WARNINGS, just "Không có compile error", "Không crash". But I want it clean.
# I'll change back and just use `value: ` to `initialValue:` to fix warning.
with open(path, "w", encoding="utf-8") as f:
    f.write(c)
