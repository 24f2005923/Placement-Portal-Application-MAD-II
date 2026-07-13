<template>
  <div class="row g-4">
    <div class="col-12 col-xl-5">
      <div class="portal-card p-4">
        <h3 class="section-heading mb-2">Schedule Interview</h3>
        <p class="text-muted mb-4">Create interview slots for shortlisted candidates.</p>
        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        <div v-if="success" class="alert alert-success">{{ success }}</div>
        <form class="row g-3" @submit.prevent="handleSchedule">
          <div class="col-12">
            <label class="form-label">Select Candidate</label>
            <select v-model="form.application_id" class="form-select" required>
              <option value="">— Choose applicant —</option>
              <option v-for="app in shortlisted" :key="app.id" :value="app.id">
                {{ app.student_name }} — {{ app.drive_title }}
              </option>
            </select>
          </div>
          <div class="col-12"><label class="form-label">Interview Round</label><input v-model="form.round_name" class="form-control" placeholder="Technical Round 1" /></div>
          <div class="col-md-6"><label class="form-label">Date</label><input v-model="form.interview_date" class="form-control" type="date" required /></div>
          <div class="col-md-6"><label class="form-label">Time</label><input v-model="form.interview_time" class="form-control" type="time" /></div>
          <div class="col-12">
            <label class="form-label">Mode</label>
            <select v-model="form.interview_mode" class="form-select">
              <option value="online">Online</option>
              <option value="offline">Offline</option>
            </select>
          </div>
          <div class="col-12"><label class="form-label">Interview Link (optional)</label><input v-model="form.interview_link" class="form-control" placeholder="https://meet.google.com/..." /></div>
          <div class="col-12 d-grid">
            <button class="btn btn-primary" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              {{ loading ? 'Scheduling...' : 'Schedule' }}
            </button>
          </div>
        </form>
      </div>
    </div>
    <div class="col-12 col-xl-7">
      <div class="portal-card p-4">
        <h5 class="section-heading mb-3">Upcoming Interviews</h5>
        <div v-if="interviews.length === 0" class="border rounded-4 p-4 text-center text-muted">No interviews scheduled yet.</div>
        <div v-else class="list-group">
          <div v-for="iv in interviews" :key="iv.id" class="list-group-item">
            <div class="fw-semibold">{{ iv.student_name }}</div>
            <small class="text-muted">{{ iv.drive_title }} — {{ iv.round_name }}</small>
            <div class="small mt-1">{{ iv.interview_date }} {{ iv.interview_time }} ({{ iv.interview_mode }})</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { companyAPI } from '@/api/company'

const shortlisted = ref([])
const interviews = ref([])
const loading = ref(false)
const error = ref('')
const success = ref('')
const form = ref({ application_id: '', round_name: '', interview_date: '', interview_time: '', interview_mode: 'online', interview_link: '' })

async function handleSchedule() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    await companyAPI.scheduleInterview(form.value)
    success.value = 'Interview scheduled successfully.'
    form.value = { application_id: '', round_name: '', interview_date: '', interview_time: '', interview_mode: 'online', interview_link: '' }
    await fetchInterviews()
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to schedule interview.'
  } finally {
    loading.value = false
  }
}

async function fetchInterviews() {
  const { data } = await companyAPI.getInterviews()
  interviews.value = data.interviews
}

onMounted(async () => {
  try {
    const [appsRes] = await Promise.all([companyAPI.getApplications({ status: 'shortlisted' })])
    shortlisted.value = appsRes.data.applications
    await fetchInterviews()
  } catch (err) { console.error(err) }
})
</script>
