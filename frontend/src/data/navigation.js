export const adminNav = [
  { label: 'Dashboard', icon: 'bi-grid', to: '/admin/dashboard' },
  { label: 'Students', icon: 'bi-people', to: '/admin/students' },
  { label: 'Companies', icon: 'bi-buildings', to: '/admin/companies' },
  { label: 'Placement Drives', icon: 'bi-megaphone', to: '/admin/drives' },
  { label: 'Reports', icon: 'bi-bar-chart', to: '/admin/reports' },
  { label: 'Applications', icon: 'bi-file-earmark-text', to: '/admin/applications' },
  { label: 'Logout', icon: 'bi-box-arrow-right', to: '/auth/login' }
]

export const companyNav = [
  { label: 'Dashboard', icon: 'bi-grid', to: '/company/dashboard' },
  { label: 'Placement Drives', icon: 'bi-megaphone', to: '/company/drives/create' },
  { label: 'Applications', icon: 'bi-inbox', to: '/company/applications' },
  { label: 'Interviews', icon: 'bi-calendar-event', to: '/company/interviews' },
  { label: 'Results', icon: 'bi-trophy', to: '/company/results' },
  { label: 'Profile', icon: 'bi-person-badge', to: '/company/profile' },
  { label: 'Logout', icon: 'bi-box-arrow-right', to: '/auth/login' }
]

export const studentNav = [
  { label: 'Dashboard', icon: 'bi-grid', to: '/student/dashboard' },
  { label: 'My Profile', icon: 'bi-person', to: '/student/profile' },
  { label: 'Placement Drives', icon: 'bi-briefcase', to: '/student/drives' },
  { label: 'Applications', icon: 'bi-send-check', to: '/student/applications' },
  { label: 'Placement History', icon: 'bi-clock-history', to: '/student/history' },
  { label: 'Logout', icon: 'bi-box-arrow-right', to: '/auth/login' }
]
