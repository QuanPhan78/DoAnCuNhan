import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/incident_model.dart';
import '../../models/role_enum.dart';
import '../../providers/auth_provider.dart';
import '../../providers/incident_provider.dart';
import '../../widgets/custom_image_widget.dart';
import '../../widgets/dashboard_widgets.dart'; // StatusBadge, BadgeStatus
import '../../widgets/core/custom_app_bar.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../theme/app_radius.dart';
import '../../theme/app_shadows.dart';

class IncidentDetailScreen extends StatefulWidget {
  final IncidentModel incident;

  const IncidentDetailScreen({super.key, required this.incident});

  @override
  State<IncidentDetailScreen> createState() => _IncidentDetailScreenState();
}

class _IncidentDetailScreenState extends State<IncidentDetailScreen> {
  late IncidentModel incident;
  bool _refreshing = true;
  bool _busy = false;

  @override
  void initState() {
    super.initState();
    incident = widget.incident;
    WidgetsBinding.instance.addPostFrameCallback((_) => _refresh());
  }

  Future<void> _refresh() async {
    if (!mounted || _busy) return;
    setState(() => _refreshing = true);
    try {
      final latest = await context.read<IncidentProvider>().getIncident(incident.id);
      if (mounted) setState(() => incident = latest);
    } catch (error) {
      if (mounted) _message(error.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _refreshing = false);
    }
  }

