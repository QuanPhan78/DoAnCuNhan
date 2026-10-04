import os

p = "lib/screens/home/home_screen.dart"
with open(p, "r", encoding="utf-8") as f:
    content = f.read()

staff_old = """            Expanded(
              child: SummaryCard(
                title: 'Hoàn thành',
                value: stats.completedRequests.toString(),
                icon: Icons.check_circle_rounded,
                color: AppColors.success,
              ),
            ),
          ],
        ),
      ],
    );"""

staff_new = """            Expanded(
              child: SummaryCard(
                title: 'Hoàn thành',
                value: stats.completedRequests.toString(),
                icon: Icons.check_circle_rounded,
                color: AppColors.success,
              ),
            ),
          ],
        ),
        const SizedBox(height: 24),
        const SectionTitle(title: 'Nhiệm vụ & Chức năng'),
        Wrap(
          spacing: 16,
          runSpacing: 16,
          alignment: WrapAlignment.start,
          children: [
            QuickActionCard(title: 'Sự cố', icon: Icons.report_problem_rounded, onTap: () => Navigator.pushNamed(context, '/incidents')),
            QuickActionCard(title: 'Bảo trì', icon: Icons.build_rounded, onTap: () => Navigator.pushNamed(context, '/maintenances')),
            QuickActionCard(title: 'Thiết bị', icon: Icons.devices_rounded, onTap: () => Navigator.pushNamed(context, '/devices')),
            QuickActionCard(title: 'Hợp đồng', icon: Icons.assignment_rounded, onTap: () => Navigator.pushNamed(context, '/contracts')),
          ],
        ),
      ],
    );"""

if staff_old in content:
    content = content.replace(staff_old, staff_new)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    print("Staff dashboard updated successfully!")
else:
    print("Old code not found. Need to check structure.")