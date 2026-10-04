import os

path = "lib/screens/contracts/contract_detail_screen.dart"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Make sure RenewalProvider is imported
if "providers/renewal_provider.dart" not in content:
    content = content.replace("import '../../providers/installation_provider.dart';", "import '../../providers/installation_provider.dart';\nimport '../../providers/renewal_provider.dart';")

# Update _buildInstallActions to _buildActions
content = content.replace("Widget _buildInstallActions(", "Widget _buildActions(")
content = content.replace("_buildInstallActions(context, installation.status, contract.id, userRole)", "_buildActions(context, installation.status, contract.id, userRole)")

# If installation is null, we STILL want the action buttons (like Complete Contract or Request Renewal).
# Currently, _buildInstallActions is placed INSIDE `if (installation != null) ...[`
# We need to extract the Actions out of the Installation block!

# Find the place where the Installation block starts and ends.
# The code is:
'''
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
                _buildActions(context, installation.status, contract.id, userRole),
            ],
'''

old_install_block = '''            if (installation != null) ...[
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
                _buildActions(context, installation.status, contract.id, userRole),
            ],'''

# We will replace it so that _buildActions is always rendered, even if installation == null
new_install_block = '''            if (installation != null) ...[
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
            ],
            const SizedBox(height: 16),
            if (installProvider.isLoading)
              const Center(child: CircularProgressIndicator())
            else
              _buildActions(context, installation?.status, contract.id, userRole),'''

content = content.replace(old_install_block, new_install_block)

# Update _buildActions signature and logic
old_build_actions = '''  Widget _buildActions(BuildContext context, String installStatus, String contractId, dynamic userRole) {
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
  }'''

new_build_actions = '''  Widget _buildActions(BuildContext context, String? installStatus, String contractId, dynamic userRole) {
    if (userRole == null) return const SizedBox();
    final canUpdateTask = PermissionManager.hasPermission(userRole, AppPermission.updateTaskStatus);
    final canManageContract = PermissionManager.hasPermission(userRole, AppPermission.manageContracts);
    final canRequestExtension = PermissionManager.hasPermission(userRole, AppPermission.requestExtension);

    List<Widget> buttons = [];

    if (canUpdateTask && installStatus != null) {
      if (installStatus == 'Chưa bắt đầu') {
        buttons.add(_actionButton(context, 'Xác nhận lắp đặt', Colors.orange, () => _confirmInstall(context, contractId)));
      } else if (installStatus == 'Đang thực hiện') {
        buttons.add(_actionButton(context, 'Hoàn thành lắp đặt', Colors.green, () => _completeInstall(context, contractId)));
      }
    }

    if (canManageContract && widget.contract.status != 'Đã thanh lý') {
      buttons.add(_actionButton(context, 'Hoàn thành hợp đồng', Colors.blue, () => _completeContract(context, contractId, userRole)));
    }

    if (canRequestExtension && widget.contract.status != 'Đã thanh lý') {
      buttons.add(_actionButton(context, 'Gia hạn hợp đồng', Colors.purple, () => _showRenewalDialog(context, contractId)));
    }

    if (buttons.isEmpty) return const SizedBox();
    
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: buttons,
    );
  }

  Future<void> _showRenewalDialog(BuildContext context, String contractId) async {
    final durationCtrl = TextEditingController();
    final notesCtrl = TextEditingController();
    
    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Gia hạn hợp đồng'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: durationCtrl,
              decoration: const InputDecoration(labelText: 'Thời gian gia hạn (vd: 1 tháng)'),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: notesCtrl,
              decoration: const InputDecoration(labelText: 'Ghi chú'),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Hủy')),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true), 
            child: const Text('Gửi yêu cầu')
          ),
        ],
      ),
    );

    if (result == true && context.mounted) {
      final user = context.read<AuthProvider>().currentUser;
      if (user == null) return;
      
      final success = await context.read<RenewalProvider>().submitRenewalRequest(
        contractId: contractId,
        customerId: user.id,
        duration: durationCtrl.text,
        notes: notesCtrl.text,
      );
      
      if (!context.mounted) return;
      _showMsg(context, success ? 'Gửi yêu cầu gia hạn thành công (Chờ xử lý)' : 'Có lỗi xảy ra', success);
    }
  }
'''

content = content.replace(old_build_actions, new_build_actions)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated ContractDetailScreen for Renewals")