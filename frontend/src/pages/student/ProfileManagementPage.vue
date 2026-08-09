<template>
  <div class="row g-4">
    <div class="col-12 col-xl-8">
      <div class="portal-card p-4">
        <h3 class="section-heading mb-2">Profile Management</h3>
        <p class="text-muted mb-4">Update academic details, skills, contact information, and resume.</p>
        
        <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
          <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
          <button type="button" class="btn-close" @click="error = ''"></button>
        </div>
        <div v-if="success" class="alert alert-success alert-dismissible fade show" role="alert">
          <i class="bi bi-check-circle me-2"></i>{{ success }}
          <button type="button" class="btn-close" @click="success = ''"></button>
        </div>

        <div v-if="loading" class="text-center py-4"><div class="spinner-border text-primary"></div></div>
        <form v-else class="row g-3" @submit.prevent="handleSave">
          <div class="col-md-6"><label class="form-label">Full Name</label><input v-model="form.name" class="form-control" required /></div>
          <div class="col-md-6"><label class="form-label">Roll Number</label><input v-model="form.register_number" class="form-control" readonly /></div>
          <div class="col-md-6"><label class="form-label">Email</label><input v-model="form.email" class="form-control" type="email" /></div>
          <div class="col-md-6"><label class="form-label">CGPA</label><input v-model.number="form.cgpa" class="form-control" type="number" step="0.01" /></div>
          <div class="col-md-6"><label class="form-label">Phone</label><input v-model="form.phone" class="form-control" /></div>
          <div class="col-md-6"><label class="form-label">Department</label><input v-model="form.department" class="form-control" /></div>
          <div class="col-12"><label class="form-label">Skills (comma-separated)</label><input v-model="skillsInput" class="form-control" placeholder="Vue.js, Node.js, SQL" /></div>
          <div class="col-md-6"><label class="form-label">Preferred Role</label><input v-model="form.preferred_role" class="form-control" /></div>
          <div class="col-md-6"><label class="form-label">Graduation Year</label><input v-model.number="form.graduation_year" class="form-control" type="number" /></div>
          <div class="col-12 d-grid">
            <button class="btn btn-primary" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
              {{ saving ? 'Saving Profile...' : 'Save Profile' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Right Column: Profile Completeness & Resume Management -->
    <div class="col-12 col-xl-4 d-flex flex-column gap-4">
      <div class="portal-card p-4">
        <h5 class="section-heading mb-3">Profile Completeness</h5>
        <div class="progress mb-2" style="height: 10px;">
          <div class="progress-bar bg-success" :style="{ width: completeness + '%' }"></div>
        </div>
        <small class="text-muted">{{ completeness }}% complete</small>
        <div class="mt-4">
          <div class="small text-muted mb-1">Placement Status</div>
          <span class="badge badge-soft-primary px-3 py-2 fs-6">{{ form.placement_status || 'Not Placed' }}</span>
        </div>
      </div>

      <!-- Resume Management Card -->
      <div class="portal-card p-4">
        <h5 class="section-heading mb-2">Resume Management</h5>
        <p class="text-muted small mb-3">Manage your default profile resume for drive applications.</p>

        <div v-if="resumeSuccess" class="alert alert-success small py-2 mb-3">{{ resumeSuccess }}</div>
        <div v-if="resumeError" class="alert alert-danger small py-2 mb-3">{{ resumeError }}</div>

        <div v-if="currentResume" class="alert alert-light border mb-3">
          <div class="d-flex align-items-center justify-content-between">
            <div class="text-truncate me-2">
              <i class="bi bi-file-earmark-pdf text-danger fs-5 me-2"></i>
              <span class="fw-medium small text-truncate d-inline-block" style="max-width: 140px;" :title="currentResume">
                {{ currentResume }}
              </span>
            </div>
            <button type="button" class="btn btn-sm btn-outline-primary" @click="openResume(currentResume)">
              View
            </button>
          </div>
        </div>
        <div v-else class="text-muted small mb-3">No default resume uploaded yet.</div>

        <form @submit.prevent="handleUploadResume">
          <div class="mb-3">
            <label class="form-label small fw-semibold">Upload / Replace Resume</label>
            <input type="file" accept=".pdf,.doc,.docx" class="form-control form-control-sm" @change="onFileSelected" required />
            <div class="form-text extra-small">Formats: PDF, DOC, DOCX (Max 5MB)</div>
          </div>
          <button type="submit" class="btn btn-sm btn-outline-primary w-100" :disabled="uploading || !selectedFile">
            <span v-if="uploading" class="spinner-border spinner-border-sm me-1"></span>
            {{ uploading ? 'Uploading...' : 'Upload New Resume' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { studentAPI } from '@/api/student'
import { openResume } from '@/utils/resume'
import { isValidPhone, getNameValidationError } from '@/utils/validators'

const loading = ref(true)
const saving = ref(false)
const uploading = ref(false)
const error = ref('')
const success = ref('')
const resumeSuccess = ref('')
const resumeError = ref('')

const currentResume = ref('')
const selectedFile = ref(null)
const skillsInput = ref('')

const form = ref({
  name: '',
  email: '',
  register_number: '',
  cgpa: '',
  phone: '',
  department: '',
  preferred_role: '',
  graduation_year: '',
  placement_status: ''
})

const completeness = computed(() => {
  const fields = [form.value.name, form.value.email, form.value.cgpa, form.value.phone, form.value.department, skillsInput.value, form.value.preferred_role, form.value.graduation_year, currentResume.value]
  const filled = fields.filter(Boolean).length
  return Math.round((filled / fields.length) * 100)
})

function onFileSelected(e) {
  selectedFile.value = e.target.files[0] || null
}

async function handleUploadResume() {
  if (!selectedFile.value) return
  uploading.value = true
  resumeError.value = ''
  resumeSuccess.value = ''
  try {
    const { data } = await studentAPI.uploadResume(selectedFile.value)
    currentResume.value = data.resume_path
    resumeSuccess.value = 'Resume uploaded successfully.'
    selectedFile.value = null
    setTimeout(() => { resumeSuccess.value = '' }, 3000)
  } catch (err) {
    resumeError.value = err.response?.data?.error || 'Resume upload failed.'
  } finally {
    uploading.value = false
  }
}

async function handleSave() {
  saving.value = true
  error.value = ''
  success.value = ''

  const f = form.value

  if (f.name !== undefined) {
    const nameErr = getNameValidationError(f.name)
    if (nameErr) {
      error.value = nameErr
      saving.value = false
      return
    }
  }

  if (f.email && f.email.trim()) {
    const emailRegex = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/
    if (!emailRegex.test(f.email.trim())) {
      error.value = 'Please enter a valid email address.'
      saving.value = false
      return
    }
  }

  if (f.phone && f.phone.trim()) {
    if (!isValidPhone(f.phone)) {
      error.value = 'Phone number must be exactly 10 digits.'
      saving.value = false
      return
    }
  }

  if (f.cgpa !== '' && f.cgpa !== null && f.cgpa !== undefined) {
    const cgpaNum = parseFloat(f.cgpa)
    if (isNaN(cgpaNum) || cgpaNum < 0 || cgpaNum > 10) {
      error.value = 'CGPA must be a number between 0 and 10.'
      saving.value = false
      return
    }
  }

  if (f.graduation_year !== '' && f.graduation_year !== null && f.graduation_year !== undefined) {
    const yr = parseInt(f.graduation_year)
    if (isNaN(yr) || yr < 2000 || yr > 2100) {
      error.value = 'Graduation year must be a valid year (e.g. 2025).'
      saving.value = false
      return
    }
  }

  try {
    await studentAPI.updateProfile({ ...form.value, skills: skillsInput.value })
    success.value = 'Profile updated successfully.'
    setTimeout(() => { success.value = '' }, 3000)
  } catch (err) {
    error.value = err.response?.data?.error || 'Update failed.'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await studentAPI.getProfile()
    const s = data.student
    form.value = {
      name: s.name,
      email: s.email,
      register_number: s.register_number,
      cgpa: s.cgpa,
      phone: s.phone || '',
      department: s.department,
      preferred_role: s.preferred_role || '',
      graduation_year: s.graduation_year || '',
      placement_status: s.placement_status
    }
    currentResume.value = s.resume_path || ''
    skillsInput.value = (s.skills || []).join(', ')
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})
</script>
