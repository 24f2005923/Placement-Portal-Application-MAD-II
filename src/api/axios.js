import axios from 'axios'

const API_SERVER_URL = 'http://localhost:5000'

// Create custom http request client
const httpClient = axios.create({
  baseURL: API_SERVER_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Attach Bearer Token to outgoing requests
httpClient.interceptors.request.use(function (requestConfig) {
  const jwtToken = localStorage.getItem('access_token')
  if (jwtToken) {
    requestConfig.headers['Authorization'] = 'Bearer ' + jwtToken
  }
  return requestConfig
})

// Handle token expiration & responses
httpClient.interceptors.response.use(
  function (successfulResponse) {
    return successfulResponse
  },
  async function (errorResponse) {
    const failedRequest = errorResponse.config

    const isUnauthorized = errorResponse.response && errorResponse.response.status === 401
    
    if (isUnauthorized && !failedRequest._retried) {
      failedRequest._retried = true

      const refreshKey = localStorage.getItem('refresh_token')
      if (refreshKey) {
        try {
          const authRefreshResponse = await axios.post(
            API_SERVER_URL + '/api/auth/refresh',
            {},
            { headers: { Authorization: 'Bearer ' + refreshKey } }
          )
          const newAccessToken = authRefreshResponse.data.access_token
          localStorage.setItem('access_token', newAccessToken)
          failedRequest.headers['Authorization'] = 'Bearer ' + newAccessToken
          return httpClient(failedRequest)
        } catch (refreshFailureError) {
          localStorage.clear()
          window.location.href = '/auth/login'
        }
      } else {
        localStorage.clear()
        window.location.href = '/auth/login'
      }
    }

    return Promise.reject(errorResponse)
  }
)

export default httpClient

