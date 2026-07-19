import api from './axios'

// auth api functions - login, register, logout

export const authAPI = {

  // login with email and password
  login: function (email, password) {
    return api.post('/api/auth/login', { email: email, password: password })
  },

  // register a new student
  registerStudent: function (studentData) {
    return api.post('/api/auth/register/student', studentData)
  },

  // register a new company
  registerCompany: function (companyData) {
    return api.post('/api/auth/register/company', companyData)
  },

  // logout current user
  logout: function () {
    return api.post('/api/auth/logout')
  },

  // get current logged in user info
  getCurrentUser: function () {
    return api.get('/api/auth/me')
  },

  // refresh access token using refresh token
  refreshToken: function () {
    const refreshToken = localStorage.getItem('refresh_token')
    return api.post('/api/auth/refresh', {}, {
      headers: { Authorization: 'Bearer ' + refreshToken }
    })
  }

}
