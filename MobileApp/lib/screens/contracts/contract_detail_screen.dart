import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/contract_model.dart';
import '../../providers/installation_provider.dart';
import '../../providers/renewal_provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/contract_provider.dart';
import '../../models/permission_enum.dart';
import '../../utils/permission_manager.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../widgets/core/custom_button.dart';
import '../../widgets/dashboard_widgets.dart'; // StatusBadge, BadgeStatus
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';
import 'package:intl/intl.dart';

class ContractDetailScreen extends StatefulWidget {
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

  BadgeStatus _getBadgeStatus(String? status) {
    if (status == null) return BadgeStatus.neutral;
    switch (status.toLowerCase()) {
      case 'đang hiệu lực':
        return BadgeStatus.success;
      case 'chờ duyệt':
        return BadgeStatus.warning;
      case 'đã thanh lý':
      case 'hoàn thành':
        return BadgeStatus.processing; 
      default:
        return BadgeStatus.neutral;
    }
  }

  String _formatCurrency(double? amount) {
    if (amount == null) return '0 đ';
    final formatter = NumberFormat('#,###', 'vi_VN');
    return '${formatter.format(amount)} đ';
  }

  @override
  Widget build(BuildContext context) {
    final contract = widget.contract;
    final installProvider = context.watch<InstallationProvider>();
    final installation = installProvider.currentInstallation;
    final authProvider = context.read<AuthProvider>();
    final userRole = authProvider.currentUser?.role;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: const CustomAppBar(title: 'Chi tiết Hợp đồng'),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    contract.contractCode ?? 'N/A', 
                    style: AppTextStyles.h1.copyWith(fontSize: 24),
                  ),
                ),
                StatusBadge(
                  text: contract.status ?? 'Không rõ',
                  status: _getBadgeStatus(contract.status),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Section 1 & 2: Thông tin & Khách hàng
            _buildSectionCard(
              title: 'Thông tin chung',
              icon: Icons.info_outline_rounded,
              content: Column(
                children: [
                  _buildInfoRow('Khách hàng', contract.customerName ?? 'Không rõ'),
                  _buildDivider(),
                  _buildInfoRow('Hình thức', contract.rentalType ?? 'N/A'),
                  _buildDivider(),
                  _buildInfoRow('Tổng tiền', _formatCurrency(contract.totalAmount), isHighlight: true),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Section 4: Thời gian thuê (Timeline)
            _buildSectionCard(
              title: 'Thời gian thuê',
              icon: Icons.calendar_month_rounded,
              content: _buildTimeline(contract.rentalStart, contract.rentalEnd),
            ),
            const SizedBox(height: 16),

            // Section 6 & 7: Lắp đặt & Gia hạn
            if ((contract.installationDetails != null && contract.installationDetails!.isNotEmpty) ||
                (contract.extensionDetails != null && contract.extensionDetails!.isNotEmpty))
              _buildSectionCard(
                title: 'Chi tiết phụ',
                icon: Icons.more_time_rounded,
                content: Column(
                  children: [
                    if (contract.installationDetails != null && contract.installationDetails!.isNotEmpty) ...[
                      _buildInfoRow('Lắp đặt', contract.installationDetails!),
                    ],
                    if (contract.extensionDetails != null && contract.extensionDetails!.isNotEmpty) ...[
                      if (contract.installationDetails != null && contract.installationDetails!.isNotEmpty)
                        _buildDivider(),
                      _buildInfoRow('Gia hạn', contract.extensionDetails!),
                    ],
                  ],
                ),
              ),
            if ((contract.installationDetails != null && contract.installationDetails!.isNotEmpty) ||
                (contract.extensionDetails != null && contract.extensionDetails!.isNotEmpty))
              const SizedBox(height: 16),

            // Installation Details (from Provider)
            if (installation != null) ...[
              _buildSectionCard(
                title: 'Tiến độ lắp đặt',
                icon: Icons.engineering_rounded,
                content: Column(
                  children: [
                    _buildInfoRow('Trạng thái', installation.status, isHighlight: true),
                    if (installation.expectedDate != null && installation.expectedDate!.isNotEmpty) ...[
                      _buildDivider(),
                      _buildInfoRow('Dự kiến', installation.expectedDate!),
                    ],
                    if (installation.actualDate != null && installation.actualDate!.isNotEmpty) ...[
                      _buildDivider(),
                      _buildInfoRow('Thực tế', installation.actualDate!),
                    ],
                    if (installation.assignedStaffName != null && installation.assignedStaffName!.isNotEmpty) ...[
                      _buildDivider(),
                      _buildInfoRow('Nhân viên', installation.assignedStaffName!),
                    ],
                    if (installation.notes != null && installation.notes!.isNotEmpty) ...[
                      _buildDivider(),
                      _buildInfoRow('Ghi chú', installation.notes!),
                    ],
                  ],
                ),
              ),
              const SizedBox(height: 16),
            ],

            // Section 3: Thiết bị thuê
            _buildSectionCard(
              title: 'Thiết bị thuê',
              icon: Icons.devices_rounded,
              content: (contract.deviceIds == null || contract.deviceIds!.isEmpty)
                  ? const Text('Không có thiết bị nào trong hợp đồng này.', style: AppTextStyles.bodySecondary)
                  : Column(
                      children: contract.deviceIds!.map((deviceId) {
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 8.0),
                          child: Row(
                            children: [
                              const Icon(Icons.check_circle_rounded, color: AppColors.success, size: 20),
                              const SizedBox(width: 8),
                              Expanded(child: Text('Mã thiết bị: $deviceId', style: AppTextStyles.body)),
                            ],
                          ),
                        );
                      }).toList(),
                    ),
            ),
            const SizedBox(height: 32),

            // Actions
            if (installProvider.isLoading)
              const Center(child: CircularProgressIndicator(color: AppColors.primary))
            else
              _buildActions(context, installation?.status, contract.id, userRole),
              
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  // REUSABLE UI
  Widget _buildSectionCard({required String title, required IconData icon, required Widget content}) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: AppRadius.lgRadius,
        boxShadow: AppShadows.cardShadow,
        border: Border.all(color: AppColors.divider),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 20, color: AppColors.primary),
              const SizedBox(width: 8),
              Text(title, style: AppTextStyles.h2),
            ],
          ),
          const SizedBox(height: 16),
          content,
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value, {bool isHighlight = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(label, style: AppTextStyles.bodySecondary),
          ),
          Expanded(
            child: Text(
              value,
              style: AppTextStyles.body.copyWith(
                fontWeight: isHighlight ? FontWeight.bold : FontWeight.w500,
                color: isHighlight ? AppColors.error : AppColors.textPrimary,
              ),
              textAlign: TextAlign.right,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDivider() {
    return const Padding(
      padding: EdgeInsets.symmetric(vertical: 8),
      child: Divider(color: AppColors.divider, height: 1),
    );
  }

  Widget _buildTimeline(String? start, String? end) {
    return Column(
      children: [
        _buildTimelineStep(title: 'Bắt đầu thuê', date: start ?? 'N/A', isLast: false, color: AppColors.success),
        _buildTimelineStep(title: 'Dự kiến kết thúc', date: end ?? 'N/A', isLast: true, color: AppColors.warning),
      ],
    );
  }

  Widget _buildTimelineStep({required String title, required String date, required bool isLast, required Color color}) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Column(
          children: [
            Container(
              width: 12,
              height: 12,
              decoration: BoxDecoration(color: color, shape: BoxShape.circle),
            ),
            if (!isLast)
              Container(
                width: 2,
                height: 30,
                color: AppColors.divider,
              ),
          ],
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: AppTextStyles.bodySecondary.copyWith(fontSize: 12)),
              Text(date, style: AppTextStyles.body.copyWith(fontWeight: FontWeight.bold)),
              if (!isLast) const SizedBox(height: 16),
            ],
          ),
        ),
      ],
    );
  }

  // LOGIC ACTIONS (Unchanged in logic, only UI updated)
  Widget _buildActions(BuildContext context, String? installStatus, String contractId, dynamic userRole) {
    if (userRole == null) return const SizedBox();
    final canUpdateTask = PermissionManager.hasPermission(userRole, AppPermission.updateTaskStatus);
    final canManageContract = PermissionManager.hasPermission(userRole, AppPermission.manageContracts);
    final canRequestExtension = PermissionManager.hasPermission(userRole, AppPermission.requestExtension);

    List<Widget> buttons = [];

    if (canUpdateTask && installStatus != null) {
      if (installStatus == 'Chưa bắt đầu') {
        buttons.add(CustomButton(text: 'Xác nhận lắp đặt', onPressed: () => _confirmInstall(context, contractId), type: ButtonType.primary, isFullWidth: true));
      } else if (installStatus == 'Đang thực hiện') {
        buttons.add(CustomButton(text: 'Hoàn thành lắp đặt', onPressed: () => _completeInstall(context, contractId), type: ButtonType.primary, isFullWidth: true));
      }
    }

    if (canManageContract && widget.contract.status != 'Đã thanh lý') {
      buttons.add(CustomButton(text: 'Hoàn thành hợp đồng', onPressed: () => _completeContract(context, contractId, userRole), type: ButtonType.secondary, isFullWidth: true));
    }

    if (canRequestExtension && widget.contract.status != 'Đã thanh lý') {
      buttons.add(CustomButton(text: 'Gia hạn hợp đồng', onPressed: () => _showRenewalDialog(context, contractId), type: ButtonType.outline, isFullWidth: true));
    }

    if (buttons.isEmpty) return const SizedBox();
    
    return Column(
      children: buttons.map((btn) => Padding(padding: const EdgeInsets.only(bottom: 12), child: btn)).toList(),
    );
  }

  Future<void> _showRenewalDialog(BuildContext context, String contractId) async {
    final durationCtrl = TextEditingController();
    final notesCtrl = TextEditingController();
    
    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: AppRadius.lgRadius),
        title: const Text('Gia hạn hợp đồng', style: AppTextStyles.h2),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: durationCtrl,
              decoration: const InputDecoration(labelText: 'Thời gian gia hạn (vd: 1 tháng)'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: notesCtrl,
              decoration: const InputDecoration(labelText: 'Ghi chú'),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Hủy')),
          CustomButton(
            text: 'Gửi yêu cầu',
            onPressed: () => Navigator.pop(ctx, true),
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

  void _showMsg(BuildContext context, String msg, bool isSuccess) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(msg), 
        backgroundColor: isSuccess ? AppColors.success : AppColors.error,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  Future<void> _confirmInstall(BuildContext context, String contractId) async {
    final confirm = await _showConfirmDialog(context, 'Bạn có chắc muốn xác nhận bắt đầu lắp đặt?');
    if (confirm == true) {
      if (!context.mounted) return;
      final success = await context.read<InstallationProvider>().confirmInstallation(contractId);
      if (!context.mounted) return;
      _showMsg(context, success ? 'Cập nhật thành công' : 'Cập nhật thất bại', success);
    }
  }

  Future<void> _completeInstall(BuildContext context, String contractId) async {
    final confirm = await _showConfirmDialog(context, 'Xác nhận hoàn thành quá trình lắp đặt?');
    if (confirm == true) {
      if (!context.mounted) return;
      final success = await context.read<InstallationProvider>().completeInstallation(contractId);
      if (!context.mounted) return;
      _showMsg(context, success ? 'Hoàn thành lắp đặt' : 'Cập nhật thất bại', success);
    }
  }

  Future<void> _completeContract(BuildContext context, String contractId, dynamic userRole) async {
    final confirm = await _showConfirmDialog(context, 'Xác nhận hợp đồng này đã hoàn thành/thanh lý?');
    if (confirm == true) {
      if (!context.mounted) return;
      final success = await context.read<ContractProvider>().updateContractStatus(
        contractId, 'Đã thanh lý', userRole, context.read<AuthProvider>().currentUser!.id
      );
      if (success) {
        if (!context.mounted) return;
        await context.read<InstallationProvider>().completeContract(contractId);
        
        if (!context.mounted) return;
        _showMsg(context, 'Đã hoàn thành hợp đồng', true);
        Navigator.pop(context); 
      } else {
        if (!context.mounted) return;
        _showMsg(context, 'Lỗi cập nhật hợp đồng', false);
      }
    }
  }

  Future<bool?> _showConfirmDialog(BuildContext context, String message) {
    return showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: AppRadius.lgRadius),
        title: const Text('Xác nhận', style: AppTextStyles.h2),
        content: Text(message, style: AppTextStyles.body),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Hủy', style: TextStyle(color: AppColors.textSecondary))),
          CustomButton(
            text: 'Đồng ý',
            onPressed: () => Navigator.pop(ctx, true),
          ),
        ],
      ),
    );
  }
}
