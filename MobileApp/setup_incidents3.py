import os

os.makedirs("lib/screens/incidents", exist_ok=True)

# 1. IncidentListScreen (We will replace RequestsScreen to point to this, or just use this directly)
list_code = """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/contract_provider.dart';
import '../../providers/incident_provider.dart';
import '../../models/permission_enum.dart';
import '../../utils/permission_manager.dart';

class IncidentListScreen extends StatefulWidget {
  const IncidentListScreen({super.key});

  @override
  State<IncidentListScreen> createState() => _IncidentListScreenState();
}

class _IncidentListScreenState extends State<IncidentListScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadData();
    });
  }

  void _loadData() {
    final auth = context.read<AuthProvider>();
    if (auth.currentUser != null) {
      context.read<IncidentProvider>().fetchIncidents(
        auth.currentUser!.id, 
        auth.currentUser!.role, 
        context.read<ContractProvider>()
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<IncidentProvider>();
    final userRole = context.read<AuthProvider>().currentUser?.role;
    final canReport = userRole != null && PermissionManager.hasPermission(userRole, AppPermission.reportIssue);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Yêu cầu & Sự cố'),
        actions: [
          if (canReport)
            IconButton(
              icon: const Icon(Icons.add),
              onPressed: () async {
                final result = await Navigator.pushNamed(context, '/create_incident');
                if (result == true) {
                  _loadData();
                }
              },
            )
        ],
      ),
      body: provider.isLoading
          ? const Center(child: CircularProgressIndicator())
          : provider.errorMessage != null
              ? Center(child: Text('Lỗi: ${provider.errorMessage}'))
              : provider.incidents.isEmpty
                  ? const Center(child: Text('Chưa có yêu cầu nào.'))
                  : RefreshIndicator(
                      onRefresh: () async => _loadData(),
                      child: ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: provider.incidents.length,
                        itemBuilder: (context, index) {
                          final inc = provider.incidents[index];
                          return Card(
                            margin: const EdgeInsets.only(bottom: 12),
                            child: ListTile(
                              title: Text('${inc.code} - ${inc.issueType}', style: const TextStyle(fontWeight: FontWeight.bold)),
                              subtitle: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text('HĐ: ${inc.contractId} - TB: ${inc.deviceId}'),
                                  const SizedBox(height: 4),
                                  Text(inc.createdAt, style: const TextStyle(fontSize: 12, color: Colors.grey)),
                                ],
                              ),
                              trailing: _buildStatusBadge(inc.status),
                              onTap: () {
                                Navigator.pushNamed(context, '/incident_detail', arguments: inc);
                              },
                            ),
                          );
                        },
                      ),
                    ),
    );
  }

  Widget _buildStatusBadge(String status) {
    Color color = Colors.grey;
    if (status == 'Chờ xử lý') color = Colors.orange;
    if (status == 'Đang xử lý') color = Colors.blue;
    if (status == 'Đã hoàn thành') color = Colors.green;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(color: color.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(8)),
      child: Text(status, style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.bold)),
    );
  }
}
"""
with open("lib/screens/incidents/incident_list_screen.dart", "w", encoding="utf-8") as f: f.write(list_code.replace(r'${', '${'))


