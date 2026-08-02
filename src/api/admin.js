import api from './axios'

// all admin API calls

export const adminAPI = {

  // dashboard
  getStats: function () {
    return api.get('/api/admin/stats')
  },
  getActivities: function () {
    return api.get('/api/admin/activities')
  },

  // reports — analytics (live DB)
  getPlacementAnalytics: function () {
    return api.get('/api/admin/reports/analytics')
  },
  getTopCompanies: function (limit) {
    return api.get('/api/admin/reports/companies/top', { params: { limit: limit || 10 } })
  },
  generateReport: function (payload) {
    return api.post('/api/admin/reports/generate', payload || {})
  },
  getReportStatus: function (taskId) {
    return api.get('/api/admin/reports/status/' + taskId)
  },
  listReports: function () {
    return api.get('/api/admin/reports/list')
  },

  // csv exports
  triggerStudentExport: function (payload) {
    return api.post('/api/admin/export/students', payload || {})
  },
  triggerCompanyExport: function (payload) {
    return api.post('/api/admin/export/companies', payload || {})
  },
  getApplications: function (params) {
    return api.get('/api/admin/applications', { params: params || {} })
  },
  setApplicationStatus: function (appId, newStatus) {
    return api.put('/api/admin/applications/' + appId + '/status', { status: newStatus })
  },

  // students management
  getStudents: function (params) {
    return api.get('/api/admin/students', { params: params || {} })
  },
  getStudent: function (studentId) {
    return api.get('/api/admin/students/' + studentId)
  },
  updateStudent: function (studentId, data) {
    return api.put('/api/admin/students/' + studentId, data)
  },
  setStudentStatus: function (studentId, newStatus) {
    return api.put('/api/admin/students/' + studentId + '/status', { status: newStatus })
  },

  // companies management
  getCompanies: function (params) {
    return api.get('/api/admin/companies', { params: params || {} })
  },
  getCompany: function (companyId) {
    return api.get('/api/admin/companies/' + companyId)
  },
  approveCompany: function (companyId) {
    return api.put('/api/admin/companies/' + companyId + '/approve')
  },
  rejectCompany: function (companyId) {
    return api.put('/api/admin/companies/' + companyId + '/reject')
  },
  blacklistCompany: function (companyId, flag) {
    return api.put('/api/admin/companies/' + companyId + '/blacklist', { blacklisted: flag })
  },

  // placement drives management
  getDrives: function (params) {
    return api.get('/api/admin/drives', { params: params || {} })
  },
  getDrive: function (driveId) {
    return api.get('/api/admin/drives/' + driveId)
  },
  approveDrive: function (driveId) {
    return api.put('/api/admin/drives/' + driveId + '/approve')
  },
  rejectDrive: function (driveId) {
    return api.put('/api/admin/drives/' + driveId + '/reject')
  },
  closeDrive: function (driveId) {
    return api.put('/api/admin/drives/' + driveId + '/close')
  },
  setDriveStatus: function (driveId, newStatus) {
    return api.put('/api/admin/drives/' + driveId + '/status', { status: newStatus })
  }

}
