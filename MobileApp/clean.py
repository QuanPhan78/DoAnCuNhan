import os

path = "lib/screens/contracts/contract_detail_screen.dart"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Remove unused variable
content = content.replace("final allDevices = context.read<DeviceProvider>().devices;", "")

# Remove .toList() from the spread operator
content = content.replace("}).toList(),", "}),")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Cleaned up")