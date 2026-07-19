<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const user = computed(() => {
  try {
    return JSON.parse(localStorage.getItem('user') || '{}')
  } catch {
    return {}
  }
})

const initials = computed(() => {
  const name = user.value.name || ''
  return name.split(' ').slice(0, 2).map(n => n[0] || '').join('').toUpperCase() || 'U'
})

const profilePath = computed(() => {
  const role = user.value.role
  if (role === 'student') return '/student/profile'
  if (role === 'company') return '/company/profile'
  return null
})

function goToProfile() {
  if (profilePath.value) router.push(profilePath.value)
}
</script>

<template>
  <div class="dropdown">
    <button class="btn btn-light d-flex align-items-center gap-2 rounded-pill shadow-sm" data-bs-toggle="dropdown">
      <span class="avatar-circle">{{ initials }}</span>
      <span class="d-none d-md-inline fw-semibold">{{ user.name || 'User' }}</span>
      <i class="bi bi-chevron-down small"></i>
    </button>
    <div class="dropdown-menu dropdown-menu-end shadow border-0">
      <button v-if="profilePath" class="dropdown-item" @click="goToProfile">
        <i class="bi bi-person me-2"></i>Profile
      </button>
      <div class="dropdown-divider"></div>
      <router-link class="dropdown-item text-danger" to="/auth/login">
        <i class="bi bi-box-arrow-right me-2"></i>Logout
      </router-link>
    </div>
  </div>
</template>
