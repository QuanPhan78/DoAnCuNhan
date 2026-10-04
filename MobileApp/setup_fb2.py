import os

def insert_provider(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "FeedbackProvider" not in content:
        import_str = "import 'package:quan_ly_cho_thue_thiet_bi/providers/feedback_provider.dart';\nimport 'package:quan_ly_cho_thue_thiet_bi/repositories/feedback_repository.dart';\nimport 'package:quan_ly_cho_thue_thiet_bi/datasources/feedback/local_feedback_datasource.dart';\n"
        if "package:quan_ly_cho_thue_thiet_bi" not in content and "main.dart" in file_path:
            import_str = "import 'providers/feedback_provider.dart';\nimport 'repositories/feedback_repository.dart';\nimport 'datasources/feedback/local_feedback_datasource.dart';\n"
        content = import_str + content
        provider_str = """
          ChangeNotifierProvider(
            create: (_) => FeedbackProvider(
              FeedbackRepository(LocalFeedbackDataSource()),
            ),
          ),"""
        content = content.replace("providers: [", "providers: [" + provider_str)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

insert_provider("lib/main.dart")
insert_provider("test/widget_test.dart")

os.makedirs("lib/screens/feedbacks", exist_ok=True)

list_code = """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/feedback_provider.dart';

class FeedbackListScreen extends StatefulWidget {
  const FeedbackListScreen({super.key});

  @override
  State<FeedbackListScreen> createState() => _FeedbackListScreenState();
}

class _FeedbackListScreenState extends State<FeedbackListScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<FeedbackProvider>().fetchFeedbacks();
    });
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<FeedbackProvider>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Phản hồi của tôi'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () async {
              final result = await Navigator.pushNamed(context, '/create_feedback');
              if (result == true && context.mounted) {
                context.read<FeedbackProvider>().fetchFeedbacks();
              }
            },
          )
        ],
      ),
      body: provider.isLoading
          ? const Center(child: CircularProgressIndicator())
          : provider.errorMessage != null
              ? Center(child: Text('Lỗi: ${provider.errorMessage}'))
              : provider.feedbacks.isEmpty
                  ? const Center(child: Text('Chưa có phản hồi nào.'))
                  : RefreshIndicator(
                      onRefresh: () => context.read<FeedbackProvider>().fetchFeedbacks(),
                      child: ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: provider.feedbacks.length,
                        itemBuilder: (context, index) {
                          final fb = provider.feedbacks[index];
                          return Card(
                            margin: const EdgeInsets.only(bottom: 12),
                            child: ListTile(
                              title: Text(fb.feedbackCode ?? 'N/A', style: const TextStyle(fontWeight: FontWeight.bold)),
                              subtitle: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const SizedBox(height: 4),
                                  Text(fb.content, maxLines: 2, overflow: TextOverflow.ellipsis),
                                  const SizedBox(height: 4),
                                  Text(fb.createdAt ?? '', style: const TextStyle(fontSize: 12, color: Colors.grey)),
                                ],
                              ),
                              trailing: _buildStatus(fb.status),
                              onTap: () {
                                Navigator.pushNamed(context, '/feedback_detail', arguments: fb);
                              },
                            ),
                          );
                        },
                      ),
                    ),
    );
  }

  Widget _buildStatus(String? status) {
    if (status == null) return const SizedBox();
    Color color = Colors.grey;
    if (status == 'Đã phản hồi') color = Colors.green;
    if (status == 'Đã ghi nhận') color = Colors.blue;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(color: color.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(8)),
      child: Text(status, style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.bold)),
    );
  }
}
"""
with open("lib/screens/feedbacks/feedback_list_screen.dart", "w", encoding="utf-8") as f: f.write(list_code.replace(r'${', '${'))

detail_code = """import 'package:flutter/material.dart';
import '../../models/feedback_model.dart';

class FeedbackDetailScreen extends StatelessWidget {
  final FeedbackModel feedback;

  const FeedbackDetailScreen({super.key, required this.feedback});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Chi tiết Phản hồi')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(feedback.feedbackCode ?? 'N/A', style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text(feedback.createdAt ?? '', style: const TextStyle(color: Colors.grey)),
            const Divider(height: 32),
            if (feedback.contractId != null && feedback.contractId!.isNotEmpty)
              _buildRow('Hợp đồng', feedback.contractId!),
            if (feedback.maintenanceId != null && feedback.maintenanceId!.isNotEmpty)
              _buildRow('Bảo trì', feedback.maintenanceId!),
            if (feedback.rating != null)
              _buildRow('Đánh giá', '${feedback.rating} Sao', color: Colors.orange),
            const Divider(height: 32),
            const Text('Nội dung:', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text(feedback.content, style: const TextStyle(fontSize: 16, height: 1.5)),
            if (feedback.response != null && feedback.response!.isNotEmpty) ...[
              const Divider(height: 32),
              const Text('Phản hồi từ doanh nghiệp:', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.blue)),
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: Colors.blue.withValues(alpha: 0.05), borderRadius: BorderRadius.circular(8), border: Border.all(color: Colors.blue.shade100)),
                child: Text(feedback.response!, style: const TextStyle(fontSize: 16, height: 1.5)),
              )
            ]
          ],
        ),
      ),
    );
  }

  Widget _buildRow(String label, String value, {Color? color}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(width: 100, child: Text(label, style: const TextStyle(color: Colors.grey))),
          Expanded(child: Text(value, style: TextStyle(fontWeight: FontWeight.w600, color: color))),
        ],
      ),
    );
  }
}
"""
with open("lib/screens/feedbacks/feedback_detail_screen.dart", "w", encoding="utf-8") as f: f.write(detail_code.replace(r'${', '${'))

create_code = """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../models/feedback_model.dart';
import '../../providers/feedback_provider.dart';

class CreateFeedbackScreen extends StatefulWidget {
  const CreateFeedbackScreen({super.key});

  @override
  State<CreateFeedbackScreen> createState() => _CreateFeedbackScreenState();
}

class _CreateFeedbackScreenState extends State<CreateFeedbackScreen> {
  final _formKey = GlobalKey<FormState>();
  String _selectedType = 'Chung';
  final _refCtrl = TextEditingController();
  final _contentCtrl = TextEditingController();
  int _rating = 5;

  final List<String> _types = ['Chung', 'Hợp đồng', 'Thiết bị', 'Lắp đặt', 'Bảo trì', 'Sửa chữa', 'Chất lượng phục vụ'];

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    
    final fb = FeedbackModel(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      feedbackCode: 'FB-2026-${DateTime.now().millisecondsSinceEpoch.toString().substring(8)}',
      contractId: (_selectedType == 'Hợp đồng') ? _refCtrl.text : null,
      maintenanceId: (_selectedType == 'Bảo trì' || _selectedType == 'Sửa chữa') ? _refCtrl.text : null,
      content: _contentCtrl.text,
      rating: _rating,
      status: 'Mới tạo',
      createdAt: DateTime.now().toString().substring(0, 16),
    );

    final success = await context.read<FeedbackProvider>().createFeedback(fb);
    if (!mounted) return;

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Đã gửi phản hồi'), backgroundColor: Colors.green));
      Navigator.pop(context, true);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Lỗi khi gửi phản hồi'), backgroundColor: Colors.red));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Gửi Phản hồi')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            DropdownButtonFormField<String>(
              decoration: const InputDecoration(labelText: 'Chủ đề', border: OutlineInputBorder()),
              value: _selectedType,
              items: _types.map((t) => DropdownMenuItem(value: t, child: Text(t))).toList(),
              onChanged: (v) => setState(() {
                _selectedType = v!;
                _refCtrl.clear();
              }),
            ),
            if (_selectedType == 'Hợp đồng' || _selectedType == 'Bảo trì' || _selectedType == 'Sửa chữa') ...[
              const SizedBox(height: 16),
              TextFormField(
                controller: _refCtrl,
                decoration: InputDecoration(
                  labelText: 'Mã ${_selectedType} liên quan', 
                  border: const OutlineInputBorder()
                ),
              ),
            ],
            const SizedBox(height: 16),
            TextFormField(
              controller: _contentCtrl,
              maxLines: 4,
              decoration: const InputDecoration(labelText: 'Nội dung phản hồi', border: OutlineInputBorder()),
              validator: (v) => v!.isEmpty ? 'Vui lòng nhập nội dung' : null,
            ),
            const SizedBox(height: 16),
            const Text('Đánh giá:', style: TextStyle(fontWeight: FontWeight.bold)),
            Row(
              children: List.generate(5, (index) {
                return IconButton(
                  icon: Icon(
                    index < _rating ? Icons.star : Icons.star_border,
                    color: Colors.orange,
                    size: 32,
                  ),
                  onPressed: () => setState(() => _rating = index + 1),
                );
              }),
            ),
            const SizedBox(height: 32),
            ElevatedButton(
              style: ElevatedButton.styleFrom(minimumSize: const Size(double.infinity, 50)),
              onPressed: _submit,
              child: const Text('GỬI PHẢN HỒI'),
            )
          ],
        ),
      ),
    );
  }
}
"""
with open("lib/screens/feedbacks/create_feedback_screen.dart", "w", encoding="utf-8") as f: f.write(create_code.replace(r'${', '${'))

router_path = "lib/routes/app_router.dart"
with open(router_path, "r", encoding="utf-8") as f:
    content = f.read()

if "/feedback_list" not in content:
    imports = """import '../screens/feedbacks/feedback_list_screen.dart';
import '../screens/feedbacks/feedback_detail_screen.dart';
import '../screens/feedbacks/create_feedback_screen.dart';
import '../models/feedback_model.dart';
"""
    content = content.replace("import '../models/maintenance_model.dart';", "import '../models/maintenance_model.dart';\n" + imports)
    
    routes = """
          case '/feedbacks':
            return const FeedbackListScreen();
          case '/create_feedback':
            return const CreateFeedbackScreen();
          case '/feedback_detail':
            final fb = settings.arguments as FeedbackModel;
            return FeedbackDetailScreen(feedback: fb);
"""
    content = content.replace("case '/device_detail':", routes + "          case '/device_detail':")
    with open(router_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Feedback screens and routes created.")