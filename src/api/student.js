import httpClient from './axios'
import { get, post, put, multipartPost, buildPath } from './http'

export const studentAPI = {
  getStats: function () {
    return get('/api/student/stats')
  },

  getProfile: function () {
    return get('/api/student/profile')
  },

  updateProfile: function (payload) {
    return put('/api/student/profile', payload)
  },

  uploadResume: function (file) {
    const formData = new FormData()
    formData.append('resume', file)
    return multipartPost('/api/student/resume', formData)
  },

  getDrives: function (params) {
    return get('/api/student/drives', params)
  },

  getDrive: function (driveId) {
    return get(buildPath('/api/student/drives', driveId))
  },

  applyForDrive: function (driveId, coverNote, resumeFile) {
    if (resumeFile) {
      const formData = new FormData()
      formData.append('drive_id', driveId)
      if (coverNote) formData.append('cover_note', coverNote)
      formData.append('resume', resumeFile)
      return multipartPost('/api/student/applications', formData)
    }
    return post('/api/student/applications', {
      drive_id: driveId,
      cover_note: coverNote || ''
    })
  },

  getApplications: function () {
    return get('/api/student/applications')
  },

  getInterviews: function () {
    return get('/api/student/interviews')
  },

  getHistory: function () {
    return get('/api/student/history')
  },

  getOfferLetterUrl: function (appId) {
    const token = localStorage.getItem('access_token')
    return `/api/student/applications/${appId}/offer-letter?token=${token}`
  },

  downloadOfferLetter: function (appId) {
    return httpClient.get(buildPath('/api/student/applications', appId, '/offer-letter'), {
      responseType: 'blob'
    })
  }
}

