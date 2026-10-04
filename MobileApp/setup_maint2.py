import os

def insert_provider(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "MaintenanceProvider" not in content:
        import_str = "import 'package:quan_ly_cho_thue_thiet_bi/providers/maintenance_provider.dart';\nimport 'package:quan_ly_cho_thue_thiet_bi/repositories/maintenance_repository.dart';\nimport 'package:quan_ly_cho_thue_thiet_bi/datasources/maintenance/local_maintenance_datasource.dart';\n"
        if "package:quan_ly_cho_thue_thiet_bi" not in content and "main.dart" in file_path:
            import_str = "import 'providers/maintenance_provider.dart';\nimport 'repositories/maintenance_repository.dart';\nimport 'datasources/maintenance/local_maintenance_datasource.dart';\n"
        content = import_str + content
        provider_str = """
          ChangeNotifierProvider(
            create: (_) => MaintenanceProvider(
              MaintenanceRepository(LocalMaintenanceDataSource()),
            ),
          ),"""
        content = content.replace("providers: [", "providers: [" + provider_str)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

insert_provider("lib/main.dart")
insert_provider("test/widget_test.dart")

# Create Widgets
os.makedirs("lib/widgets", exist_ok=True)
card_widget = """import 'package:flutter/material.dart';
import '../models/maintenance_model.dart';

class MaintenanceCard extends StatelessWidget {
  final MaintenanceModel maintenance;
  final VoidCallback onTap;

  const MaintenanceCard({super.key, required this.maintenance, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        onTap: onTap,
        title: Text('${maintenance.requestCode ?? 'N/A'} - ${maintenance.status ?? 'N/A'}', style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text('KH: ${maintenance.customer ?? 'N/A'}'),
            Text('TB: ${maintenance.deviceId ?? 'N/A'} - HĐ: ${maintenance.contractId ?? 'N/A'}'),
          ],
        ),
        trailing: const Icon(Icons.arrow_forward_ios, size: 16),
      ),
    );
  }
}
"""
with open("lib/widgets/maintenance_card.dart", "w", encoding="utf-8") as f: f.write(card_widget)

timeline_widget = """import 'package:flutter/material.dart';
import '../models/maintenance_model.dart';

class MaintenanceTimeline extends StatelessWidget {
  final List<MaintenanceNote> notes;
  const MaintenanceTimeline({super.key, required this.notes});

  @override
  Widget build(BuildContext context) {
    if (notes.isEmpty) return const Text('Chưa có lịch sử cập nhật.');
    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: notes.length,
      itemBuilder: (context, index) {
        final note = notes[index];
        return Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Column(
                children: [
                  Container(
                    width: 12, height: 12,
                    decoration: const BoxDecoration(color: Colors.blue, shape: BoxShape.circle),
                  ),
                  if (index != notes.length - 1)
                    Container(width: 2, height: 50, color: Colors.blue.withValues(alpha: 0.3)),
                ],
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(note.time, style: const TextStyle(fontSize: 12, color: Colors.grey)),
                    const SizedBox(height: 4),
                    Text(note.content, style: const TextStyle(fontSize: 14)),
                    const SizedBox(height: 4),
                    Text('Bởi: ${note.author}', style: const TextStyle(fontSize: 12, fontStyle: FontStyle.italic)),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
"""
with open("lib/widgets/maintenance_timeline.dart", "w", encoding="utf-8") as f: f.write(timeline_widget)

print("Injected Providers and created Widgets")