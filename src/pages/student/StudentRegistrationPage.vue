<template>
  <div class="portal-card p-4 p-md-5">
    <h3 class="section-heading mb-2">Student Registration</h3>
    <p class="text-muted mb-4">Create your student profile to access placement features.</p>
    <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
    <div v-if="success" class="alert alert-success" role="alert">{{ success }}</div>
    <form class="row g-3" @submit.prevent="handleRegister" novalidate>
      <div class="col-md-6">
        <label class="form-label">Full Name <span class="text-danger">*</span></label>
        <input v-model="form.name" class="form-control" placeholder="John Doe" required />
      </div>
      <div class="col-md-6">
        <label class="form-label">Roll / Register Number <span class="text-danger">*</span></label>
        <input v-model="form.register_number" class="form-control" placeholder="21CS001" required />
      </div>
      <div class="col-md-6">
        <label class="form-label">Email <span class="text-danger">*</span></label>
        <input v-model="form.email" class="form-control" type="email" placeholder="student@college.edu" required />
      </div>
      <div class="col-md-6">
        <label class="form-label">Department <span class="text-danger">*</span></label>
        <input v-model="form.department" class="form-control" placeholder="Computer Science" required />
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
        <label class="form-label">CGPA</label>
        <input v-model="form.cgpa" class="form-control" type="number" step="0.01" min="0" max="10" placeholder="8.50" />
      </div>

      <!-- Password Strength Policy Checklist -->
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '@/api/auth'
import { getPasswordCriteria, getPasswordValidationError } from '@/utils/validators'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const success = ref('')
const passwordTouched = ref(false)

const form = ref({
  name: '',
  email: '',
  password: '',
  register_number: '',
  department: '',
  cgpa: ''
})

const pwdCriteria = computed(() => getPasswordCriteria(form.value.password))
const passwordError = computed(() => getPasswordValidationError(form.value.password))

async function handleRegister() {
  passwordTouched.value = true
  error.value = ''
  success.value = ''

  const pwdErr = getPasswordValidationError(form.value.password)
  if (pwdErr) {
    error.value = pwdErr
    return
  }

  if (!form.value.name || !form.value.register_number || !form.value.email || !form.value.department) {
    error.value = 'Please fill in all required fields.'
    return
  }

  loading.value = true
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
