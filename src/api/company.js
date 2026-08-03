import httpClient from './axios'
import { get, post, put, del, buildPath } from './http'

// company API calls

export const companyAPI = {

  // dashboard stats
  getStats: function () {
    return get('/api/company/stats')
  },

  // profile
  getProfile: function () {
    return get('/api/company/profile')
  },
  updateProfile: function (data) {
    return put('/api/company/profile', data)
  },

  // placement drives
  getDrives: function () {
    return get('/api/company/drives')
  },
  getDrive: function (driveId) {
    return get(buildPath('/api/company/drives', driveId))
  },
  createDrive: function (driveData) {
    return post('/api/company/drives', driveData)
  },
  updateDrive: function (driveId, driveData) {
    return put(buildPath('/api/company/drives', driveId), driveData)
  },
  deleteDrive: function (driveId) {
    return del(buildPath('/api/company/drives', driveId))
  },
  closeDrive: function (driveId) {
    return put(buildPath('/api/company/drives', driveId, '/close'))
  },

  // applications
  getApplications: function (params) {
    return get('/api/company/applications', params)
  },
  shortlistApplication: function (appId) {
    return put(buildPath('/api/company/applications', appId, '/shortlist'))
  },
  rejectApplication: function (appId) {
    return put(buildPath('/api/company/applications', appId, '/reject'))
  },
  updateApplicationStatus: function (appId, newStatus) {
    return put(buildPath('/api/company/applications', appId, '/status'), { status: newStatus })
  },
  exportApplicationsCsv: function (driveId) {
    return post('/api/company/applications/export', { drive_id: driveId })
  },
  getApplicationsExportStatus: function (taskId) {
    return get('/api/company/applications/export/status/' + taskId)
  },
  downloadApplicationsExport: function (filename) {
    return httpClient.get('/api/company/applications/export/download/' + filename, {
      responseType: 'blob'
    })
  },

  // interviews
  getInterviews: function () {
    return get('/api/company/interviews')
  },
  scheduleInterview: function (interviewData) {
    return post('/api/company/interviews', interviewData)
  },
  sendInterviewEmail: function (interviewId) {
    return post(buildPath('/api/company/interviews', interviewId, '/email'))
  },

  // results
  getResults: function () {
    return get('/api/company/results')
  },
  publishResult: function (resultData) {
    return post('/api/company/results/publish', resultData)
  }

}
