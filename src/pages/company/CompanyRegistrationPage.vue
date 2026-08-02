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
        <label class="form-label">Phone Number <span class="text-danger">*</span></label>
        <input
          v-model="form.phone"
          type="tel"
          class="form-control"
          :class="{ 'is-invalid': phoneTouched && phoneError }"
          placeholder="10-digit phone number (e.g. 9876543210)"
          maxlength="10"
          @input="onPhoneInput"
          @blur="phoneTouched = true"
          required
        />
        <div v-if="phoneTouched && phoneError" class="invalid-feedback d-block">{{ phoneError }}</div>
        <div v-else class="form-text">Must be exactly 10 numeric digits.</div>
      </div>
      <div class="col-md-6">
        <label class="form-label">Password <span class="text-danger">*</span></label>
        <input
          v-model="form.password"
          type="password"
          class="form-control"
          :class="{ 'is-invalid': passwordTouched && passwordError }"
          placeholder="••••••••"
          @blur="passwordTouched = true"
          required
        />
        <div v-if="passwordTouched && passwordError" class="invalid-feedback d-block">{{ passwordError }}</div>
      </div>
      <div class="col-md-6">
        <label class="form-label">City</label>
        <input v-model="form.city" class="form-control" placeholder="City" />
      </div>
      <div class="col-12">
        <label class="form-label">Address</label>
        <textarea v-model="form.address" class="form-control" rows="3" placeholder="Company headquarters address"></textarea>
      </div>

      <!-- Password Policy Requirements Checklist -->
      <div class="col-12 mt-2">
        <div class="p-3 bg-light rounded border">
          <small class="fw-semibold text-muted d-block mb-2">Password Policy Requirements:</small>
          <div class="d-flex flex-wrap gap-2">
            <span class="badge" :class="pwdCriteria.minLength ? 'bg-success' : 'bg-secondary'">
              <i :class="pwdCriteria.minLength ? 'bi bi-check-lg me-1' : 'bi bi-x-lg me-1'"></i> 8+ Characters
            </span>
            <span class="badge" :class="pwdCriteria.hasUppercase ? 'bg-success' : 'bg-secondary'">
              <i :class="pwdCriteria.hasUppercase ? 'bi bi-check-lg me-1' : 'bi bi-x-lg me-1'"></i> Uppercase (A-Z)
            </span>
            <span class="badge" :class="pwdCriteria.hasLowercase ? 'bg-success' : 'bg-secondary'">
              <i :class="pwdCriteria.hasLowercase ? 'bi bi-check-lg me-1' : 'bi bi-x-lg me-1'"></i> Lowercase (a-z)
            </span>
            <span class="badge" :class="pwdCriteria.hasNumber ? 'bg-success' : 'bg-secondary'">
              <i :class="pwdCriteria.hasNumber ? 'bi bi-check-lg me-1' : 'bi bi-x-lg me-1'"></i> Number (0-9)
            </span>
            <span class="badge" :class="pwdCriteria.hasSpecial ? 'bg-success' : 'bg-secondary'">
              <i :class="pwdCriteria.hasSpecial ? 'bi bi-check-lg me-1' : 'bi bi-x-lg me-1'"></i> Special (!@#$)
            </span>
          </div>
        </div>
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '@/api/auth'
import { getPhoneValidationError, getPasswordCriteria, getPasswordValidationError } from '@/utils/validators'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const success = ref('')
const phoneTouched = ref(false)
const passwordTouched = ref(false)

const form = ref({
  company_name: '',
  industry: '',
  email: '',
  phone: '',
  password: '',
  city: '',
  address: ''
})

const phoneError = computed(() => getPhoneValidationError(form.value.phone))
const pwdCriteria = computed(() => getPasswordCriteria(form.value.password))
const passwordError = computed(() => getPasswordValidationError(form.value.password))

function onPhoneInput(e) {
  // Enforce digits only and max 10 chars
  form.value.phone = e.target.value.replace(/\D/g, '').slice(0, 10)
  if (phoneTouched.value && !phoneError.value) {
    error.value = ''
  }
}

async function handleRegister() {
  phoneTouched.value = true
  passwordTouched.value = true
  error.value = ''
  success.value = ''

  // Client-side phone validation check
  const pErr = getPhoneValidationError(form.value.phone)
  if (pErr) {
    error.value = pErr
    return
  }

  // Client-side password validation check
  const pwdErr = getPasswordValidationError(form.value.password)
  if (pwdErr) {
    error.value = pwdErr
    return
  }

  // Basic required fields check
  if (!form.value.company_name || !form.value.email || !form.value.password) {
    error.value = 'Please fill in all required fields.'
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
