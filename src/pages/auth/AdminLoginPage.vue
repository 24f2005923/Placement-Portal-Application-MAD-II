<template>
  <div class="portal-card auth-card p-4 p-md-5">
    <div class="mb-4">
      <h2 class="fw-bold section-heading mb-1">Admin Login</h2>
      <p class="text-muted small mb-0">Restricted access - administrators only.</p>
    </div>

    <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>

    <form class="row g-3" @submit.prevent="handleLogin">
      <div class="col-12">
        <label class="form-label">Email Address</label>
        <input v-model="form.email" type="email" class="form-control form-control-lg" placeholder="admin@admin.com" required />
      </div>
      <div class="col-12">
        <label class="form-label">Password</label>
        <input v-model="form.password" type="password" class="form-control form-control-lg" placeholder="password" required />
      </div>
      <div class="col-12">
        <button type="submit" class="btn btn-danger btn-lg w-100" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? 'Signing in...' : 'Admin Login' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '@/api/auth'

const router = useRouter()
const form = ref({ email: '', password: '' })
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await authAPI.login(form.value.email, form.value.password)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    localStorage.setItem('user', JSON.stringify(data.user))

    if (data.user.role === 'admin') {
      router.push('/admin/dashboard')
    } else {
      localStorage.clear()
      error.value = 'Access denied. This portal is for admins only.'
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
