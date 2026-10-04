import os

path = "lib/screens/contracts/contract_detail_screen.dart"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Add new imports
new_imports = """
import '../../providers/installation_provider.dart';
import '../../models/permission_enum.dart';
import '../../utils/permission_manager.dart';
"""
content = content.replace("import '../../providers/device_provider.dart';", "import '../../providers/device_provider.dart';\n" + new_imports.strip())

# Add Stateful wrapper for ContractDetailScreen since we need to fetch installation
# We'll just convert it using regex or replacement
old_class_start = """class ContractDetailScreen extends StatelessWidget {
  final ContractModel contract;

  const ContractDetailScreen({super.key, required this.contract});

  @override
  Widget build(BuildContext context) {"""

new_class = """class ContractDetailScreen extends StatefulWidget {
  final ContractModel contract;

  const ContractDetailScreen({super.key, required this.contract});

  @override
  State<ContractDetailScreen> createState() => _ContractDetailScreenState();
}

class _ContractDetailScreenState extends State<ContractDetailScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<InstallationProvider>().fetchInstallation(widget.contract.id);
    });
  }

  @override
  Widget build(BuildContext context) {
    final contract = widget.contract;
    final installProvider = context.watch<InstallationProvider>();
    final installation = installProvider.currentInstallation;
    final authProvider = context.read<AuthProvider>();
    final userRole = authProvider.currentUser?.role;
"""
content = content.replace(old_class_start, new_class)

# Add Installation Section before "DANH SÁCH THIẾT BỊ"
install_section = """
            if (installation != null) ...[
              const Divider(height: 32),
              const Text('THÔNG TIN LẮP ĐẶT', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.blue)),
              const SizedBox(height: 16),
              _buildInfoRow('Trạng thái', installation.status, valueColor: _getInstallStatusColor(installation.status)),
              if (installation.expectedDate != null && installation.expectedDate!.isNotEmpty)
                _buildInfoRow('Dự kiến', installation.expectedDate!),
              if (installation.actualDate != null && installation.actualDate!.isNotEmpty)
                _buildInfoRow('Thực tế', installation.actualDate!),
              if (installation.assignedStaffName != null && installation.assignedStaffName!.isNotEmpty)
                _buildInfoRow('Nhân viên', installation.assignedStaffName!),
              if (installation.notes != null && installation.notes!.isNotEmpty)
                _buildInfoRow('Ghi chú', installation.notes!),
              
              const SizedBox(height: 16),
              if (installProvider.isLoading)
                const Center(child: CircularProgressIndicator())
              else
                _buildInstallActions(context, installation.status, contract.id, userRole),
            ],
"""
content = content.replace("const Divider(height: 32),\n            const Text('DANH SÁCH THIẾT BỊ'", install_section + "            const Divider(height: 32),\n            const Text('DANH SÁCH THIẾT BỊ'")

# Add helper methods
helpers = """
  Color _getInstallStatusColor(String status) {
    if (status == 'Chưa bắt đầu') return Colors.grey;
    if (status == 'Đang thực hiện') return Colors.orange;
    if (status == 'Đã hoàn thành') return Colors.green;
    return Colors.black;
  }

  Widget _buildInstallActions(BuildContext context, String installStatus, String contractId, dynamic userRole) {
    if (userRole == null) return const SizedBox();
    final canUpdateTask = PermissionManager.hasPermission(userRole, AppPermission.updateTaskStatus);
    final canManageContract = PermissionManager.hasPermission(userRole, AppPermission.manageContracts);

    List<Widget> buttons = [];

    if (canUpdateTask) {
      if (installStatus == 'Chưa bắt đầu') {
        buttons.add(_actionButton(context, 'Xác nhận lắp đặt', Colors.orange, () => _confirmInstall(context, contractId)));
      } else if (installStatus == 'Đang thực hiện') {
        buttons.add(_actionButton(context, 'Hoàn thành lắp đặt', Colors.green, () => _completeInstall(context, contractId)));
      }
    }

    if (canManageContract && widget.contract.status != 'Đã thanh lý') {
      buttons.add(_actionButton(context, 'Hoàn thành hợp đồng', Colors.blue, () => _completeContract(context, contractId, userRole)));
    }

    if (buttons.isEmpty) return const SizedBox();
    
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: buttons,
    );
  }

  Widget _actionButton(BuildContext context, String text, Color color, VoidCallback onPressed) {
    return ElevatedButton(
      style: ElevatedButton.styleFrom(backgroundColor: color, foregroundColor: Colors.white),
      onPressed: onPressed,
      child: Text(text),
    );
  }

  void _showMsg(BuildContext context, String msg, bool isSuccess) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg), backgroundColor: isSuccess ? Colors.green : Colors.red),
    );
  }

  Future<void> _confirmInstall(BuildContext context, String contractId) async {
    final confirm = await _showConfirmDialog(context, 'Bạn có chắc muốn xác nhận bắt đầu lắp đặt?');
    if (confirm == true) {
      final success = await context.read<InstallationProvider>().confirmInstallation(contractId);
      _showMsg(context, success ? 'Cập nhật thành công' : 'Cập nhật thất bại', success);
    }
  }

  Future<void> _completeInstall(BuildContext context, String contractId) async {
    final confirm = await _showConfirmDialog(context, 'Xác nhận hoàn thành quá trình lắp đặt?');
    if (confirm == true) {
      final success = await context.read<InstallationProvider>().completeInstallation(contractId);
      _showMsg(context, success ? 'Hoàn thành lắp đặt' : 'Cập nhật thất bại', success);
    }
  }

  Future<void> _completeContract(BuildContext context, String contractId, dynamic userRole) async {
    final confirm = await _showConfirmDialog(context, 'Xác nhận hợp đồng này đã hoàn thành/thanh lý?');
    if (confirm == true) {
      final success = await context.read<ContractProvider>().updateContractStatus(
        contractId, 'Đã thanh lý', userRole, context.read<AuthProvider>().currentUser!.id
      );
      if (success) {
        // Also call InstallationProvider's completeContract if needed
        await context.read<InstallationProvider>().completeContract(contractId);
        
        // update widget's local UI state temporarily by re-fetching or navigating back
        _showMsg(context, 'Đã hoàn thành hợp đồng', true);
        Navigator.pop(context); // Trở về danh sách để refresh
      } else {
        _showMsg(context, 'Lỗi cập nhật hợp đồng', false);
      }
    }
  }

  Future<bool?> _showConfirmDialog(BuildContext context, String message) {
    return showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Xác nhận'),
        content: Text(message),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Hủy')),
          ElevatedButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Đồng ý')),
        ],
      ),
    );
  }
"""
content = content.replace("  Widget _buildInfoRow", helpers + "\n  Widget _buildInfoRow")
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated ContractDetailScreen")