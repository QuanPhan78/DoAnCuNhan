import 'providers/report_provider.dart';
import 'repositories/report_repository.dart';
import 'datasources/report/local_report_datasource.dart';
import 'providers/search_provider.dart';
import 'repositories/search_repository.dart';
import 'datasources/search/local_search_datasource.dart';
import 'providers/feedback_provider.dart';
import 'repositories/feedback_repository.dart';
import 'datasources/feedback/local_feedback_datasource.dart';
import 'providers/maintenance_provider.dart';
import 'repositories/maintenance_repository.dart';
import 'datasources/maintenance/local_maintenance_datasource.dart';
import 'providers/incident_provider.dart';
import 'repositories/incident_repository.dart';
import 'datasources/incident/local_incident_datasource.dart';
import 'providers/renewal_provider.dart';
import 'repositories/renewal_repository.dart';
import 'datasources/renewal/local_renewal_datasource.dart';
import 'providers/promotion_provider.dart';
import 'repositories/promotion_repository.dart';
import 'datasources/promotion/local_promotion_datasource.dart';
import 'providers/installation_provider.dart';
import 'repositories/installation_repository.dart';
import 'datasources/installation/local_installation_datasource.dart';
import 'providers/contract_provider.dart';
import 'repositories/contract_repository.dart';
import 'datasources/contract/local_contract_datasource.dart';
import 'providers/device_provider.dart';

import 'repositories/device_repository.dart';

import 'datasources/device/local_device_datasource.dart';

import 'package:flutter/material.dart';

import 'package:provider/provider.dart';

import 'datasources/local/local_auth_datasource.dart';

import 'repositories/auth_repository.dart';

import 'providers/auth_provider.dart';

import 'repositories/dashboard_repository.dart';

import 'providers/dashboard_provider.dart';

import 'routes/app_router.dart';
import 'theme/app_theme.dart';



void main() {

  runApp(

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

          create: (_) => AuthProvider(

            AuthRepository(LocalAuthDataSource()),

          )..checkSession(),

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

}



class MyApp extends StatelessWidget {

  const MyApp({super.key});



  @override

  Widget build(BuildContext context) {

    return MaterialApp(

      title: 'Thiết Bị Điện Tử',

      theme: AppTheme.lightTheme,
      initialRoute: '/',
      onGenerateRoute: AppRouter.generateRoute,
      debugShowCheckedModeBanner: false,
    );

  }

}