# 2. IncidentDetailScreen
detail_code = """import 'package:flutter/material.dart';
import '../../models/incident_model.dart';
import '../../widgets/custom_image_widget.dart';

class IncidentDetailScreen extends StatelessWidget {
  final IncidentModel incident;

  const IncidentDetailScreen({super.key, required this.incident});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Chi tiết Yêu cầu')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(incident.code, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            _buildStatusBadge(incident.status),
            const Divider(height: 32),
            _buildRow('Loại sự cố', incident.issueType),
            _buildRow('Mức độ', incident.severity, color: _getSeverityColor(incident.severity)),
            _buildRow('Hợp đồng', incident.contractId),
            _buildRow('Mã Thiết bị', incident.deviceId),
            _buildRow('Thời gian bị', incident.occurrenceTime),
            if (incident.assignedStaff != null && incident.assignedStaff!.isNotEmpty)
              _buildRow('Nhân viên', incident.assignedStaff!),
            const Divider(height: 32),
            const Text('Mô tả', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text(incident.description, style: const TextStyle(fontSize: 16, height: 1.5)),
            if (incident.attachments.isNotEmpty) ...[
              const Divider(height: 32),
              const Text('Hình ảnh đính kèm', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: incident.attachments.map((att) {
                  return Container(
                    width: 100,
                    height: 100,
                    decoration: BoxDecoration(border: Border.all(color: Colors.grey.shade300)),
                    child: CustomImageWidget(
                      imageUrl: att.url ?? att.localPath ?? '',
                    ),
                  );
                }).toList(),
              )
            ]
          ],
        ),
      ),
    );
  }

  Widget _buildRow(String label, String value, {Color? color}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(width: 100, child: Text(label, style: const TextStyle(color: Colors.grey))),
          Expanded(child: Text(value, style: TextStyle(fontWeight: FontWeight.w600, color: color, fontSize: 16))),
        ],
      ),
    );
  }

  Color _getSeverityColor(String sev) {
    if (sev == 'Nghiêm trọng') return Colors.red;
    if (sev == 'Trung bình') return Colors.orange;
    return Colors.blue;
  }

  Widget _buildStatusBadge(String status) {
    Color color = Colors.grey;
    if (status == 'Chờ xử lý') color = Colors.orange;
    if (status == 'Đang xử lý') color = Colors.blue;
    if (status == 'Đã hoàn thành') color = Colors.green;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color),
      ),
      child: Text(status, style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.w600)),
    );
  }
}
"""
with open("lib/screens/incidents/incident_detail_screen.dart", "w", encoding="utf-8") as f: f.write(detail_code.replace(r'${', '${'))