  void _message(String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  Future<void> _review({bool? accepted}) async {
    final form = GlobalKey<FormState>();
    var feedback = '';
    var rating = incident.rating ?? 5;
    final title = switch (accepted) {
      true => 'Đồng ý nghiệm thu',
      false => 'Từ chối nghiệm thu',
      null => 'Đánh giá dịch vụ',
    };
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialog) => AlertDialog(
        title: Text(title),
        content: Form(
          key: form,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (accepted == null)
                DropdownButtonFormField<int>(
                  initialValue: rating,
                  decoration: const InputDecoration(labelText: 'Số sao'),
                  items: [for (var value = 1; value <= 5; value++)
                    DropdownMenuItem(value: value, child: Text('$value sao'))],
                  onChanged: (value) => rating = value!,
                ),
              TextFormField(
                initialValue: accepted == null ? incident.feedback : null,
                decoration: InputDecoration(labelText: accepted == false ? 'Lý do từ chối' : 'Nhận xét (tùy chọn)'),
                maxLength: 1000,
                maxLines: 2,
                validator: (value) => accepted == false && (value ?? '').trim().isEmpty
                    ? 'Nhập lý do từ chối.' : null,
                onSaved: (value) => feedback = (value ?? '').trim(),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(dialog), child: const Text('Đóng')),
          FilledButton(
            onPressed: () {
              if (!form.currentState!.validate()) return;
              form.currentState!.save();
              Navigator.pop(dialog, true);
            },
            child: const Text('Gửi'),
          ),
        ],
      ),
    );
    if (confirmed != true || !mounted || _busy) return;
    final provider = context.read<IncidentProvider>();
    setState(() => _busy = true);
    try {
      final latest = accepted == null
          ? await provider.rateIncident(incident, rating, feedback)
          : await provider.acceptIncident(incident, accepted, feedback);
      if (!mounted) return;
      setState(() => incident = latest);
      _message(switch (accepted) {
        true => 'Đã xác nhận nghiệm thu.',
        false => 'Đã yêu cầu kỹ thuật viên xử lý lại.',
        null => 'Đã lưu đánh giá.',
      });
    } catch (error) {
      if (mounted) _message(error.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  BadgeStatus _getBadgeStatus(String status) {
    switch (status.toLowerCase()) {
      case 'đã hoàn thành':
      case 'đã nghiệm thu':
        return BadgeStatus.success;
      case 'đang xử lý':
      case 'chờ nghiệm thu':
        return BadgeStatus.processing;
      case 'chờ xử lý':
        return BadgeStatus.warning;
      default:
        return BadgeStatus.neutral;
    }
  }

  @override
  Widget build(BuildContext context) {
    final isCustomer = context.watch<AuthProvider>().currentUser?.role == Role.customer;
    final canReview = isCustomer && !_busy && !_refreshing;
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: CustomAppBar(title: 'Chi tiết sự cố', actions: [
        IconButton(onPressed: _refreshing || _busy ? null : _refresh,
          tooltip: 'Tải lại phiếu', icon: const Icon(Icons.refresh)),
      ]),
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
                    incident.code, 
                    style: AppTextStyles.h1.copyWith(fontSize: 24),
                  ),
                ),
                StatusBadge(
                  text: incident.status,
                  status: _getBadgeStatus(incident.status),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // Thông tin chung
            _buildSectionCard(
              title: 'Thông tin chung',
              icon: Icons.info_outline_rounded,
              content: Column(
                children: [
                  _buildInfoRow('Thiết bị', incident.deviceName ?? incident.deviceId, isHighlight: true),
                  _buildDivider(),
                  _buildInfoRow('Loại sự cố', incident.issueType),
                  _buildDivider(),
                  _buildInfoRow(
                    'Mức độ', 
                    incident.severity, 
                    isError: incident.severity.toLowerCase() == 'nghiêm trọng',
                    isWarning: incident.severity.toLowerCase() == 'trung bình',
                  ),
                  _buildDivider(),
                  _buildInfoRow('Hợp đồng', incident.contractId),
                  _buildDivider(),
                  _buildInfoRow('Thời gian', incident.occurrenceTime),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Người phụ trách
            if (incident.assignedStaff != null && incident.assignedStaff!.isNotEmpty) ...[
              _buildSectionCard(
                title: 'Người phụ trách',
                icon: Icons.person_outline_rounded,
                content: _buildInfoRow('Nhân viên', incident.assignedStaff!),
              ),
              const SizedBox(height: 16),
            ],

            // Mô tả
            _buildSectionCard(
              title: 'Mô tả chi tiết',
              icon: Icons.description_outlined,
              content: Text(
                incident.description, 
                style: AppTextStyles.body.copyWith(height: 1.5),
              ),
            ),
            
            if (incident.result?.isNotEmpty == true) ...[
              const SizedBox(height: 16),
              _buildSectionCard(title: 'Kết quả xử lý', icon: Icons.build_outlined,
                content: Text(incident.result!)),
            ],

            // Hình ảnh đính kèm
            if (incident.attachments.isNotEmpty) ...[
              const SizedBox(height: 16),
              _buildSectionCard(
                title: 'Hình ảnh đính kèm',
                icon: Icons.image_outlined,
                content: Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: incident.attachments.map((att) {
                    return Container(
                      width: 100,
                      height: 100,
                      decoration: BoxDecoration(
                        border: Border.all(color: AppColors.divider),
                        borderRadius: AppRadius.mdRadius,
                      ),
                      child: ClipRRect(
                        borderRadius: AppRadius.mdRadius,
                        child: CustomImageWidget(
                          imageUrl: att.url ?? att.localPath ?? '',
                          fit: BoxFit.cover,
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ),
            ],
            
            if (_busy || _refreshing) ...[
              const SizedBox(height: 16),
              const LinearProgressIndicator(),
            ],
            if (isCustomer && incident.statusCode == 3) ...[
              const SizedBox(height: 16),
              _buildSectionCard(
                title: 'Nghiệm thu',
                icon: Icons.fact_check_outlined,
                content: Wrap(spacing: 8, runSpacing: 8, children: [
                  FilledButton(onPressed: canReview ? () => _review(accepted: true) : null,
                    child: const Text('Đồng ý nghiệm thu')),
                  OutlinedButton(onPressed: canReview ? () => _review(accepted: false) : null,
                    child: const Text('Từ chối nghiệm thu')),
                ]),
              ),
            ],
            if (isCustomer && (incident.rating != null || incident.statusCode == 3 || incident.statusCode == 5)) ...[
              const SizedBox(height: 16),
              _buildSectionCard(
                title: 'Đánh giá dịch vụ',
                icon: Icons.star_outline,
                content: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  if (incident.rating != null) Text('${incident.rating}/5 sao'),
                  if (incident.feedback?.isNotEmpty == true) Text(incident.feedback!),
                  if (incident.rating == null && (incident.statusCode == 3 || incident.statusCode == 5))
                    OutlinedButton(onPressed: canReview ? () => _review() : null,
                      child: const Text('Gửi đánh giá')),
                ]),
              ),
            ],
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

  Widget _buildInfoRow(String label, String value, {bool isHighlight = false, bool isError = false, bool isWarning = false}) {
    Color valColor = AppColors.textPrimary;
    if (isHighlight) valColor = AppColors.primary;
    if (isError) valColor = AppColors.error;
    if (isWarning) valColor = AppColors.warning;

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
                fontWeight: (isHighlight || isError || isWarning) ? FontWeight.bold : FontWeight.w500,
                color: valColor,
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
}
