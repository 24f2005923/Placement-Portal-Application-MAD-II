import api from './axios'

// company API calls

export const companyAPI = {

  // dashboard stats
  getStats: function () {
    return api.get('/api/company/stats')
  },

  // profile
  getProfile: function () {
    return api.get('/api/company/profile')
  },
  updateProfile: function (data) {
    return api.put('/api/company/profile', data)
  },

  // placement drives
  getDrives: function () {
    return api.get('/api/company/drives')
  },
  getDrive: function (driveId) {
    return api.get('/api/company/drives/' + driveId)
  },
  createDrive: function (driveData) {
    return api.post('/api/company/drives', driveData)
  },
  updateDrive: function (driveId, driveData) {
    return api.put('/api/company/drives/' + driveId, driveData)
  },
  deleteDrive: function (driveId) {
    return api.delete('/api/company/drives/' + driveId)
  },
  closeDrive: function (driveId) {
    return api.put('/api/company/drives/' + driveId + '/close')
  },

  // applications
  getApplications: function (params) {
    return api.get('/api/company/applications', { params: params || {} })
  },
  shortlistApplication: function (appId) {
    return api.put('/api/company/applications/' + appId + '/shortlist')
  },
  rejectApplication: function (appId) {
    return api.put('/api/company/applications/' + appId + '/reject')
  },
  updateApplicationStatus: function (appId, newStatus) {
    return api.put('/api/company/applications/' + appId + '/status', { status: newStatus })
  },

  // interviews
  getInterviews: function () {
    return api.get('/api/company/interviews')
  },
  scheduleInterview: function (interviewData) {
    return api.post('/api/company/interviews', interviewData)
  },

  // results
  getResults: function () {
    return api.get('/api/company/results')
  },
  publishResult: function (resultData) {
    return api.post('/api/company/results/publish', resultData)
  }

}
