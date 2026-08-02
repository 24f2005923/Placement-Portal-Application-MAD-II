import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('@/pages/public/LandingPage.vue') },
  {
    path: '/auth',
    component: () => import('@/layouts/PublicLayout.vue'),
    children: [
      { path: '', redirect: 'login' },
      { path: 'login', component: () => import('@/pages/auth/LoginPage.vue') },
      { path: 'adminlogin', component: () => import('@/pages/auth/AdminLoginPage.vue') }
    ]
  },
  {
    path: '/student/register',
    component: () => import('@/layouts/PublicLayout.vue'),
    children: [
      { path: '', component: () => import('@/pages/student/StudentRegistrationPage.vue') }
    ]
  },
  {
    path: '/company/register',
    component: () => import('@/layouts/PublicLayout.vue'),
    children: [
      { path: '', component: () => import('@/pages/company/CompanyRegistrationPage.vue') }
    ]
  },
  {
    path: '/admin',
    component: () => import('@/layouts/DashboardLayout.vue'),
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      { path: '', redirect: 'dashboard' },
      { path: 'dashboard', component: () => import('@/pages/admin/AdminDashboard.vue') },
      { path: 'students', component: () => import('@/pages/admin/StudentsPage.vue') },
      { path: 'students/:id', component: () => import('@/pages/admin/StudentProfilePage.vue') },
      { path: 'companies', component: () => import('@/pages/admin/CompaniesPage.vue') },
      { path: 'companies/:id', component: () => import('@/pages/admin/CompanyDetailsPage.vue') },
      { path: 'drives', component: () => import('@/pages/admin/PlacementDrivesPage.vue') },
      { path: 'drives/:id', component: () => import('@/pages/admin/DriveDetailsPage.vue') },
      { path: 'reports', component: () => import('@/pages/admin/ReportsPage.vue') },
      { path: 'applications', component: () => import('@/pages/admin/ManageApplicationsPage.vue') }
    ]
  },
  {
    path: '/company',
    component: () => import('@/layouts/DashboardLayout.vue'),
    meta: { requiresAuth: true, role: 'company' },
    children: [
      { path: '', redirect: 'dashboard' },
      { path: 'dashboard', component: () => import('@/pages/company/CompanyDashboard.vue') },
      { path: 'profile', component: () => import('@/pages/company/CompanyProfilePage.vue') },
      { path: 'drives', redirect: 'drives/create' },
      { path: 'drives/create', component: () => import('@/pages/company/CreatePlacementDrivePage.vue') },
      { path: 'drives/:id/edit', component: () => import('@/pages/company/EditPlacementDrivePage.vue') },
      { path: 'applications', component: () => import('@/pages/company/ViewApplicationsPage.vue') },
      { path: 'candidates', component: () => import('@/pages/company/ShortlistCandidatesPage.vue') },
      { path: 'interviews', component: () => import('@/pages/company/ScheduleInterviewPage.vue') },
      { path: 'results', component: () => import('@/pages/company/PublishResultsPage.vue') }
    ]
  },
  {
    path: '/student',
    component: () => import('@/layouts/DashboardLayout.vue'),
    meta: { requiresAuth: true, role: 'student' },
    children: [
      { path: '', redirect: 'dashboard' },
      { path: 'dashboard', component: () => import('@/pages/student/StudentDashboard.vue') },
      { path: 'profile', component: () => import('@/pages/student/ProfileManagementPage.vue') },
      { path: 'resume', component: () => import('@/pages/student/UploadResumePage.vue') },
      { path: 'drives', component: () => import('@/pages/student/ViewPlacementDrivesPage.vue') },
      { path: 'drives/:id/apply', component: () => import('@/pages/student/ApplyForDrivePage.vue') },
      { path: 'applications', component: () => import('@/pages/student/TrackApplicationStatusPage.vue') },
      { path: 'history', component: () => import('@/pages/student/PlacementHistoryPage.vue') }
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/auth/login' }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(r => r.meta.requiresAuth)
  const requiredRole = to.matched.find(r => r.meta.role)?.meta.role

  if (!requiresAuth) return next()

  const token = localStorage.getItem('access_token')
  if (!token) return next('/auth/login')

  if (requiredRole) {
    try {
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      if (user.role !== requiredRole) {
        const roleRedirect = { admin: '/admin/dashboard', company: '/company/dashboard', student: '/student/dashboard' }
        return next(roleRedirect[user.role] || '/auth/login')
      }
    } catch {
      localStorage.clear()
      return next('/auth/login')
    }
  }

  next()
})

export default router
