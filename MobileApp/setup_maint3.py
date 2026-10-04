import os

os.makedirs("lib/screens/maintenance", exist_ok=True)

# 1. List Screen
list_screen = """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/maintenance_provider.dart';
import '../../widgets/maintenance_card.dart';

class MaintenanceListScreen extends StatefulWidget {
  const MaintenanceListScreen({super.key});

  @override
  State<MaintenanceListScreen> createState() => _MaintenanceListScreenState();
}

class _MaintenanceListScreenState extends State<MaintenanceListScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadData();
    });
  }

  void _loadData() {
    final user = context.read<AuthProvider>().currentUser;
    if (user != null) {
      context.read<MaintenanceProvider>().fetchMaintenances(user.id, user.role, user.name);
    }
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<MaintenanceProvider>();

    return Scaffold(
      appBar: AppBar(title: const Text('Bảo trì & Sửa chữa')),
      body: provider.isLoading
          ? const Center(child: CircularProgressIndicator())
          : provider.errorMessage != null
              ? Center(child: Text('Lỗi: ${provider.errorMessage}'))
              : provider.maintenances.isEmpty
                  ? const Center(child: Text('Không có dữ liệu.'))
                  : RefreshIndicator(
                      onRefresh: () async => _loadData(),
                      child: ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: provider.maintenances.length,
                        itemBuilder: (context, index) {
                          final m = provider.maintenances[index];
                          return MaintenanceCard(
                            maintenance: m,
                            onTap: () async {
                              await Navigator.pushNamed(context, '/maintenance_detail', arguments: m);
                              _loadData();
                            },
                          );
                        },
                      ),
                    ),
    );
  }
}
"""
with open("lib/screens/maintenance/maintenance_list_screen.dart", "w", encoding="utf-8") as f: f.write(list_screen)

# 2. Detail Screen
detail_screen = """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/maintenance_model.dart';
import '../../providers/auth_provider.dart';
import '../../models/permission_enum.dart';
import '../../utils/permission_manager.dart';
import '../../widgets/maintenance_timeline.dart';

class MaintenanceDetailScreen extends StatelessWidget {
  final MaintenanceModel maintenance;

  const MaintenanceDetailScreen({super.key, required this.maintenance});

  @override
  Widget build(BuildContext context) {
    final userRole = context.read<AuthProvider>().currentUser?.role;
    final canUpdate = userRole != null && PermissionManager.hasPermission(userRole, AppPermission.viewAssignedMaintenance);

    return Scaffold(
      appBar: AppBar(title: const Text('Chi tiết Bảo trì')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Yêu cầu: ${maintenance.requestCode}', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(color: Colors.blue.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(12)),
              child: Text(maintenance.status ?? 'N/A', style: const TextStyle(color: Colors.blue, fontWeight: FontWeight.w600)),
            ),
            const Divider(height: 32),
            _buildRow('Khách hàng', maintenance.customer ?? 'N/A'),
            _buildRow('Thiết bị', maintenance.deviceId ?? 'N/A'),
            _buildRow('Hợp đồng', maintenance.contractId ?? 'N/A'),
            _buildRow('Nhân viên', maintenance.assignedEmployee?.isEmpty ?? true ? 'Chưa phân công' : maintenance.assignedEmployee!),
            _buildRow('Ngày tạo', maintenance.createdAt ?? 'N/A'),
            if (maintenance.completedAt != null && maintenance.completedAt!.isNotEmpty)
              _buildRow('Hoàn thành', maintenance.completedAt!),
            const Divider(height: 32),
            const Text('Mô tả sự cố', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text(maintenance.description ?? 'N/A', style: const TextStyle(fontSize: 14)),
            if (maintenance.result != null && maintenance.result!.isNotEmpty) ...[
              const Divider(height: 32),
              const Text('Kết quả xử lý', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Text(maintenance.result!, style: const TextStyle(fontSize: 14)),
            ],
            const Divider(height: 32),
            const Text('Tiến trình', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            MaintenanceTimeline(notes: maintenance.notes),
          ],
        ),
      ),
      bottomNavigationBar: canUpdate && maintenance.status != 'Hoàn thành'
          ? SafeArea(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pushNamed(context, '/maintenance_update', arguments: maintenance);
                  },
                  child: const Text('CẬP NHẬT TRẠNG THÁI'),
                ),
              ),
            )
          : null,
    );
  }

  Widget _buildRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(width: 100, child: Text(label, style: const TextStyle(color: Colors.grey))),
          Expanded(child: Text(value, style: const TextStyle(fontWeight: FontWeight.w600))),
        ],
      ),
    );
  }
}
"""
with open("lib/screens/maintenance/maintenance_detail_screen.dart", "w", encoding="utf-8") as f: f.write(detail_screen.replace(r'${', '${'))

