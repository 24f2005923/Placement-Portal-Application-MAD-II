<template>
  <div class="row g-4">
    <div class="col-12 col-xl-5">
      <div class="portal-card p-4">
        <h3 class="section-heading mb-2">Schedule Interview</h3>
        <p class="text-muted mb-4">Create interview slots exclusively for shortlisted candidates.</p>

        <FeedbackAlert 
          :success="successMsg"
          :error="errorMsg"
          @clear-success="clearMessages"
          @clear-error="clearMessages"
        />

        <div v-if="!fetchingApps && !fetchError && shortlisted.length === 0" class="alert alert-warning mb-3">
          <i class="bi bi-info-circle me-2"></i>
          No shortlisted candidates available. Please shortlist candidates from
          <router-link to="/company/applications" class="fw-bold alert-link">View Applications</router-link> before scheduling an interview.
        </div>

        <form class="row g-3" @submit.prevent="handleSchedule">
          <div class="col-12">
            <label class="form-label fw-semibold">Select Shortlisted Candidate</label>
            <select v-model="form.application_id" class="form-select" required :disabled="shortlisted.length === 0">
              <option value="">— Choose shortlisted applicant —</option>
              <option v-for="app in shortlisted" :key="app.id" :value="app.id">
                {{ app.student_name }} — {{ app.drive_title }} ({{ app.application_status }})
              </option>
            </select>
          </div>
          <div class="col-12">
            <label class="form-label">Interview Round</label>
            <input v-model="form.round_name" class="form-control" placeholder="Technical Round 1" required />
          </div>
          <div class="col-md-6">
            <label class="form-label">Date</label>
            <input v-model="form.interview_date" class="form-control" type="date" required />
          </div>
          <div class="col-md-6">
            <label class="form-label">Time</label>
            <input v-model="form.interview_time" class="form-control" type="time" required />
          </div>
          <div class="col-12">
            <label class="form-label">Mode</label>
            <select v-model="form.interview_mode" class="form-select">
              <option value="online">Online</option>
              <option value="offline">Offline</option>
            </select>
          </div>
          <div class="col-12">
            <label class="form-label">Interview Link / Location (optional)</label>
            <input v-model="form.interview_link" class="form-control" placeholder="https://meet.google.com/..." />
          </div>
          <div class="col-12 d-grid">
            <button class="btn btn-primary" :disabled="loading || shortlisted.length === 0">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              {{ loading ? 'Scheduling...' : 'Schedule Interview' }}
            </button>
          </div>
        </form>
      </div>
    </div>
    <div class="col-12 col-xl-7">
      <div class="portal-card p-4">
        <h5 class="section-heading mb-3">Upcoming Scheduled Interviews</h5>
        <div v-if="interviews.length === 0" class="border rounded-4 p-4 text-center text-muted">
          No interviews scheduled yet.
        </div>
        <div v-else class="list-group">
          <div v-for="iv in interviews" :key="iv.id" class="list-group-item p-3">
            <div class="d-flex justify-content-between align-items-start">
              <div>
                <div class="fw-semibold text-primary fs-6">{{ iv.student_name }}</div>
                <div class="small text-muted">{{ iv.drive_title }} — <span class="fw-medium text-dark">{{ iv.round_name || 'Interview Round' }}</span></div>
                <div class="small mt-1 text-secondary">
                  <i class="bi bi-calendar-event me-1"></i>{{ iv.interview_date }}
                  <i class="bi bi-clock ms-2 me-1"></i>{{ iv.interview_time || 'TBD' }}
                  <span class="badge badge-soft-info ms-2 text-capitalize">{{ iv.interview_mode }}</span>
                </div>
                <div v-if="iv.interview_link" class="small mt-1">
                  <a :href="iv.interview_link" target="_blank" class="text-decoration-none"><i class="bi bi-link-45deg me-1"></i>Meeting Link</a>
                </div>
                <div class="mt-2">
                  <button class="btn btn-sm btn-outline-primary" @click="sendEmail(iv.id)" :disabled="sendingEmailId === iv.id">
                    <span v-if="sendingEmailId === iv.id" class="spinner-border spinner-border-sm me-1"></span>
                    <i v-else class="bi bi-envelope me-1"></i>Email Reminder
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { companyAPI } from '@/api/company'
import FeedbackAlert from '@/components/common/FeedbackAlert.vue'
import { usePageFeedback } from '@/composables/usePageFeedback'

const { successMsg, errorMsg, showSuccess, showError, clearMessages } = usePageFeedback()

const shortlisted = ref([])
const interviews = ref([])
const loading = ref(false)
const fetchingApps = ref(true)
const fetchError = ref(false)
const sendingEmailId = ref(null)
const form = ref({ application_id: '', round_name: '', interview_date: '', interview_time: '', interview_mode: 'online', interview_link: '' })

async function handleSchedule() {
  loading.value = true
  clearMessages()
  try {
    const res = await companyAPI.scheduleInterview(form.value)
    showSuccess(`Interview scheduled for ${res.data.interview.student_name}. Notifications sent.`)
    form.value = { application_id: '', round_name: '', interview_date: '', interview_time: '', interview_mode: 'online', interview_link: '' }
    await fetchShortlisted()
    await fetchInterviews()
  } catch (err) {
    showError(err.response?.data?.error || 'Failed to schedule interview.')
  } finally {
    loading.value = false
  }
}

async function fetchShortlisted() {
  fetchingApps.value = true
  fetchError.value = false
  try {
    const { data } = await companyAPI.getApplications({ status: 'shortlisted' })
    shortlisted.value = data.applications || []
  } catch (err) {
    console.error('Fetch shortlisted error:', err)
    fetchError.value = true
    shortlisted.value = []
  } finally {
    fetchingApps.value = false
  }
}

async function fetchInterviews() {
  try {
    const { data } = await companyAPI.getInterviews()
    interviews.value = data.interviews || []
  } catch (err) {
    console.error('Fetch interviews error:', err)
  }
}

async function sendEmail(interviewId) {
  sendingEmailId.value = interviewId
  error.value = ''
  success.value = ''
  try {
    const { data } = await companyAPI.sendInterviewEmail(interviewId)
    success.value = data.message || 'Email sent successfully.'
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to send email.'
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } finally {
    sendingEmailId.value = null
  }
}

onMounted(async () => {
  await Promise.all([fetchShortlisted(), fetchInterviews()])
})
</script>
