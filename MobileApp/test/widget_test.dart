import 'package:quan_ly_cho_thue_thiet_bi/providers/report_provider.dart';
import 'package:quan_ly_cho_thue_thiet_bi/repositories/report_repository.dart';
import 'package:quan_ly_cho_thue_thiet_bi/datasources/report/local_report_datasource.dart';
import 'package:quan_ly_cho_thue_thiet_bi/providers/search_provider.dart';
import 'package:quan_ly_cho_thue_thiet_bi/repositories/search_repository.dart';
import 'package:quan_ly_cho_thue_thiet_bi/datasources/search/local_search_datasource.dart';
import 'package:quan_ly_cho_thue_thiet_bi/providers/feedback_provider.dart';
import 'package:quan_ly_cho_thue_thiet_bi/repositories/feedback_repository.dart';
import 'package:quan_ly_cho_thue_thiet_bi/datasources/feedback/local_feedback_datasource.dart';
import 'package:quan_ly_cho_thue_thiet_bi/providers/maintenance_provider.dart';
import 'package:quan_ly_cho_thue_thiet_bi/repositories/maintenance_repository.dart';
import 'package:quan_ly_cho_thue_thiet_bi/datasources/maintenance/local_maintenance_datasource.dart';
import 'package:quan_ly_cho_thue_thiet_bi/providers/incident_provider.dart';
import 'package:quan_ly_cho_thue_thiet_bi/repositories/incident_repository.dart';
import 'package:quan_ly_cho_thue_thiet_bi/datasources/incident/local_incident_datasource.dart';
import 'package:quan_ly_cho_thue_thiet_bi/providers/renewal_provider.dart';
import 'package:quan_ly_cho_thue_thiet_bi/repositories/renewal_repository.dart';
import 'package:quan_ly_cho_thue_thiet_bi/datasources/renewal/local_renewal_datasource.dart';
import 'package:quan_ly_cho_thue_thiet_bi/providers/promotion_provider.dart';
import 'package:quan_ly_cho_thue_thiet_bi/repositories/promotion_repository.dart';
import 'package:quan_ly_cho_thue_thiet_bi/datasources/promotion/local_promotion_datasource.dart';
import 'package:quan_ly_cho_thue_thiet_bi/providers/installation_provider.dart';
import 'package:quan_ly_cho_thue_thiet_bi/repositories/installation_repository.dart';
import 'package:quan_ly_cho_thue_thiet_bi/datasources/installation/local_installation_datasource.dart';
import 'package:quan_ly_cho_thue_thiet_bi/providers/contract_provider.dart';
import 'package:quan_ly_cho_thue_thiet_bi/repositories/contract_repository.dart';
import 'package:quan_ly_cho_thue_thiet_bi/datasources/contract/local_contract_datasource.dart';
import 'package:quan_ly_cho_thue_thiet_bi/providers/device_provider.dart';

import 'package:quan_ly_cho_thue_thiet_bi/repositories/device_repository.dart';

import 'package:quan_ly_cho_thue_thiet_bi/datasources/device/local_device_datasource.dart';

import 'package:flutter_test/flutter_test.dart';

import 'package:provider/provider.dart';

import 'package:shared_preferences/shared_preferences.dart';

import 'package:quan_ly_cho_thue_thiet_bi/main.dart';

import 'package:quan_ly_cho_thue_thiet_bi/providers/auth_provider.dart';

import 'package:quan_ly_cho_thue_thiet_bi/repositories/auth_repository.dart';

import 'package:quan_ly_cho_thue_thiet_bi/datasources/local/local_auth_datasource.dart';

import 'package:quan_ly_cho_thue_thiet_bi/providers/dashboard_provider.dart';

import 'package:quan_ly_cho_thue_thiet_bi/repositories/dashboard_repository.dart';



void main() {

  setUp(() {

    SharedPreferences.setMockInitialValues({});

  });



  testWidgets('App should render splash screen and navigate', (WidgetTester tester) async {

    await tester.pumpWidget(

      MultiProvider(

        providers: [
          ChangeNotifierProvider(
            create: (_) => ReportProvider(
              ReportRepository(LocalReportDataSource()),
            ),
          ),
          ChangeNotifierProvider(
            create: (_) => SearchProvider(
              SearchRepository(LocalSearchDataSource()),
            ),
          ),
          ChangeNotifierProvider(
            create: (_) => FeedbackProvider(
              FeedbackRepository(LocalFeedbackDataSource()),
            ),
          ),
          ChangeNotifierProvider(
            create: (_) => MaintenanceProvider(
              MaintenanceRepository(LocalMaintenanceDataSource()),
            ),
          ),
          ChangeNotifierProvider(
            create: (_) => IncidentProvider(
              IncidentRepository(LocalIncidentDataSource()),
            ),
          ),
          ChangeNotifierProvider(
            create: (_) => RenewalProvider(
              RenewalRepository(LocalRenewalDataSource()),
            ),
          ),
          ChangeNotifierProvider(
            create: (_) => PromotionProvider(
              PromotionRepository(LocalPromotionDataSource()),
            ),
          ),
          ChangeNotifierProvider(
            create: (_) => InstallationProvider(
              InstallationRepository(LocalInstallationDataSource()),
            ),
          ),
          ChangeNotifierProvider(
            create: (_) => ContractProvider(
              ContractRepository(LocalContractDataSource()),
            ),
          ),

          ChangeNotifierProvider(

            create: (_) => DeviceProvider(

              DeviceRepository(LocalDeviceDataSource()),

            ),

          ),

          ChangeNotifierProvider(

            create: (_) => AuthProvider(AuthRepository(LocalAuthDataSource())),

          ),

          ChangeNotifierProvider(

            create: (_) => DashboardProvider(

              DashboardRepository(LocalDashboardDataSource()),

            ),

          ),

        ],

        child: const MyApp(),

      ),

    );



    expect(find.text('Thiết Bị Điện Tử'), findsOneWidget);

    await tester.pumpAndSettle(const Duration(seconds: 2));

    expect(find.text('Quản lý thiết bị điện tử'), findsWidgets);

  });

}

