import api from './axios'

// student API calls

export const studentAPI = {

  // dashboard stats
  getStats: function () {
    return api.get('/api/student/stats')
  },

  // profile
  getProfile: function () {
    return api.get('/api/student/profile')
  },
  updateProfile: function (profileData) {
    return api.put('/api/student/profile', profileData)
  },

  // resume upload - needs multipart form data
  uploadResume: function (file) {
    const formData = new FormData()
    formData.append('resume', file)
    return api.post('/api/student/resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // placement drives
  getDrives: function (params) {
    return api.get('/api/student/drives', { params: params || {} })
  },
  getDrive: function (driveId) {
    return api.get('/api/student/drives/' + driveId)
  },

  // applications
  applyForDrive: function (driveId, coverNote) {
    return api.post('/api/student/applications', {
      drive_id: driveId,
      cover_note: coverNote || ''
    })
  },
  getApplications: function () {
    return api.get('/api/student/applications')
  },

  // interviews
  getInterviews: function () {
    return api.get('/api/student/interviews')
  },

  // placement history
  getHistory: function () {
    return api.get('/api/student/history')
  }

}
