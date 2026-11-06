import 'services/api_session.dart';
import 'providers/rental_provider.dart';
import 'repositories/rental_repository.dart';
import 'datasources/rental/remote_rental_datasource.dart';
import 'providers/report_provider.dart';
import 'repositories/report_repository.dart';
import 'datasources/report/remote_report_datasource.dart';
import 'providers/search_provider.dart';
import 'repositories/search_repository.dart';
import 'datasources/search/remote_search_datasource.dart';
import 'providers/feedback_provider.dart';
import 'repositories/feedback_repository.dart';
import 'datasources/feedback/remote_feedback_datasource.dart';
import 'providers/maintenance_provider.dart';
import 'repositories/maintenance_repository.dart';
import 'datasources/maintenance/remote_maintenance_datasource.dart';
import 'providers/incident_provider.dart';
import 'repositories/incident_repository.dart';
import 'datasources/incident/remote_incident_datasource.dart';
import 'providers/renewal_provider.dart';
import 'repositories/renewal_repository.dart';
import 'datasources/renewal/remote_renewal_datasource.dart';
import 'providers/promotion_provider.dart';
import 'repositories/promotion_repository.dart';
import 'datasources/promotion/remote_promotion_datasource.dart';
import 'providers/installation_provider.dart';
import 'repositories/installation_repository.dart';
import 'datasources/installation/remote_installation_datasource.dart';
import 'providers/contract_provider.dart';
import 'repositories/contract_repository.dart';
import 'datasources/contract/remote_contract_datasource.dart';
import 'providers/device_provider.dart';
import 'providers/app_config_provider.dart';

import 'repositories/device_repository.dart';

import 'package:flutter/material.dart';

import 'package:provider/provider.dart';

import 'datasources/remote/remote_auth_datasource.dart';

import 'repositories/auth_repository.dart';

import 'providers/auth_provider.dart';

import 'repositories/dashboard_repository.dart';

import 'providers/dashboard_provider.dart';

import 'routes/app_router.dart';
import 'theme/app_theme.dart';

import 'datasources/device/remote_device_datasource.dart';


void main() {

  runApp(

    MultiProvider(

      providers: [
          ChangeNotifierProvider(
            create: (_) => RentalProvider(
              RentalRepository(RemoteRentalDataSource()),
            ),
          ),
          ChangeNotifierProvider(
            create: (_) => ReportProvider(
              ReportRepository(RemoteReportDataSource()),
            ),
          ),
          ChangeNotifierProvider(
            create: (_) => SearchProvider(
              SearchRepository(RemoteSearchDataSource()),
            ),
          ),
          ChangeNotifierProvider(
            create: (_) => FeedbackProvider(
              FeedbackRepository(RemoteFeedbackDataSource()),
            ),
          ),
          ChangeNotifierProvider(
            create: (_) => MaintenanceProvider(
              MaintenanceRepository(RemoteMaintenanceDataSource()),
            ),
          ),
          ChangeNotifierProvider(
            create: (_) => IncidentProvider(
              IncidentRepository(RemoteIncidentDataSource()),
            ),
          ),
          ChangeNotifierProvider(
            create: (_) => RenewalProvider(
              RenewalRepository(RemoteRenewalDataSource()),
            ),
          ),
          ChangeNotifierProvider(
            create: (_) => PromotionProvider(
              PromotionRepository(RemotePromotionDataSource()),
            ),
          ),
          ChangeNotifierProvider(
            create: (_) => InstallationProvider(
              InstallationRepository(RemoteInstallationDataSource()),
            ),
          ),
          ChangeNotifierProvider(
            create: (_) => ContractProvider(
              ContractRepository(RemoteContractDataSource()),
            ),
          ),

          ChangeNotifierProvider(

            create: (_) => DeviceProvider(

              DeviceRepository(RemoteDeviceDataSource()),

            ),

          ),

        ChangeNotifierProvider(

          create: (_) => AuthProvider(

            AuthRepository(RemoteAuthDataSource()),
            sessionExpired: ApiSession.expired,
          ),

        ),

        ChangeNotifierProvider(
          create: (_) => AppConfigProvider(),
        ),

        ChangeNotifierProvider(

          create: (_) => DashboardProvider(

            DashboardRepository(RemoteDashboardDataSource()),

          ),

        ),

      ],

      child: const MyApp(),

    ),

  );

}



class MyApp extends StatelessWidget {

  const MyApp({super.key});



  @override

  Widget build(BuildContext context) {
    final config = context.watch<AppConfigProvider>();

    return MaterialApp(

      title: 'Thiết Bị Điện Tử',

      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: config.themeMode,
      initialRoute: '/',
      onGenerateRoute: AppRouter.generateRoute,
      debugShowCheckedModeBanner: false,
    );

  }

}