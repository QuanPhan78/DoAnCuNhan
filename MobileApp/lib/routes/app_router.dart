import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/permission_enum.dart';
import '../models/device_model.dart';
import '../providers/auth_provider.dart';
import '../utils/permission_manager.dart';

import '../screens/splash/splash_screen.dart';
import '../screens/onboarding/onboarding_screen.dart';
import '../screens/auth/login_screen.dart';
import '../screens/auth/register_screen.dart';
import '../screens/dashboard/dashboard_screen.dart';
import '../screens/unauthorized/unauthorized_screen.dart';
import '../screens/reports/reports_screen.dart';
import '../screens/devices/devices_screen.dart';
import '../screens/devices/device_detail_screen.dart';
import '../screens/contracts/contracts_screen.dart';
import '../screens/contracts/contract_detail_screen.dart';
import '../screens/tasks/tasks_screen.dart';
import '../widgets/core/custom_app_bar.dart';
import '../screens/promotions/promotion_list_screen.dart';
import '../screens/promotions/promotion_detail_screen.dart';
import '../screens/incidents/incident_list_screen.dart';
import '../screens/incidents/incident_detail_screen.dart';
import '../screens/incidents/create_incident_screen.dart';
import '../models/incident_model.dart';
import '../screens/maintenance/maintenance_list_screen.dart';
import '../screens/maintenance/maintenance_detail_screen.dart';
import '../screens/maintenance/maintenance_update_screen.dart';
import '../models/maintenance_model.dart';
import '../screens/feedbacks/feedback_list_screen.dart';
import '../screens/feedbacks/feedback_detail_screen.dart';
import '../screens/feedbacks/create_feedback_screen.dart';
import '../screens/search/search_screen.dart';
import '../models/feedback_model.dart';


import '../models/promotion_model.dart';
import '../models/contract_model.dart';
import '../models/rental_request_model.dart';
import '../screens/requests/rental_form_screen.dart';
import '../screens/requests/rental_confirm_screen.dart';
import '../screens/requests/requests_screen.dart';
import '../screens/requests/rental_detail_screen.dart';
import '../screens/notifications/notifications_screen.dart';

class AppRouter {
  static Route<dynamic> generateRoute(RouteSettings settings) {
    return MaterialPageRoute(
      builder: (context) {
        final authProvider = context.watch<AuthProvider>();
        final user = authProvider.currentUser;

        // Nếu truy cập các route không yêu cầu đăng nhập
        if (settings.name == '/' || settings.name == '/login' || settings.name == '/onboarding' || settings.name == '/register') {
           if (settings.name == '/') return const SplashScreen();
           if (settings.name == '/onboarding') return const OnboardingScreen();
           if (settings.name == '/login') return const LoginScreen();
           if (settings.name == '/register') return const RegisterScreen();
        }

        // Từ đây trở xuống là yêu cầu phải đăng nhập
        if (!authProvider.isAuthenticated || user == null) {
          // Trả về login nếu chưa đăng nhập
          return const LoginScreen();
        }

        switch (settings.name) {
          case '/dashboard':
            return const DashboardScreen();
          
          case '/devices':
            return const Scaffold(
              appBar: CustomAppBar(title: 'Thiết bị'),
              body: DevicesScreen(),
            );

          case '/contracts':
            return const Scaffold(
              appBar: CustomAppBar(title: 'Hợp đồng'),
              body: ContractsScreen(),
            );

          case '/tasks':
            return const Scaffold(
              appBar: CustomAppBar(title: 'Công việc'),
              body: TasksScreen(),
            );
          case '/notifications':
            return const Scaffold(
              appBar: CustomAppBar(title: 'Thông báo'),
              body: NotificationsScreen(),
            );
          
          case '/contract_detail':
            final contract = settings.arguments as ContractModel;
            return ContractDetailScreen(contract: contract);
          
          case '/promotions':
            return const PromotionListScreen();
          case '/promotion_detail':
            final promo = settings.arguments as PromotionModel;
            return PromotionDetailScreen(promotion: promo);
          
          case '/incidents':
            return const IncidentListScreen();
          case '/create_incident':
            return const CreateIncidentScreen();
          case '/incident_detail':
            final inc = settings.arguments as IncidentModel;
            return IncidentDetailScreen(incident: inc);
          
          case '/maintenances':
            return const MaintenanceListScreen();
          case '/maintenance_detail':
            final m = settings.arguments as MaintenanceModel;
            return MaintenanceDetailScreen(maintenance: m);
          case '/maintenance_update':
            final m2 = settings.arguments as MaintenanceModel;
            return MaintenanceUpdateScreen(maintenance: m2);
          
          case '/feedbacks':
            return const FeedbackListScreen();
          case '/create_feedback':
            return const CreateFeedbackScreen();
          case '/feedback_detail':
            final fb = settings.arguments as FeedbackModel;
            return FeedbackDetailScreen(feedback: fb);
          
          case '/search':
            return const SearchScreen();
          case '/device_detail':
            final device = settings.arguments as DeviceModel;
            return DeviceDetailScreen(device: device);

          case '/rental_form':
            final device = settings.arguments as DeviceModel;
            return RentalFormScreen(device: device);
          case '/rental_confirm':
            final req = settings.arguments as RentalRequestModel;
            return RentalConfirmScreen(requestData: req);
          case '/requests':
            return const RequestsScreen();
          case '/rental_detail':
            final req = settings.arguments as RentalRequestModel;
            return RentalDetailScreen(initialRequest: req);

          case '/admin/reports':
            // Ví dụ Route Guard: Check xem user có quyền viewReports không
            if (PermissionManager.hasPermission(user.role, AppPermission.viewReports)) {
              return const ReportsScreen();
            } else {
              return const UnauthorizedScreen();
            }
            
          default:
            return Scaffold(
              appBar: AppBar(title: const Text('Error')),
              body: const Center(child: Text('Không tìm thấy trang.')),
            );
        }
      },
    );
  }
}
