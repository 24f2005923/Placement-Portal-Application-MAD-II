<template>
  <div class="portal-card p-4">
    <h3 class="section-heading mb-2">Shortlist Candidates</h3>
    <p class="text-muted mb-4">Review applications and promote candidates to the interview round.</p>
    <div v-if="msg" class="alert alert-success">{{ msg }}</div>
    <div v-if="loading" class="text-center py-4"><div class="spinner-border text-primary"></div></div>
    <div v-else class="row g-3">
      <div v-for="app in applications" :key="app.id" class="col-md-6">
        <div class="border rounded-4 p-3 h-100">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <div class="fw-semibold">{{ app.student_name }}</div>
              <small class="text-muted">{{ app.drive_title }}</small>
              <div class="mt-2 d-flex align-items-center gap-2">
                <span class="badge rounded-pill"
                  :class="app.application_status === 'shortlisted' ? 'badge-soft-success' : 'badge-soft-primary'">
                  {{ app.application_status }}
                </span>
                <button v-if="app.resume_path || app.student_resume_path"
                  class="btn btn-sm btn-outline-info py-0 px-2"
                  @click="openResume(app.resume_path || app.student_resume_path)">
                  <i class="bi bi-file-earmark-pdf me-1"></i>Resume
                </button>
              </div>
            </div>
            <button class="btn btn-sm btn-outline-primary"
              :disabled="app.application_status !== 'applied'"
              @click="shortlist(app)">
              {{ app.application_status === 'shortlisted' ? 'Shortlisted' : 'Shortlist' }}
            </button>
          </div>
        </div>
      </div>
      <p v-if="!applications.length" class="text-muted text-center py-3">No pending applications.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { companyAPI } from '@/api/company'
import { openResume } from '@/utils/resume'

const applications = ref([])
const loading = ref(false)
const msg = ref('')

async function fetchApplications() {
  loading.value = true
  try {
    const { data } = await companyAPI.getApplications({ status: 'applied' })
    applications.value = data.applications
  } catch (err) { console.error(err) } finally { loading.value = false }
}

async function shortlist(app) {
  try {
    await companyAPI.shortlistApplication(app.id)
    app.application_status = 'shortlisted'
    msg.value = `${app.student_name} has been shortlisted.`
    setTimeout(() => { msg.value = '' }, 3000)
  } catch (err) { console.error(err) }
}

onMounted(fetchApplications)
</script>
