<template>
  <div class="portal-card p-4 p-md-5">
    <h3 class="section-heading mb-2">Company Registration</h3>
    <p class="text-muted mb-4">Submit company profile details for placement portal approval.</p>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>
    <form class="row g-3" @submit.prevent="handleRegister">
      <div class="col-md-6"><label class="form-label">Company Name</label><input v-model="form.company_name" class="form-control" placeholder="Company name" required /></div>
      <div class="col-md-6"><label class="form-label">Industry</label><input v-model="form.industry" class="form-control" placeholder="Industry" /></div>
      <div class="col-md-6"><label class="form-label">Email</label><input v-model="form.email" class="form-control" type="email" placeholder="hr@company.com" required /></div>
      <div class="col-md-6"><label class="form-label">Phone</label><input v-model="form.phone" class="form-control" placeholder="+91..." /></div>
      <div class="col-md-6"><label class="form-label">Password</label><input v-model="form.password" class="form-control" type="password" required /></div>
      <div class="col-md-6"><label class="form-label">City</label><input v-model="form.city" class="form-control" placeholder="City" /></div>
      <div class="col-12"><label class="form-label">Address</label><textarea v-model="form.address" class="form-control" rows="3"></textarea></div>
      <div class="col-12 d-grid">
        <button class="btn btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? 'Submitting...' : 'Submit Registration' }}
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
const form = ref({ company_name: '', industry: '', email: '', phone: '', password: '', city: '', address: '' })

async function handleRegister() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    await authAPI.registerCompany(form.value)
    success.value = 'Registration submitted! Awaiting admin approval.'
    setTimeout(() => router.push('/auth/login'), 2000)
  } catch (err) {
    error.value = err.response?.data?.error || 'Registration failed.'
  } finally {
    loading.value = false
  }
}
</script>
