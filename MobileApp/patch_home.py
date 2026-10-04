import os

p = "lib/screens/home/home_screen.dart"
with open(p, "r", encoding="utf-8") as f:
    content = f.read()

admin_dashboard_old = """        SummaryCard(
          title: 'Công việc đang xử lý',
          value: stats.processingTasks.toString(),
          icon: Icons.sync_rounded,
          color: AppColors.info,
        ),
      ],
    );"""

admin_dashboard_new = """        SummaryCard(
          title: 'Công việc đang xử lý',
          value: stats.processingTasks.toString(),
          icon: Icons.sync_rounded,
          color: AppColors.info,
        ),
        const SizedBox(height: 24),
        const SectionTitle(title: 'Quản lý vận hành'),
        Wrap(
          spacing: 16,
          runSpacing: 16,
          alignment: WrapAlignment.start,
          children: [
            QuickActionCard(title: 'Sự cố', icon: Icons.report_problem_rounded, onTap: () => Navigator.pushNamed(context, '/incidents')),
            QuickActionCard(title: 'Bảo trì', icon: Icons.build_rounded, onTap: () => Navigator.pushNamed(context, '/maintenances')),
            QuickActionCard(title: 'Phản hồi', icon: Icons.feedback_rounded, onTap: () => Navigator.pushNamed(context, '/feedbacks')),
            QuickActionCard(title: 'Khuyến mãi', icon: Icons.local_offer_rounded, onTap: () => Navigator.pushNamed(context, '/promotions')),
          ],
        ),
      ],
    );"""

if admin_dashboard_old in content:
    content = content.replace(admin_dashboard_old, admin_dashboard_new)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    print("Admin dashboard updated successfully!")
else:
    print("Old code not found. Trying flexible replacement.")
    # Fallback if needed, but it should match since I wrote it recently.