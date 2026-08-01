import httpClient from './axios'

export const studentAPI = {
  getStats: function () {
    return httpClient.get('/api/student/stats')
  },

  getProfile: function () {
    return httpClient.get('/api/student/profile')
  },

  updateProfile: function (payload) {
    return httpClient.put('/api/student/profile', payload)
  },

  uploadResume: function (file) {
    const formData = new FormData()
    formData.append('resume', file)
    return httpClient.post('/api/student/resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  getDrives: function (params) {
    return httpClient.get('/api/student/drives', { params: params || {} })
  },

  getDrive: function (driveId) {
    return httpClient.get('/api/student/drives/' + driveId)
  },

  applyForDrive: function (driveId, coverNote, resumeFile) {
    if (resumeFile) {
      const formData = new FormData()
      formData.append('drive_id', driveId)
      if (coverNote) formData.append('cover_note', coverNote)
      formData.append('resume', resumeFile)
      return httpClient.post('/api/student/applications', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    return httpClient.post('/api/student/applications', {
      drive_id: driveId,
      cover_note: coverNote || ''
    })
  },

  getApplications: function () {
    return httpClient.get('/api/student/applications')
  },

  getInterviews: function () {
    return httpClient.get('/api/student/interviews')
  },

  getHistory: function () {
    return httpClient.get('/api/student/history')
  }
}

