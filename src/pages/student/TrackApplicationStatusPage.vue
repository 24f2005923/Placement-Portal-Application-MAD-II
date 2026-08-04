<template>
  <div class="portal-card p-4 p-md-5">
    <!-- Header -->
    <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center mb-4 pb-3 border-bottom gap-3">
      <div>
        <h3 class="section-heading mb-1">Application History & Status Tracking</h3>
        <p class="text-muted mb-0">View all submitted placement applications, interview schedules, feedback, and downloadable documents.</p>
      </div>
      <div class="d-flex align-items-center gap-2 flex-wrap">
        <button
          class="btn btn-outline-primary rounded-pill px-3"
          :disabled="exporting"
          @click="handleExportApplications"
        >
          <span v-if="exporting" class="spinner-border spinner-border-sm me-1"></span>
          <i v-else class="bi bi-download me-1"></i>{{ exporting ? exportStatus : 'Export CSV' }}
        </button>
        <router-link to="/student/drives" class="btn btn-primary rounded-pill px-4">
          <i class="bi bi-briefcase me-2"></i>Browse Drives
        </router-link>
      </div>
    </div>

    <!-- Feedback Alerts -->
    <FeedbackAlert 
      :success="successMsg"
      :error="errorMsg"
      @clear-success="clearMessages"
      @clear-error="clearMessages"
    />

    <!-- Summary Quick Stats -->
    <div class="row g-3 mb-4" v-if="!loading && applications.length > 0">
      <div class="col-6 col-md-3">
        <div class="p-3 bg-light rounded-4 border text-center">
          <div class="text-muted small">Total Applied</div>
          <div class="fs-4 fw-bold text-dark">{{ statsCount.total }}</div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="p-3 bg-light rounded-4 border text-center">
          <div class="text-muted small">Shortlisted</div>
          <div class="fs-4 fw-bold text-warning">{{ statsCount.shortlisted }}</div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="p-3 bg-light rounded-4 border text-center">
          <div class="text-muted small">Interviews</div>
          <div class="fs-4 fw-bold text-info">{{ statsCount.interviews }}</div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="p-3 bg-light rounded-4 border text-center">
          <div class="text-muted small">Offers Received</div>
          <div class="fs-4 fw-bold text-success">{{ statsCount.selected }}</div>
        </div>
      </div>
    </div>

    <!-- Filter & Search Controls -->
    <div class="row g-3 mb-4 align-items-center">
      <div class="col-12 col-md-6 col-lg-7">
        <div class="input-group">
          <span class="input-group-text bg-white border-end-0"><i class="bi bi-search text-muted"></i></span>
          <input
            v-model="searchQuery"
            type="search"
            class="form-control border-start-0 ps-0"
            placeholder="Search application history by company name or job role..."
          />
        </div>
      </div>
      <div class="col-12 col-md-6 col-lg-5">
        <div class="btn-group w-100 btn-group-sm" role="group">
          <button
            v-for="status in statusOptions"
            :key="status.value"
            type="button"
            class="btn"
            :class="selectedStatus === status.value ? 'btn-primary' : 'btn-outline-secondary'"
            @click="selectedStatus = status.value"
          >
            {{ status.label }}
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <LoadingSpinner v-if="loading" message="Loading application history..." />

    <!-- Empty State -->
    <EmptyState 
      v-else-if="filteredApplications.length === 0" 
      title="No Applications Found"
      :message="searchQuery || selectedStatus !== 'all' ? 'No applications match your filter criteria.' : 'You have not submitted any placement drive applications yet.'"
      icon="bi-journal-x"
      actionLabel="Explore Placement Drives"
      actionTo="/student/drives"
    />

    <!-- Application History Table -->
    <div v-else class="table-responsive">
      <table class="table align-middle table-hover border">
        <thead class="table-light">
          <tr>
            <th>Company & Job Role</th>
            <th>Applied Date</th>
            <th>Status & Stage</th>
            <th>Interview Details & Feedback</th>
            <th class="text-center">Downloadable Documents</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="app in filteredApplications" :key="app.id">
            <!-- Company & Job Role -->
            <td>
              <div class="fw-bold text-primary fs-6">{{ app.company_name }}</div>
              <div class="fw-medium text-dark">{{ app.drive_title || app.drive_role }}</div>
              <small class="text-muted d-block">{{ app.drive_role }} • <span class="text-success fw-semibold">{{ app.drive_package || 'N/A' }}</span></small>
            </td>

            <!-- Applied Date -->
            <td>
              <div class="small fw-medium text-dark">
                <i class="bi bi-calendar-event me-1 text-muted"></i>{{ app.applied_at || 'Recent' }}
              </div>
            </td>

            <!-- Status & Stage -->
            <td>
              <div class="mb-1">
                <StatusBadge variant="application" :status="app.application_status" class="fs-7" />
              </div>
              <small class="text-muted d-block">Stage: <strong>{{ app.stage }}</strong></small>
              <div class="progress mt-2" style="height: 6px; width: 110px;">
                <div
                  class="progress-bar"
                  :class="app.application_status === 'selected' ? 'bg-success' : app.application_status === 'rejected' ? 'bg-danger' : 'bg-primary'"
                  :style="{ width: app.progress + '%' }"
                ></div>
              </div>
            </td>

            <!-- Interview Details & Feedback -->
            <td style="max-width: 280px;">
              <!-- Interview Scheduled Box -->
              <div v-if="app.interview" class="small mb-2 bg-light border p-2 rounded-3">
                <div class="fw-semibold text-primary mb-1">
                  <i class="bi bi-camera-video me-1"></i>{{ app.interview.round_name || 'Interview Round' }}
                </div>
                <div class="text-secondary">
                  <i class="bi bi-calendar3 me-1"></i>{{ app.interview.interview_date }} {{ app.interview.interview_time || '' }}
                  <span class="badge badge-soft-info ms-1 text-capitalize">{{ app.interview.interview_mode }}</span>
                </div>
                <div v-if="app.interview.interview_link" class="mt-1">
                  <a :href="app.interview.interview_link" target="_blank" class="fw-semibold text-decoration-none">
                    <i class="bi bi-link-45deg me-1"></i>Join Interview Link
                  </a>
                </div>
                <div v-if="app.interview.remarks" class="mt-1 text-muted extra-small">
                  <em>"{{ app.interview.remarks }}"</em>
                </div>
              </div>

              <!-- Result / Evaluation Feedback -->
              <div v-if="app.result?.remarks" class="small text-secondary bg-light border p-2 rounded-3">
                <i class="bi bi-chat-left-quote me-1 text-primary"></i><strong>Company Feedback:</strong>
                <p class="mb-0 mt-1 extra-small text-dark">{{ app.result.remarks }}</p>
              </div>

              <div v-else-if="!app.interview" class="small text-muted fst-italic">
                No interview scheduled. Application screening in progress.
              </div>
            </td>

            <!-- Downloadable Documents -->
            <td class="text-center">
              <div class="d-flex flex-column gap-2 align-items-center">
                <!-- Submitted Resume Download -->
                <button
                  v-if="app.resume_path || app.resume_url"
                  class="btn btn-sm btn-outline-info rounded-pill px-3 w-100"
                  style="max-width: 170px;"
                  @click="openResume(app.resume_path)"
                >
                  <i class="bi bi-file-earmark-pdf me-1"></i>Attached Resume
                </button>
                <span v-else class="text-muted small">No Resume Attached</span>

                <!-- Offer Letter Download (Only for Selected Candidates) -->
                <a
                  v-if="app.application_status === 'selected'"
                  :href="studentAPI.getOfferLetterUrl(app.id)"
                  target="_blank"
                  class="btn btn-sm btn-success rounded-pill px-3 w-100"
                  style="max-width: 170px;"
                >
                  <i class="bi bi-file-earmark-arrow-down me-1"></i>Offer Letter
                </a>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { studentAPI } from '@/api/student'
