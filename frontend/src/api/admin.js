import { get, post, put, buildPath } from './http'
import httpClient from './axios'

// all admin API calls

export const adminAPI = {

  // dashboard
  getStats: function () {
    return get('/api/admin/stats')
  },
  getActivities: function () {
    return get('/api/admin/activities')
  },

  // reports — analytics (live DB)
  getMonthlyActivityReport: function (params) {
    return get('/api/admin/reports/monthly-activity', params)
  },
  generateReport: function (payload) {
    return post('/api/admin/reports/generate', payload)
  },
  getReportStatus: function (taskId) {
    return get('/api/admin/reports/status/' + taskId)
  },
  downloadExportFile: function (filename) {
    return httpClient.get('/api/admin/export/download/' + filename, { responseType: 'blob' })
  },

  // csv exports
  triggerStudentExport: function (payload) {
    return post('/api/admin/export/students', payload)
  },
  triggerCompanyExport: function (payload) {
    return post('/api/admin/export/companies', payload)
  },
  getApplications: function (params) {
    return get('/api/admin/applications', params)
  },
  setApplicationStatus: function (appId, newStatus) {
    return put(buildPath('/api/admin/applications', appId, '/status'), { status: newStatus })
  },

  // students management
  getStudents: function (params) {
    return get('/api/admin/students', params)
  },
  getStudent: function (studentId) {
    return get(buildPath('/api/admin/students', studentId))
  },
  updateStudent: function (studentId, data) {
    return put(buildPath('/api/admin/students', studentId), data)
  },
  setStudentStatus: function (studentId, newStatus) {
    return put(buildPath('/api/admin/students', studentId, '/status'), { status: newStatus })
  },

  // companies management
  getCompanies: function (params) {
    return get('/api/admin/companies', params)
  },
  getCompany: function (companyId) {
    return get(buildPath('/api/admin/companies', companyId))
  },
  approveCompany: function (companyId) {
    return put(buildPath('/api/admin/companies', companyId, '/approve'))
  },
  rejectCompany: function (companyId) {
    return put(buildPath('/api/admin/companies', companyId, '/reject'))
  },
  blacklistCompany: function (companyId, flag) {
    return put(buildPath('/api/admin/companies', companyId, '/blacklist'), { blacklisted: flag })
  },

  // placement drives management
  getDrives: function (params) {
    return get('/api/admin/drives', params)
  },
  getDrive: function (driveId) {
    return get(buildPath('/api/admin/drives', driveId))
  },
  approveDrive: function (driveId) {
    return put(buildPath('/api/admin/drives', driveId, '/approve'))
  },
  rejectDrive: function (driveId) {
    return put(buildPath('/api/admin/drives', driveId, '/reject'))
  },
  closeDrive: function (driveId) {
    return put(buildPath('/api/admin/drives', driveId, '/close'))
  },
  setDriveStatus: function (driveId, newStatus) {
    return put(buildPath('/api/admin/drives', driveId, '/status'), { status: newStatus })
  }

}
