import 'package:flutter/material.dart';
import 'package:printing/printing.dart';
import 'package:provider/provider.dart';
import '../../models/contract_model.dart';
import '../../providers/auth_provider.dart';
import '../../providers/contract_provider.dart';
import '../../services/contract_pdf_generator.dart';
import '../../theme/app_colors.dart';
import '../../theme/app_text_styles.dart';
import '../../widgets/core/custom_app_bar.dart';
import '../../widgets/core/custom_button.dart';

class ContractPdfViewerScreen extends StatefulWidget {
  final ContractModel contract;

  const ContractPdfViewerScreen({super.key, required this.contract});

  @override
  State<ContractPdfViewerScreen> createState() => _ContractPdfViewerScreenState();
}

class _ContractPdfViewerScreenState extends State<ContractPdfViewerScreen> {
  ContractModel? _loadedContract;
  bool _isLoading = true;
  String? _errorMessage;
  bool _isSecurityError = false;

  @override
  void initState() {
    super.initState();
    _checkPermissionAndLoad();
  }

  Future<void> _checkPermissionAndLoad() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _isSecurityError = false;
    });

    final authProvider = context.read<AuthProvider>();
    final user = authProvider.currentUser;

    if (user == null) {
      setState(() {
        _isLoading = false;
        _errorMessage = 'Vui lòng đăng nhập để xem hợp đồng.';
        _isSecurityError = true;
      });
      return;
    }

    try {
      final contractProvider = context.read<ContractProvider>();
      final contract = await contractProvider.getContract(
        widget.contract.id,
        user.id,
        user.role,
      );

      if (mounted) {
        setState(() {
          _loadedContract = contract;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        final errorText = e.toString().replaceFirst('Exception: ', '');
        final is403 = errorText.contains('BẢO MẬT') || errorText.contains('403');
        setState(() {
          _isLoading = false;
          _errorMessage = errorText;
          _isSecurityError = is403;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final title = 'Hợp đồng ${widget.contract.contractCode ?? widget.contract.id}';

    return Scaffold(
      appBar: CustomAppBar(
        title: title,
      ),
      backgroundColor: AppColors.background,
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const CircularProgressIndicator(),
            const SizedBox(height: 16),
            Text(
              'Đang tải hợp đồng...',
              style: AppTextStyles.bodySecondary.copyWith(fontSize: 14),
            ),
          ],
        ),
      );
    }

    if (_errorMessage != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(28.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: (_isSecurityError ? AppColors.warning : AppColors.error).withValues(alpha: 0.12),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  _isSecurityError ? Icons.lock_person_rounded : Icons.error_outline_rounded,
                  size: 64,
                  color: _isSecurityError ? AppColors.warning : AppColors.error,
                ),
              ),
              const SizedBox(height: 20),
              Text(
                _isSecurityError ? 'BẢO MẬT HỢP ĐỒNG' : 'Không thể mở hợp đồng',
                style: AppTextStyles.h2.copyWith(
                  color: _isSecurityError ? AppColors.warning : AppColors.error,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                _errorMessage!,
                textAlign: TextAlign.center,
                style: AppTextStyles.body.copyWith(
                  color: AppColors.textPrimary,
                  fontSize: 15,
                ),
              ),
              const SizedBox(height: 28),
              CustomButton(
                text: 'Quay lại',
                onPressed: () => Navigator.pop(context),
                type: ButtonType.primary,
              ),
            ],
          ),
        ),
      );
    }

    final contract = _loadedContract;
    if (contract == null) return const Center(child: Text('Không tải được hợp đồng.'));

    return PdfPreview(
      build: (format) => ContractPdfGenerator.generateContractPdf(contract),
      canChangeOrientation: false,
      canChangePageFormat: false,
      canDebug: false,
      pdfFileName: '${contract.contractCode ?? "HopDong"}.pdf',
      previewPageMargin: const EdgeInsets.symmetric(horizontal: 6, vertical: 10),
      padding: EdgeInsets.zero,
      loadingWidget: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 12),
            Text('Đang kết xuất văn bản PDF...'),
          ],
        ),
      ),
    );
  }
}
