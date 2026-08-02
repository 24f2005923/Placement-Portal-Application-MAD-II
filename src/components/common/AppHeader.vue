<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NotificationsDropdown from './NotificationsDropdown.vue'
import UserProfileDropdown from './UserProfileDropdown.vue'

const emit = defineEmits(['toggle-sidebar'])
const route = useRoute()

const title = computed(() => {
  const path = route.path
  const map = [
    ['/admin/dashboard', 'Admin Dashboard'],
    ['/admin/students/', 'Student Profile'],
    ['/admin/students', 'Student Management'],
    ['/admin/companies/', 'Company Details'],
    ['/admin/companies', 'Company Management'],
    ['/admin/drives/', 'Drive Details'],
    ['/admin/drives', 'Placement Drive Management'],
    ['/admin/reports', 'Reports'],
    ['/admin/applications', 'Application Management'],
    ['/company/dashboard', 'Company Dashboard'],
    ['/company/register', 'Company Registration'],
    ['/company/profile', 'Company Profile'],
    ['/company/drives/create', 'Create Placement Drive'],
    ['/company/drives/', 'Edit Placement Drive'],
    ['/company/applications', 'View Applications'],
    ['/company/candidates', 'Shortlist Candidates'],
    ['/company/interviews', 'Schedule Interview'],
    ['/company/results', 'Publish Results'],
    ['/student/dashboard', 'Student Dashboard'],
    ['/student/register', 'Student Registration'],
    ['/student/profile', 'Profile Management'],
    ['/student/resume', 'Upload Resume'],
    ['/student/drives/', 'Apply for Drive'],
    ['/student/drives', 'View Placement Drives'],
    ['/student/applications', 'Track Application Status'],
    ['/student/history', 'Placement History'],
    ['/auth/login', 'Login']
  ]

  const match = map.find(([pattern]) => (pattern.endsWith('/') ? path.startsWith(pattern) : path === pattern))
  return match?.[1] ?? 'Dashboard'
})
</script>

<template>
  <header class="portal-topbar sticky-top px-3 px-lg-4 py-3">
    <div class="d-flex align-items-center justify-content-between gap-3">
      <div class="d-flex align-items-center gap-3">
        <button class="btn btn-primary d-lg-none" type="button" @click="emit('toggle-sidebar')">
          <i class="bi bi-list"></i>
        </button>
        <div>
          <div class="text-muted small">Placement Management System</div>
          <h4 class="mb-0 section-heading">{{ title }}</h4>
        </div>
      </div>

      <div class="d-flex align-items-center gap-2 gap-lg-3">
        <NotificationsDropdown />
        <UserProfileDropdown />
      </div>
    </div>
  </header>
</template>
