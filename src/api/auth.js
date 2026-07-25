import httpClient from './axios'

export const authAPI = {
  login: function (emailInput, passwordInput) {
    return httpClient.post('/api/auth/login', { email: emailInput, password: passwordInput })
  },

  registerStudent: function (payload) {
    return httpClient.post('/api/auth/register/student', payload)
  },

  registerCompany: function (payload) {
    return httpClient.post('/api/auth/register/company', payload)
  },

  logout: function () {
    return httpClient.post('/api/auth/logout')
  },

  getCurrentUser: function () {
    return httpClient.get('/api/auth/me')
  },

  refreshToken: function () {
    const refreshKey = localStorage.getItem('refresh_token')
    return httpClient.post('/api/auth/refresh', {}, {
      headers: { Authorization: 'Bearer ' + refreshKey }
    })
  }
}

