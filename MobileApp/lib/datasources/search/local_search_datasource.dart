import 'dart:convert';
import 'package:flutter/services.dart';
import '../../models/search/search_result_model.dart';
import '../../models/device_model.dart';
import '../../models/contract_model.dart';
import '../../models/incident_model.dart';
import '../../models/maintenance_model.dart';
import '../../models/role_enum.dart';
import 'search_datasource.dart';

class LocalSearchDataSource implements SearchDataSource {
  @override
  Future<List<SearchResultModel>> search(String query, {String filterType = 'all', String? userId, Role? role}) async {
    await Future.delayed(const Duration(milliseconds: 400));
    final String lowerQuery = query.toLowerCase().trim();
    List<SearchResultModel> results = [];

    // 1. Load Data
    final devicesRaw = json.decode(await rootBundle.loadString('assets/mock/devices.json')) as List;
    final contractsRaw = json.decode(await rootBundle.loadString('assets/mock/contracts.json')) as List;
    final incidentsRaw = json.decode(await rootBundle.loadString('assets/mock/incidents.json')) as List;
    final maintenancesRaw = json.decode(await rootBundle.loadString('assets/mock/maintenances.json')) as List;

    // 2. Parse & Filter Devices
    if (filterType == 'all' || filterType == 'device') {
      for (var raw in devicesRaw) {
        final d = DeviceModel.fromJson(raw);
        final match = d.name.toLowerCase().contains(lowerQuery) ||
            (d.code?.toLowerCase().contains(lowerQuery) ?? false) ||
            d.type.toLowerCase().contains(lowerQuery) ||
            (d.brand?.toLowerCase().contains(lowerQuery) ?? false) ||
            (d.model?.toLowerCase().contains(lowerQuery) ?? false) ||
            (d.rentalStatus?.toLowerCase().contains(lowerQuery) ?? false);
        
        if (match) {
          results.add(SearchResultModel(
            id: d.id,
            type: 'device',
            title: d.name,
            subtitle: 'Mã: ${d.code} - ${d.brand ?? ''}',
            status: d.rentalStatus,
            originalData: d,
          ));
        }
      }
    }

    // 3. Parse & Filter Contracts
    if (filterType == 'all' || filterType == 'contract') {
      for (var raw in contractsRaw) {
        final c = ContractModel.fromJson(raw);
        // Security check for Customer
        if (role == Role.customer && c.customerId != userId) continue;

        final match = (c.contractCode?.toLowerCase().contains(lowerQuery) ?? false) ||
            (c.customerName?.toLowerCase().contains(lowerQuery) ?? false) ||
            (c.deviceIds?.any((id) => id.toLowerCase().contains(lowerQuery)) ?? false);
        
        if (match) {
          results.add(SearchResultModel(
            id: c.id,
            type: 'contract',
            title: c.contractCode ?? 'Hợp đồng vô danh',
            subtitle: 'KH: ${c.customerName ?? 'N/A'}',
            status: c.status,
            originalData: c,
          ));
        }
      }
    }

    // 4. Parse & Filter Incidents
    if (filterType == 'all' || filterType == 'incident') {
      for (var raw in incidentsRaw) {
        final inc = IncidentModel.fromJson(raw);
        // Customer check (Assuming contract IDs would be checked in a real app, here we just allow it for mock or strict filter)
        // Simplified mock security
        final match = inc.code.toLowerCase().contains(lowerQuery) ||
            inc.issueType.toLowerCase().contains(lowerQuery) ||
            inc.description.toLowerCase().contains(lowerQuery) ||
            inc.contractId.toLowerCase().contains(lowerQuery);
        
        if (match) {
          results.add(SearchResultModel(
            id: inc.id,
            type: 'incident',
            title: inc.code,
            subtitle: inc.issueType,
            status: inc.status,
            originalData: inc,
          ));
        }
      }
    }

    // 5. Parse & Filter Maintenances
    if (filterType == 'all' || filterType == 'maintenance') {
      for (var raw in maintenancesRaw) {
        final m = MaintenanceModel.fromJson(raw);
        final match = (m.requestCode?.toLowerCase().contains(lowerQuery) ?? false) ||
            (m.customer?.toLowerCase().contains(lowerQuery) ?? false) ||
            (m.description?.toLowerCase().contains(lowerQuery) ?? false) ||
            (m.assignedEmployee?.toLowerCase().contains(lowerQuery) ?? false);
        
        if (match) {
          results.add(SearchResultModel(
            id: m.id,
            type: 'maintenance',
            title: m.requestCode ?? 'N/A',
            subtitle: 'KH: ${m.customer ?? 'N/A'}',
            status: m.status,
            originalData: m,
          ));
        }
      }
    }

    return results;
  }
}