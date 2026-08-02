<template>
  <div class="portal-card auth-card p-4 p-md-5">
    <div class="mb-4 text-center">
      <h2 class="fw-bold section-heading mb-1">Welcome Back</h2>
      <p class="text-muted small mb-0">Sign in to your account</p>
    </div>

    <div class="d-flex rounded-3 overflow-hidden border mb-4">
      <button
        class="btn w-50 rounded-0 py-2 fw-semibold"
        :class="activeTab === 'student' ? 'btn-primary' : 'btn-light text-muted'"
        @click="activeTab = 'student'"
        type="button"
      >
        Student
      </button>
      <button
        class="btn w-50 rounded-0 py-2 fw-semibold"
        :class="activeTab === 'company' ? 'btn-primary' : 'btn-light text-muted'"
        @click="activeTab = 'company'"
        type="button"
      >
        Company
      </button>
    </div>

    <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>

    <form class="row g-3" @submit.prevent="handleLogin">
      <div class="col-12">
        <label class="form-label">{{ activeTab === 'student' ? 'Email Address or Register Number' : 'Email Address' }}</label>
        <input
          v-model="form.email"
          :type="activeTab === 'student' ? 'text' : 'email'"
          class="form-control form-control-lg"
          :placeholder="activeTab === 'student' ? 'student@university.edu or REG123' : 'hr@company.com'"
          required
        />
      </div>
      <div class="col-12">
        <label class="form-label">Password</label>
        <input v-model="form.password" type="password" class="form-control form-control-lg" placeholder="••••••••" required />
      </div>
      <div class="col-12">
        <button type="submit" class="btn btn-primary btn-lg w-100" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? 'Signing in...' : `Login as ${activeTab === 'student' ? 'Student' : 'Company'}` }}
        </button>
      </div>
    </form>

    <div class="mt-4 text-center small text-muted">
      <template v-if="activeTab === 'student'">
        New student?
        <router-link to="/student/register" class="fw-semibold">Register here</router-link>
      </template>
      <template v-else>
        New company?
        <router-link to="/company/register" class="fw-semibold">Register here</router-link>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authAPI } from '@/api/auth'

const router = useRouter()
const route = useRoute()
const activeTab = ref(route.query.role === 'company' ? 'company' : 'student')
const form = ref({ email: '', password: '' })
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await authAPI.login(form.value.email, form.value.password, activeTab.value)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    localStorage.setItem('user', JSON.stringify(data.user))

    const role = data.user.role
    if (role === 'admin') {
      router.push('/admin/dashboard')
    } else if (role === 'company') {
      router.push('/company/dashboard')
    } else {
      router.push('/student/dashboard')
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
