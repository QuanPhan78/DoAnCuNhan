enum AppPermission {
  // Quyền Khách hàng
  viewDevices,
  viewOwnContracts,
  viewRentalHistory,
  requestExtension,
  reportIssue,
  trackMaintenance,
  submitFeedback,
  viewPromotions,

  // Quyền Nhân viên
  viewAssignedTasks,
  viewAssignedMaintenance,
  updateTaskStatus,

  // Quyền Quản lý
  manageDevices,
  manageContracts,
  manageMaintenance,
  viewReports,
}