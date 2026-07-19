import axios from 'axios'

// base url of our flask backend
const BASE_URL = 'http://localhost:5000'

// create axios instance with base url
const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// before every request, attach the jwt token from localStorage
api.interceptors.request.use(function (config) {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers['Authorization'] = 'Bearer ' + token
  }
  return config
})

// handle response errors globally
api.interceptors.response.use(
  function (response) {
    // if request was successful just return it
    return response
  },
  async function (error) {
    const originalRequest = error.config

    // if token expired (401), try to refresh it once
    if (error.response && error.response.status === 401 && !originalRequest._retried) {
      originalRequest._retried = true

      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const refreshResponse = await axios.post(
            BASE_URL + '/api/auth/refresh',
            {},
            { headers: { Authorization: 'Bearer ' + refreshToken } }
          )
          const newToken = refreshResponse.data.access_token
          localStorage.setItem('access_token', newToken)
          originalRequest.headers['Authorization'] = 'Bearer ' + newToken
          return api(originalRequest)
        } catch (refreshError) {
          // refresh also failed, clear storage and go to login
          localStorage.clear()
          window.location.href = '/auth/login'
        }
      } else {
        localStorage.clear()
        window.location.href = '/auth/login'
      }
    }

    return Promise.reject(error)
  }
)

export default api