# 3. Update Screen
update_screen = """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/maintenance_model.dart';
import '../../providers/auth_provider.dart';
import '../../providers/maintenance_provider.dart';

class MaintenanceUpdateScreen extends StatefulWidget {
  final MaintenanceModel maintenance;
  const MaintenanceUpdateScreen({super.key, required this.maintenance});

  @override
  State<MaintenanceUpdateScreen> createState() => _MaintenanceUpdateScreenState();
}

class _MaintenanceUpdateScreenState extends State<MaintenanceUpdateScreen> {
  final _formKey = GlobalKey<FormState>();
  late String _status;
  final _noteCtrl = TextEditingController();
  final _resultCtrl = TextEditingController();

  final List<String> _statuses = ['Chờ tiếp nhận', 'Đã tiếp nhận', 'Đã phân công', 'Đang xử lý', 'Hoàn thành'];

  @override
  void initState() {
    super.initState();
    _status = widget.maintenance.status ?? 'Chờ tiếp nhận';
    if (!_statuses.contains(_status)) {
      _statuses.add(_status);
    }
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    final user = context.read<AuthProvider>().currentUser;
    if (user == null) return;

    final updated = MaintenanceModel(
      id: widget.maintenance.id,
      requestCode: widget.maintenance.requestCode,
      contractId: widget.maintenance.contractId,
      deviceId: widget.maintenance.deviceId,
      customer: widget.maintenance.customer,
      description: widget.maintenance.description,
      status: _status,
      assignedEmployee: user.name,
      createdAt: widget.maintenance.createdAt,
      completedAt: _status == 'Hoàn thành' ? DateTime.now().toString().substring(0, 16) : widget.maintenance.completedAt,
      result: _status == 'Hoàn thành' ? _resultCtrl.text : widget.maintenance.result,
      notes: List.from(widget.maintenance.notes),
    );

    if (_noteCtrl.text.isNotEmpty || _status == 'Hoàn thành') {
      updated.notes.add(MaintenanceNote(
        time: DateTime.now().toString().substring(0, 16),
        content: _noteCtrl.text.isNotEmpty ? _noteCtrl.text : 'Đã hoàn thành bảo trì',
        author: user.name,
      ));
    }

    final success = await context.read<MaintenanceProvider>().updateMaintenance(updated);
    if (!mounted) return;
    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Cập nhật thành công'), backgroundColor: Colors.green));
      // Pop twice to go back to list
      Navigator.pop(context);
      Navigator.pop(context); 
    } else {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Lỗi cập nhật'), backgroundColor: Colors.red));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Cập nhật Bảo trì')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            DropdownButtonFormField<String>(
              decoration: const InputDecoration(labelText: 'Trạng thái', border: OutlineInputBorder()),
              value: _status,
              items: _statuses.map((s) => DropdownMenuItem(value: s, child: Text(s))).toList(),
              onChanged: (v) => setState(() => _status = v!),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _noteCtrl,
              maxLines: 3,
              decoration: const InputDecoration(labelText: 'Ghi chú / Tiến độ', border: OutlineInputBorder()),
            ),
            if (_status == 'Hoàn thành') ...[
              const SizedBox(height: 16),
              TextFormField(
                controller: _resultCtrl,
                maxLines: 2,
                decoration: const InputDecoration(labelText: 'Kết quả xử lý', border: OutlineInputBorder()),
                validator: (v) => v!.isEmpty ? 'Vui lòng nhập kết quả' : null,
              ),
            ],
            const SizedBox(height: 32),
            ElevatedButton(
              style: ElevatedButton.styleFrom(minimumSize: const Size(double.infinity, 50)),
              onPressed: _submit,
              child: const Text('LƯU CẬP NHẬT'),
            )
          ],
        ),
      ),
    );
  }
}
"""
with open("lib/screens/maintenance/maintenance_update_screen.dart", "w", encoding="utf-8") as f: f.write(update_screen)

print("Maintenance screens created.")