# 3. CreateIncidentScreen
create_code = """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/incident_model.dart';
import '../../models/attachment_model.dart';
import '../../models/contract_model.dart';
import '../../providers/auth_provider.dart';
import '../../providers/contract_provider.dart';
import '../../providers/incident_provider.dart';

class CreateIncidentScreen extends StatefulWidget {
  const CreateIncidentScreen({super.key});

  @override
  State<CreateIncidentScreen> createState() => _CreateIncidentScreenState();
}

class _CreateIncidentScreenState extends State<CreateIncidentScreen> {
  final _formKey = GlobalKey<FormState>();
  
  String? _selectedContractId;
  String? _selectedDeviceId;
  String _selectedIssueType = 'Không lên nguồn';
  String _selectedSeverity = 'Trung bình';
  final _descCtrl = TextEditingController();
  final _timeCtrl = TextEditingController();
  
  final List<String> _issueTypes = [
    'Không lên nguồn', 'Lỗi màn hình', 'Lỗi bàn phím', 'Chuột lỗi', 'Mất kết nối', 'Lỗi phần mềm', 'Khác'
  ];
  final List<String> _severities = ['Nhẹ', 'Trung bình', 'Nghiêm trọng'];
  final List<AttachmentModel> _mockAttachments = [];

  List<ContractModel> _myContracts = [];
  List<String> _contractDevices = [];

  @override
  void initState() {
    super.initState();
    _timeCtrl.text = DateTime.now().toString().substring(0, 16);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final userId = context.read<AuthProvider>().currentUser?.id;
      final allContracts = context.read<ContractProvider>().contracts;
      setState(() {
        _myContracts = allContracts.where((c) => c.customerId == userId && c.status != 'Đã thanh lý').toList();
      });
    });
  }

  void _onContractChanged(String? val) {
    setState(() {
      _selectedContractId = val;
      _selectedDeviceId = null;
      if (val != null) {
        final c = _myContracts.firstWhere((c) => c.id == val);
        _contractDevices = c.deviceIds ?? [];
      } else {
        _contractDevices = [];
      }
    });
  }

  void _addMockImage() {
    setState(() {
      _mockAttachments.add(AttachmentModel(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        localPath: 'assets/images/placeholder.png',
        type: 'image'
      ));
    });
  }

  void _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedContractId == null || _selectedDeviceId == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Vui lòng chọn Hợp đồng và Thiết bị')));
      return;
    }

    final inc = IncidentModel(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      code: 'INC-2026-${DateTime.now().millisecondsSinceEpoch.toString().substring(8)}',
      contractId: _selectedContractId!,
      deviceId: _selectedDeviceId!,
      issueType: _selectedIssueType,
      description: _descCtrl.text,
      severity: _selectedSeverity,
      occurrenceTime: _timeCtrl.text,
      status: 'Chờ xử lý',
      createdAt: DateTime.now().toString().substring(0, 16),
      attachments: _mockAttachments,
    );

    final success = await context.read<IncidentProvider>().createIncident(inc);
    if (!mounted) return;
    
    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Đã gửi yêu cầu'), backgroundColor: Colors.green));
      Navigator.pop(context, true);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Lỗi khi gửi yêu cầu'), backgroundColor: Colors.red));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Báo sự cố')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            DropdownButtonFormField<String>(
              decoration: const InputDecoration(labelText: 'Hợp đồng', border: OutlineInputBorder()),
              value: _selectedContractId,
              items: _myContracts.map((c) => DropdownMenuItem(value: c.id, child: Text(c.contractCode ?? c.id))).toList(),
              onChanged: _onContractChanged,
              validator: (v) => v == null ? 'Bắt buộc' : null,
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              decoration: const InputDecoration(labelText: 'Thiết bị', border: OutlineInputBorder()),
              value: _selectedDeviceId,
              items: _contractDevices.map((d) => DropdownMenuItem(value: d, child: Text('Mã TB: $d'))).toList(),
              onChanged: (v) => setState(() => _selectedDeviceId = v),
              validator: (v) => v == null ? 'Bắt buộc' : null,
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              decoration: const InputDecoration(labelText: 'Loại sự cố', border: OutlineInputBorder()),
              value: _selectedIssueType,
              items: _issueTypes.map((t) => DropdownMenuItem(value: t, child: Text(t))).toList(),
              onChanged: (v) => setState(() => _selectedIssueType = v!),
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              decoration: const InputDecoration(labelText: 'Mức độ', border: OutlineInputBorder()),
              value: _selectedSeverity,
              items: _severities.map((t) => DropdownMenuItem(value: t, child: Text(t))).toList(),
              onChanged: (v) => setState(() => _selectedSeverity = v!),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _timeCtrl,
              decoration: const InputDecoration(labelText: 'Thời gian phát sinh', border: OutlineInputBorder()),
              validator: (v) => v!.isEmpty ? 'Bắt buộc' : null,
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _descCtrl,
              maxLines: 3,
              decoration: const InputDecoration(labelText: 'Mô tả chi tiết', border: OutlineInputBorder()),
              validator: (v) => v!.isEmpty ? 'Bắt buộc' : null,
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Hình ảnh đính kèm', style: TextStyle(fontWeight: FontWeight.bold)),
                TextButton.icon(onPressed: _addMockImage, icon: const Icon(Icons.add_a_photo), label: const Text('Thêm ảnh (Mock)')),
              ],
            ),
            if (_mockAttachments.isNotEmpty)
              Wrap(
                spacing: 8,
                children: _mockAttachments.map((a) => Container(
                  width: 60, height: 60,
                  decoration: BoxDecoration(border: Border.all(color: Colors.grey)),
                  child: const Icon(Icons.image),
                )).toList(),
              ),
            const SizedBox(height: 32),
            ElevatedButton(
              style: ElevatedButton.styleFrom(minimumSize: const Size(double.infinity, 50)),
              onPressed: _submit,
              child: const Text('GỬI YÊU CẦU', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            )
          ],
        ),
      ),
    );
  }
}
"""
with open("lib/screens/incidents/create_incident_screen.dart", "w", encoding="utf-8") as f: f.write(create_code.replace(r'${', '${'))

print("Incident UI Setup Complete")