import os

os.makedirs("lib/screens/search", exist_ok=True)
search_ui = """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/auth_provider.dart';
import '../../providers/search_provider.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<SearchProvider>().clearSearch();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _onChanged(String query) {
    final user = context.read<AuthProvider>().currentUser;
    context.read<SearchProvider>().onSearchChanged(query, user?.id, user?.role);
  }

  void _onFilterChanged(String filter) {
    final user = context.read<AuthProvider>().currentUser;
    context.read<SearchProvider>().setFilter(filter, user?.id, user?.role);
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<SearchProvider>();

    return Scaffold(
      appBar: AppBar(
        title: TextField(
          controller: _searchController,
          autofocus: true,
          decoration: InputDecoration(
            hintText: 'Tìm kiếm...',
            border: InputBorder.none,
            suffixIcon: _searchController.text.isNotEmpty
                ? IconButton(
                    icon: const Icon(Icons.clear),
                    onPressed: () {
                      _searchController.clear();
                      _onChanged('');
                    },
                  )
                : null,
          ),
          onChanged: _onChanged,
        ),
      ),
      body: Column(
        children: [
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              children: [
                _buildChip('Tất cả', 'all', provider),
                const SizedBox(width: 8),
                _buildChip('Thiết bị', 'device', provider),
                const SizedBox(width: 8),
                _buildChip('Hợp đồng', 'contract', provider),
                const SizedBox(width: 8),
                _buildChip('Sự cố', 'incident', provider),
                const SizedBox(width: 8),
                _buildChip('Bảo trì', 'maintenance', provider),
              ],
            ),
          ),
          const Divider(height: 1),
          Expanded(
            child: _buildResults(provider),
          ),
        ],
      ),
    );
  }

  Widget _buildChip(String label, String value, SearchProvider provider) {
    return ChoiceChip(
      label: Text(label),
      selected: provider.currentFilter == value,
      onSelected: (selected) {
        if (selected) _onFilterChanged(value);
      },
    );
  }

  Widget _buildResults(SearchProvider provider) {
    if (provider.isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (provider.errorMessage != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, color: Colors.red, size: 48),
            const SizedBox(height: 16),
            Text('Lỗi: ${provider.errorMessage}'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () {
                final user = context.read<AuthProvider>().currentUser;
                provider.search(provider.currentQuery, userId: user?.id, role: user?.role);
              },
              child: const Text('Thử lại'),
            )
          ],
        ),
      );
    }

    if (provider.currentQuery.trim().isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.search, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text('Nhập từ khóa để tìm kiếm', style: TextStyle(color: Colors.grey, fontSize: 16)),
          ],
        ),
      );
    }

    if (provider.results.isEmpty) {
      return const Center(
        child: Text('Không tìm thấy kết quả phù hợp.', style: TextStyle(color: Colors.grey, fontSize: 16)),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: provider.results.length,
      itemBuilder: (context, index) {
        final result = provider.results[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: ListTile(
            leading: _getIconForType(result.type),
            title: Text(result.title, style: const TextStyle(fontWeight: FontWeight.bold)),
            subtitle: Text(result.subtitle),
            trailing: _buildStatus(result.status),
            onTap: () {
              // Navigate safely
              switch (result.type) {
                case 'device':
                  Navigator.pushNamed(context, '/device_detail', arguments: result.originalData);
                  break;
                case 'contract':
                  Navigator.pushNamed(context, '/contract_detail', arguments: result.originalData);
                  break;
                case 'incident':
                  Navigator.pushNamed(context, '/incident_detail', arguments: result.originalData);
                  break;
                case 'maintenance':
                  Navigator.pushNamed(context, '/maintenance_detail', arguments: result.originalData);
                  break;
              }
            },
          ),
        );
      },
    );
  }

  Widget _getIconForType(String type) {
    switch (type) {
      case 'device': return const Icon(Icons.devices, color: Colors.blue);
      case 'contract': return const Icon(Icons.description, color: Colors.purple);
      case 'incident': return const Icon(Icons.warning, color: Colors.orange);
      case 'maintenance': return const Icon(Icons.build, color: Colors.green);
      default: return const Icon(Icons.insert_drive_file);
    }
  }

  Widget _buildStatus(String? status) {
    if (status == null || status.isEmpty) return const SizedBox();
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(color: Colors.grey.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(8)),
      child: Text(status, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
    );
  }
}
"""
with open("lib/screens/search/search_screen.dart", "w", encoding="utf-8") as f: f.write(search_ui.replace(r'${', '${'))

router_path = "lib/routes/app_router.dart"
with open(router_path, "r", encoding="utf-8") as f:
    content = f.read()

if "/search" not in content:
    content = content.replace("import '../screens/feedbacks/create_feedback_screen.dart';", "import '../screens/feedbacks/create_feedback_screen.dart';\nimport '../screens/search/search_screen.dart';")
    routes = """
          case '/search':
            return const SearchScreen();
"""
    content = content.replace("case '/device_detail':", routes + "          case '/device_detail':")
    with open(router_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Search UI and routing created.")