<template>
  <div class="portal-card p-4 p-md-5">
    <h3 class="section-heading mb-2">Company Registration</h3>
    <p class="text-muted mb-4">Submit company profile details for placement portal approval.</p>
    <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
    <div v-if="success" class="alert alert-success" role="alert">{{ success }}</div>
    <form class="row g-3" @submit.prevent="handleRegister" novalidate>
      <div class="col-md-6">
        <label class="form-label">Company Name <span class="text-danger">*</span></label>
        <input v-model="form.company_name" class="form-control" placeholder="Company name" required />
      </div>
      <div class="col-md-6">
        <label class="form-label">Industry</label>
        <input v-model="form.industry" class="form-control" placeholder="e.g. Information Technology" />
      </div>
      <div class="col-md-6">
        <label class="form-label">Email <span class="text-danger">*</span></label>
        <input v-model="form.email" class="form-control" type="email" placeholder="hr@company.com" required />
      </div>
      <div class="col-md-6">
        <label class="form-label">Phone Number</label>
        <input
          v-model="form.phone"
          type="tel"
          class="form-control"
          placeholder="10-digit phone number"
          maxlength="10"
          @input="onPhoneInput"
        />
      </div>
      <div class="col-md-6">
        <label class="form-label">Password <span class="text-danger">*</span></label>
        <input
          v-model="form.password"
          type="password"
          class="form-control"
          placeholder="••••••••"
          required
        />
      </div>
      <div class="col-md-6">
        <label class="form-label">City</label>
        <input v-model="form.city" class="form-control" placeholder="City" />
      </div>
      <div class="col-12">
        <label class="form-label">Address</label>
        <textarea v-model="form.address" class="form-control" rows="3" placeholder="Company headquarters address"></textarea>
      </div>

      <div class="col-12 d-grid mt-3">
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
import { getPasswordValidationError } from '@/utils/validators'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const success = ref('')

const form = ref({
  company_name: '',
  industry: '',
  email: '',
  phone: '',
  password: '',
  city: '',
  address: ''
})

function onPhoneInput(e) {
  form.value.phone = e.target.value.replace(/\D/g, '').slice(0, 10)
}

async function handleRegister() {
  error.value = ''
  success.value = ''

  const f = form.value

  if (!f.company_name.trim() || !f.email.trim() || !f.password) {
    error.value = 'Please fill in all required fields.'
    return
  }

  if (f.company_name.trim().length < 2) {
    error.value = 'Company name must be at least 2 characters.'
    return
  }

  const emailRegex = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/
  if (!emailRegex.test(f.email.trim())) {
    error.value = 'Please enter a valid email address.'
    return
  }

  const pwdError = getPasswordValidationError(f.password)
  if (pwdError) {
    error.value = pwdError
    return
  }

  loading.value = true
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

