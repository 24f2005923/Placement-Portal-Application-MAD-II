<template>
  <div class="portal-card p-4 p-md-5">
    <h3 class="section-heading mb-2">Student Registration</h3>
    <p class="text-muted mb-4">Create your student profile to access placement features.</p>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>
    <form class="row g-3" @submit.prevent="handleRegister">
      <div class="col-md-6"><label class="form-label">Full Name</label><input v-model="form.name" class="form-control" required /></div>
      <div class="col-md-6"><label class="form-label">Roll Number</label><input v-model="form.register_number" class="form-control" required /></div>
      <div class="col-md-6"><label class="form-label">Email</label><input v-model="form.email" class="form-control" type="email" required /></div>
      <div class="col-md-6"><label class="form-label">Department</label><input v-model="form.department" class="form-control" required /></div>
      <div class="col-md-6"><label class="form-label">Password</label><input v-model="form.password" class="form-control" type="password" required /></div>
      <div class="col-md-6"><label class="form-label">CGPA</label><input v-model="form.cgpa" class="form-control" type="number" step="0.01" /></div>
      <div class="col-12 d-grid">
        <button class="btn btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? 'Registering...' : 'Register' }}
        </button>
      </div>
    </form>
    <div class="mt-3 text-center small">
      Already registered? <router-link to="/auth/login" class="fw-semibold">Login</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '@/api/auth'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const success = ref('')
const form = ref({ name: '', email: '', password: '', register_number: '', department: '', cgpa: '' })

async function handleRegister() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    await authAPI.registerStudent(form.value)
    success.value = 'Registration successful! Please login.'
    setTimeout(() => router.push('/auth/login'), 1500)
  } catch (err) {
    error.value = err.response?.data?.error || 'Registration failed.'
  } finally {
    loading.value = false
  }
}
</script>
