import httpClient from './axios'

export function get(path, params) {
  return httpClient.get(path, { params: params || {} })
}

export function post(path, payload, config) {
  return httpClient.post(path, payload || {}, config)
}

export function put(path, payload, config) {
  return httpClient.put(path, payload || {}, config)
}

export function del(path, config) {
  return httpClient.delete(path, config)
}

export function multipartPost(path, formData) {
  return httpClient.post(path, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export function buildPath(basePath, id, suffix = '') {
  return `${basePath}/${id}${suffix}`
}