import { openResume } from '@/utils/resume'
import { useAsyncCsvExport } from '@/composables/useAsyncCsvExport'
import { usePageFeedback } from '@/composables/usePageFeedback'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import FeedbackAlert from '@/components/common/FeedbackAlert.vue'

const applications = ref([])
const loading = ref(true)
const searchQuery = ref('')
const selectedStatus = ref('all')

const { successMsg, errorMsg, showSuccess, showError, clearMessages } = usePageFeedback()

const {
  busy: exporting,
  statusText: exportStatus,
  run: runApplicationExport
} = useAsyncCsvExport({ idleText: 'Exporting...' })

const statusOptions = [
  { label: 'All', value: 'all' },
  { label: 'Applied', value: 'applied' },
  { label: 'Shortlisted', value: 'shortlisted' },
  { label: 'Interview', value: 'interview' },
  { label: 'Selected', value: 'selected' },
  { label: 'Rejected', value: 'rejected' }
]

const statsCount = computed(() => {
  const total = applications.value.length
  const shortlisted = applications.value.filter(a => ['shortlisted', 'interview'].includes(a.application_status)).length
  const interviews = applications.value.filter(a => a.interview || a.application_status === 'interview').length
  const selected = applications.value.filter(a => a.application_status === 'selected').length
  return { total, shortlisted, interviews, selected }
})

const filteredApplications = computed(() => {
  return applications.value.filter(app => {
    // Status Filter
    if (selectedStatus.value !== 'all' && app.application_status !== selectedStatus.value) {
      return false
    }
    // Search Query Filter
    if (searchQuery.value.trim()) {
      const q = searchQuery.value.trim().toLowerCase()
      const matchCompany = (app.company_name || '').toLowerCase().includes(q)
      const matchRole = (app.drive_role || '').toLowerCase().includes(q)
      const matchTitle = (app.drive_title || '').toLowerCase().includes(q)
      return matchCompany || matchRole || matchTitle
    }
    return true
  })
})

async function handleExportApplications() {
  clearMessages()
  try {
    await runApplicationExport({
      start: () => studentAPI.exportApplicationsCsv(),
      status: taskId => studentAPI.getApplicationsExportStatus(taskId),
      download: filename => studentAPI.downloadApplicationsExport(filename),
      success: () => showSuccess('Application CSV exported successfully.')
    })
  } catch (err) {
    showError(err?.response?.data?.error || err.message || 'Application CSV export failed.')
  }
}

onMounted(async () => {
  try {
    const { data } = await studentAPI.getApplications()
    applications.value = data.applications || []
  } catch (err) {
    console.error('Failed to load application history:', err)
  } finally {
    loading.value = false
  }
})
</script>
