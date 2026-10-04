import os

path = "lib/screens/contracts/contract_detail_screen.dart"
with open(path, "r", encoding="utf-8") as f: c = f.read()

c = c.replace(
    "_showMsg(context, success ? 'Cập nhật thành công' : 'Cập nhật thất bại', success);",
    "if (!context.mounted) return;\n      _showMsg(context, success ? 'Cập nhật thành công' : 'Cập nhật thất bại', success);"
)

c = c.replace(
    "_showMsg(context, success ? 'Hoàn thành lắp đặt' : 'Cập nhật thất bại', success);",
    "if (!context.mounted) return;\n      _showMsg(context, success ? 'Hoàn thành lắp đặt' : 'Cập nhật thất bại', success);"
)

c = c.replace(
    "await context.read<InstallationProvider>().completeContract(contractId);",
    "if (!context.mounted) return;\n        await context.read<InstallationProvider>().completeContract(contractId);"
)

c = c.replace(
    "_showMsg(context, 'Đã hoàn thành hợp đồng', true);",
    "if (!context.mounted) return;\n        _showMsg(context, 'Đã hoàn thành hợp đồng', true);"
)

c = c.replace(
    "_showMsg(context, 'Lỗi cập nhật hợp đồng', false);",
    "if (!context.mounted) return;\n        _showMsg(context, 'Lỗi cập nhật hợp đồng', false);"
)

with open(path, "w", encoding="utf-8") as f: f.write(c)