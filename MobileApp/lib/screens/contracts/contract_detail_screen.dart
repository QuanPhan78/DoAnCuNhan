import '../tasks/handover_screen.dart';
import 'sign_contract_screen.dart';
import 'debt_screen.dart';
import '../../services/customer_contract_service.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/contract_model.dart';
import '../../models/role_enum.dart';
import '../../models/installation_model.dart';
import '../../providers/installation_provider.dart';
import '../../providers/renewal_provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/contract_provider.dart';
import '../../providers/rental_provider.dart';
import '../../models/permission_enum.dart';
import '../../utils/permission_manager.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../widgets/core/custom_button.dart';
import '../../widgets/cancellation_reason_dialog.dart';
import '../../widgets/dashboard_widgets.dart'; // StatusBadge, BadgeStatus
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';
import 'package:intl/intl.dart';
import 'contract_pdf_viewer_screen.dart';

class ContractDetailScreen extends StatefulWidget {
  final ContractModel contract;

  const ContractDetailScreen({super.key, required this.contract});

  @override
  State<ContractDetailScreen> createState() => _ContractDetailScreenState();
}

class _ContractDetailScreenState extends State<ContractDetailScreen> {
  late ContractModel _contract;
  bool _updatingInstallation = false;

  @override
  void initState() {
    super.initState();
    _contract = widget.contract;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      context.read<InstallationProvider>().fetchInstallation(widget.contract.id);
      _refreshContract();
    });
  }

  Future<void> _refreshContract() async {
    final user = context.read<AuthProvider>().currentUser;
    if (user == null) return;
    try {
      final contract = await context.read<ContractProvider>().getContract(
        _contract.id, user.id, user.role,
      );
      if (mounted) setState(() => _contract = contract);
    } catch (error) {
      if (mounted) _showMsg(context, error.toString().replaceFirst('Exception: ', ''), false);
    }
  }

  Future<void> _requestCancellation() async {
    final reason = await showCancellationReasonDialog(context);
    if (reason == null || !mounted) return;
    final rentals = context.read<RentalProvider>();
    final contracts = context.read<ContractProvider>();
    final user = context.read<AuthProvider>().currentUser;
    if (rentals.isLoading || user == null) return;
    try {
      await rentals.requestCancellation(_contract.id, reason);
      if (!mounted) return;
      _showMsg(context, 'Đã gửi yêu cầu hủy. Vui lòng chờ duyệt.', true);
      await Future.wait([_refreshContract(), contracts.fetchContracts(user.role, user.id)]);
    } catch (error) {
      if (mounted) _showMsg(context, error.toString().replaceFirst('Exception: ', ''), false);
    }
  }

  void _openPdfViewer(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ContractPdfViewerScreen(contract: _contract),
      ),
    );
  }

  BadgeStatus _getBadgeStatus(String? status) {
    if (status == null) return BadgeStatus.neutral;
    switch (status.toLowerCase()) {
      case 'đang hiệu lực':
        return BadgeStatus.success;
      case 'chờ duyệt':
      case 'yêu cầu hủy':
      case 'đã trả máy (chờ quyết toán)':
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
    final contract = _contract;
    final installProvider = context.watch<InstallationProvider>();
    final currentInstallation = installProvider.currentInstallation;
    final installation = currentInstallation?.contractId == contract.id ? currentInstallation : null;
    final authProvider = context.read<AuthProvider>();
    final user = authProvider.currentUser;
    final canRequestCancellation = user?.role == Role.customer &&
        user?.id == contract.customerId && contract.statusCode == 0 &&
        !contract.cancellationRequested;
    final rentalLoading = context.watch<RentalProvider>().isLoading;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: CustomAppBar(
        title: 'Chi tiết Hợp đồng',
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            tooltip: 'Tải lại hợp đồng',
            onPressed: () {
              installProvider.fetchInstallation(contract.id);
              _refreshContract();
            },
          ),
          IconButton(
            icon: const Icon(Icons.picture_as_pdf_rounded, color: Colors.white),
            tooltip: 'Xem file PDF',
            onPressed: () => _openPdfViewer(context),
          ),
        ],
      ),
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
                Flexible(
                  child: StatusBadge(
                    text: contract.status ?? 'Không rõ',
                    status: _getBadgeStatus(contract.status),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            OutlinedButton.icon(
              onPressed: () => _openPdfViewer(context),
              icon: const Icon(Icons.picture_as_pdf_rounded, color: AppColors.primary),
              label: const Text(
                'Xem văn bản hợp đồng (PDF)',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
              ),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 14),
                side: const BorderSide(color: AppColors.primary, width: 1.5),
                shape: RoundedRectangleBorder(borderRadius: AppRadius.mdRadius),
                backgroundColor: AppColors.primary.withValues(alpha: 0.04),
              ),
            ),
            const SizedBox(height: 20),

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
                  const Divider(),
                  _buildInfoRow('Trạng thái thanh toán', contract.paymentStatus ?? 'Chưa xác định'),
                  if (contract.cancellationReason?.isNotEmpty == true) ...[
                    _buildDivider(),
                    _buildInfoRow('Lý do hủy', contract.cancellationReason!),
                  ],
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

            if (installProvider.errorMessage case final message?) ...[
              Text(message, style: const TextStyle(color: AppColors.error)),
              const SizedBox(height: 16),
            ],
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
            if (canRequestCancellation) ...[
              CustomButton(
                text: 'Yêu cầu hủy',
                type: ButtonType.destructive,
                onPressed: rentalLoading ? null : _requestCancellation,
                isLoading: rentalLoading,
              ),
              const SizedBox(height: 12),
            ],
            if (installProvider.isLoading)
              const Center(child: CircularProgressIndicator(color: AppColors.primary))
            else
              _buildActions(context, installation, contract.id, user?.role),
              
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

  Widget _buildActions(BuildContext context, InstallationModel? installation, String contractId, Role? userRole) {
    if (userRole == null) return const SizedBox();
    final canRequestExtension = PermissionManager.hasPermission(userRole, AppPermission.requestExtension);

    List<Widget> buttons = [];
    if (userRole == Role.staff) {
      buttons.add(CustomButton(text: 'Biên bản giao nhận thiết bị', type: ButtonType.outline,
        onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => HandoverScreen(contractId: contractId)))));
    }
    if (userRole == Role.customer) {
      if (_contract.statusCode == 0 && !_contract.cancellationRequested && _contract.customerSigned != true) {
        buttons.add(CustomButton(text: 'Ký hợp đồng', icon: Icons.draw_outlined, onPressed: () async {
          final signed = await Navigator.push<bool>(context, MaterialPageRoute(builder: (_) => SignContractScreen(contract: _contract)));
          if (signed == true) { await _refreshContract(); }
        }));
      }
      buttons.add(CustomButton(text: 'Công nợ và thanh toán', type: ButtonType.outline,
        onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => DebtScreen(contractId: contractId)))));
      buttons.add(CustomButton(text: 'Lịch sử gia hạn', type: ButtonType.outline, onPressed: () => _showRenewalHistory()));
    }


    if (installation != null && installation.canUpdate && installation.taskId != null &&
        (installation.statusCode == 0 || installation.statusCode == 1)) {
      final starting = installation.statusCode == 0;
      buttons.add(CustomButton(
        text: starting ? 'Bắt đầu lắp đặt' : 'Hoàn thành lắp đặt',
        onPressed: _updatingInstallation ? null : () => _updateInstallation(installation, starting ? 1 : 2),
      ));
    }

    if (canRequestExtension && _contract.statusCode == 1) {
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
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Số ngày gia hạn (1–365)'),
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
      _showMsg(context, success ? 'Gửi yêu cầu gia hạn thành công (Chờ xử lý)' : context.read<RenewalProvider>().errorMessage ?? 'Không gửi được yêu cầu.', success);
      if (success) await _refreshContract();
    }
  }

  Future<void> _showRenewalHistory() async {
    try {
      final rows = await CustomerContractService.renewals(_contract.id);
      if (!mounted) return;
      await showDialog<void>(context: context, builder: (ctx) => AlertDialog(title: const Text('Lịch sử gia hạn'),
        content: SizedBox(width: double.maxFinite, child: rows.isEmpty ? const Text('Chưa có yêu cầu gia hạn.') :
          ListView(shrinkWrap: true, children: rows.map((r) => ListTile(
            title: Text('${r['days']} ngày · ${const {0: "Chờ duyệt", 1: "Đã duyệt", 2: "Từ chối"}[r['statusCode']] ?? "Chưa xác định"}'),
            subtitle: Text('${r['notes'] ?? ""}\n${r['response'] ?? ""}'))).toList())),
        actions: [TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Đóng'))]));
    } catch (error) { if (mounted) _showMsg(context, error.toString().replaceFirst('Exception: ', ''), false); }
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

  Future<void> _updateInstallation(InstallationModel installation, int status) async {
    final confirm = await _showConfirmDialog(context,
      status == 1 ? 'Xác nhận bắt đầu lắp đặt?' : 'Xác nhận đã lắp đặt xong?');
    if (confirm != true || !mounted || _updatingInstallation) return;
    setState(() => _updatingInstallation = true);
    try {
      await context.read<InstallationProvider>().updateInstallation(installation, status);
      if (mounted) _showMsg(context, 'Đã cập nhật tiến độ lắp đặt.', true);
    } catch (error) {
      if (mounted) _showMsg(context, error.toString().replaceFirst('Exception: ', ''), false);
    } finally {
      if (mounted) setState(() => _updatingInstallation = false);
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
