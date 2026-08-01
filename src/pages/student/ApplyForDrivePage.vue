<template>
  <div class="portal-card p-4 p-md-5">
    <h3 class="section-heading mb-2">Apply for Drive</h3>
    <p class="text-muted mb-4">Complete the application form and submit it for company review.</p>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>
    <div v-if="loading" class="text-center py-4"><div class="spinner-border text-primary"></div></div>
    <template v-else-if="drive">
      <div v-if="drive.already_applied" class="alert alert-info">
        You have already applied for this drive.
        <router-link to="/student/applications" class="fw-semibold ms-2">View Application</router-link>
      </div>
      <div v-else>
        <div class="portal-card bg-light p-3 mb-4 rounded-3">
          <div class="fw-semibold">{{ drive.title || drive.job_role }}</div>
          <small class="text-muted">{{ drive.company_name }} • {{ drive.package }} • {{ drive.openings }} openings</small>
          <p class="small mt-2 mb-0">{{ drive.eligibility }}</p>
        </div>
        <form class="row g-3" @submit.prevent="handleApply">
          <div class="col-12">
            <label class="form-label">Resume Upload</label>
            <div v-if="profileResume" class="alert alert-light border mb-2 d-flex align-items-center justify-content-between">
              <div>
                <i class="bi bi-file-earmark-pdf text-primary me-2 fs-5"></i>
                <span class="small">Default Profile Resume: <strong>{{ profileResume }}</strong></span>
              </div>
              <button type="button" class="btn btn-sm btn-outline-primary" @click="openResume(profileResume)">View</button>
            </div>
            <input type="file" accept=".pdf,.doc,.docx" class="form-control" @change="onFileChange" />
            <div class="form-text">
              <span v-if="resumeFile" class="text-success fw-medium">
                <i class="bi bi-check-circle me-1"></i>New resume selected: {{ resumeFile.name }}
              </span>
              <span v-else class="text-muted">
                Select a file to attach a specific resume for this application, or leave blank to submit your default profile resume.
              </span>
            </div>
          </div>
          <div class="col-12"><label class="form-label">Cover Note (optional)</label><textarea v-model="coverNote" class="form-control" rows="4" placeholder="Briefly describe why you're a great fit..."></textarea></div>
          <div class="col-12 d-grid">
            <button class="btn btn-primary" :disabled="submitting">
              <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
              {{ submitting ? 'Submitting...' : 'Submit Application' }}
            </button>
          </div>
        </form>
      </div>
    </template>
    <div v-else class="text-muted">Drive not found.</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { studentAPI } from '@/api/student'
import { openResume } from '@/utils/resume'

const route = useRoute()
const router = useRouter()
const drive = ref(null)
const coverNote = ref('')
const resumeFile = ref(null)
const profileResume = ref('')
const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const success = ref('')

function onFileChange(e) {
  resumeFile.value = e.target.files[0] || null
}

async function handleApply() {
  submitting.value = true
  error.value = ''
  try {
    await studentAPI.applyForDrive(drive.value.id, coverNote.value, resumeFile.value)
    success.value = 'Application submitted successfully!'
    setTimeout(() => router.push('/student/applications'), 1500)
  } catch (err) {
    error.value = err.response?.data?.error || 'Application failed.'
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  try {
    const [driveRes, profileRes] = await Promise.all([
      studentAPI.getDrive(route.params.id),
      studentAPI.getProfile()
    ])
    drive.value = driveRes.data.drive
    profileResume.value = profileRes.data.student?.resume_path || ''
  } catch (err) {
    error.value = 'Failed to load drive details.'
  } finally {
    loading.value = false
  }
})
</script>
