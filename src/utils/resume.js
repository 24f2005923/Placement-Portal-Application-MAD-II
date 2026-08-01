export function getResumeUrl(filename) {
  if (!filename) return '#'
  const token = localStorage.getItem('access_token') || ''
  return `http://localhost:5000/api/student/resume/${filename}?token=${token}`
}

export function openResume(filename) {
  if (!filename) return
  const url = getResumeUrl(filename)
  window.open(url, '_blank')
}
