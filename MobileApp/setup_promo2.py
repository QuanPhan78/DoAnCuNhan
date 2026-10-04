import os

os.makedirs("lib/screens/promotions", exist_ok=True)

# PromotionListScreen
list_screen = """import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/promotion_provider.dart';
import '../../widgets/custom_image_widget.dart';

class PromotionListScreen extends StatefulWidget {
  const PromotionListScreen({super.key});

  @override
  State<PromotionListScreen> createState() => _PromotionListScreenState();
}

class _PromotionListScreenState extends State<PromotionListScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<PromotionProvider>().fetchPromotions();
    });
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<PromotionProvider>();

    return Scaffold(
      appBar: AppBar(title: const Text('Khuyến Mãi')),
      body: provider.isLoading
          ? const Center(child: CircularProgressIndicator())
          : provider.errorMessage != null
              ? Center(child: Text('Lỗi: ${provider.errorMessage}'))
              : provider.promotions.isEmpty
                  ? const Center(child: Text('Chưa có khuyến mãi nào.'))
                  : RefreshIndicator(
                      onRefresh: () => context.read<PromotionProvider>().fetchPromotions(),
                      child: ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: provider.promotions.length,
                        itemBuilder: (context, index) {
                          final promo = provider.promotions[index];
                          return Card(
                            margin: const EdgeInsets.only(bottom: 16),
                            clipBehavior: Clip.antiAlias,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            child: InkWell(
                              onTap: () {
                                Navigator.pushNamed(context, '/promotion_detail', arguments: promo);
                              },
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  AspectRatio(
                                    aspectRatio: 16 / 9,
                                    child: CustomImageWidget(
                                      imageUrl: promo.imageUrl,
                                      localAsset: promo.imageAsset ?? 'assets/images/placeholder.png',
                                    ),
                                  ),
                                  Padding(
                                    padding: const EdgeInsets.all(16),
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(promo.title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                                        const SizedBox(height: 8),
                                        Text('Từ ${promo.validFrom} đến ${promo.validTo}', style: const TextStyle(color: Colors.grey)),
                                        if (promo.status != null) ...[
                                          const SizedBox(height: 8),
                                          Container(
                                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                            decoration: BoxDecoration(color: Colors.red.shade50, borderRadius: BorderRadius.circular(8)),
                                            child: Text(promo.status!, style: const TextStyle(color: Colors.red, fontWeight: FontWeight.w600)),
                                          )
                                        ]
                                      ],
                                    ),
                                  )
                                ],
                              ),
                            ),
                          );
                        },
                      ),
                  ),
    );
  }
}
"""
with open("lib/screens/promotions/promotion_list_screen.dart", "w", encoding="utf-8") as f: f.write(list_screen)

detail_screen = """import 'package:flutter/material.dart';
import '../../models/promotion_model.dart';
import '../../widgets/custom_image_widget.dart';

class PromotionDetailScreen extends StatelessWidget {
  final PromotionModel promotion;

  const PromotionDetailScreen({super.key, required this.promotion});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Chi tiết Khuyến Mãi')),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            AspectRatio(
              aspectRatio: 16 / 9,
              child: CustomImageWidget(
                imageUrl: promotion.imageUrl,
                localAsset: promotion.imageAsset ?? 'assets/images/placeholder.png',
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(promotion.title, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 16),
                  
                  if (promotion.discountValue != null)
                    _buildSection('Mức khuyến mãi', promotion.discountValue!, Icons.local_offer, Colors.red),
                    
                  _buildSection('Thời gian', '${promotion.validFrom} - ${promotion.validTo}', Icons.date_range, Colors.blue),
                  
                  if (promotion.status != null)
                    _buildSection('Trạng thái', promotion.status!, Icons.info, Colors.orange),

                  const Divider(height: 32),
                  const Text('Nội dung chương trình', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Text(promotion.description ?? 'Không có thông tin', style: const TextStyle(fontSize: 16, height: 1.5)),
                  
                  const Divider(height: 32),
                  const Text('Điều kiện áp dụng', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Text(promotion.conditions ?? 'Không có thông tin', style: const TextStyle(fontSize: 16, height: 1.5)),
                ],
              ),
            )
          ],
        ),
      ),
    );
  }

  Widget _buildSection(String title, String content, IconData icon, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontSize: 14, color: Colors.grey)),
                const SizedBox(height: 4),
                Text(content, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
              ],
            ),
          )
        ],
      ),
    );
  }
}
"""
with open("lib/screens/promotions/promotion_detail_screen.dart", "w", encoding="utf-8") as f: f.write(detail_screen)

# Inject routing and provider
def update_router():
    router_path = "lib/routes/app_router.dart"
    with open(router_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "/promotions" not in content:
        content = content.replace(
            "import '../screens/contracts/contract_detail_screen.dart';", 
            "import '../screens/contracts/contract_detail_screen.dart';\nimport '../screens/promotions/promotion_list_screen.dart';\nimport '../screens/promotions/promotion_detail_screen.dart';\nimport '../models/promotion_model.dart';"
        )
        routes = """
          case '/promotions':
            return const PromotionListScreen();
          case '/promotion_detail':
            final promo = settings.arguments as PromotionModel;
            return PromotionDetailScreen(promotion: promo);
"""
        content = content.replace("case '/device_detail':", routes + "          case '/device_detail':")
        with open(router_path, "w", encoding="utf-8") as f:
            f.write(content)

def insert_provider(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "PromotionProvider" not in content:
        import_str = "import 'package:quan_ly_cho_thue_thiet_bi/providers/promotion_provider.dart';\nimport 'package:quan_ly_cho_thue_thiet_bi/repositories/promotion_repository.dart';\nimport 'package:quan_ly_cho_thue_thiet_bi/datasources/promotion/local_promotion_datasource.dart';\n"
        if "package:quan_ly_cho_thue_thiet_bi" not in content and "main.dart" in file_path:
            import_str = "import 'providers/promotion_provider.dart';\nimport 'repositories/promotion_repository.dart';\nimport 'datasources/promotion/local_promotion_datasource.dart';\n"
        content = import_str + content
        provider_str = """
          ChangeNotifierProvider(
            create: (_) => PromotionProvider(
              PromotionRepository(LocalPromotionDataSource()),
            ),
          ),"""
        content = content.replace("providers: [", "providers: [" + provider_str)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

update_router()
insert_provider("lib/main.dart")
insert_provider("test/widget_test.dart")

print("Promotion UI and wiring setup.")