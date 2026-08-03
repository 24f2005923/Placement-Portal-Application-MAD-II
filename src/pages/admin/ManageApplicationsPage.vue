<template>
  <div class="row g-4">
    <!-- Header Card -->
    <div class="col-12">
      <div class="portal-card p-4">
        <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">
          <div>
            <h3 class="section-heading mb-1">Application Management</h3>
            <p class="text-muted mb-0">Monitor and manage all student placement applications across drives.</p>
          </div>
          <div class="d-flex align-items-center gap-2 flex-wrap">
            <span class="badge badge-soft-primary px-3 py-2">Total: {{ pagination.total || 0 }}</span>
          </div>
        </div>

        <!-- Feedback Alerts -->
        <FeedbackAlert
          :success="successMsg"
          :error="errorMsg"
          @clear-success="clearMessages"
          @clear-error="clearMessages"
        />

        <!-- Status Filter -->
        <div class="row g-3 mb-4 align-items-center">
          <div class="col-12 col-sm-6 col-md-4 col-lg-3">
            <select v-model="statusFilter" class="form-select" @change="fetchApplications(1)">
              <option value="">All Statuses</option>
              <option value="applied">Applied (Screening)</option>
              <option value="shortlisted">Shortlisted</option>
              <option value="interview">Interview Scheduled</option>
              <option value="selected">Selected / Placed</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
        </div>

        <!-- Applications Data Table -->
        <LoadingSpinner v-if="loading" />
        <EmptyState 
          v-else-if="applications.length === 0" 
          title="No applications match the current status filter." 
        />
        <div v-else class="table-responsive">
          <table class="table align-middle table-hover border">
            <thead class="table-light">
              <tr>
                <th>Student Details</th>
                <th>Company & Job Role</th>
                <th>Applied Date</th>
                <th>Resume</th>
                <th>Current Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in applications" :key="app.id">
                <td>
                  <div class="fw-semibold text-dark">{{ app.student_name || 'N/A' }}</div>
                  <div class="small text-muted">
                    Roll: {{ app.student_register_number || 'N/A' }} • {{ app.student_department || '' }}
                    <span v-if="app.student_cgpa" class="badge badge-soft-info ms-1">CGPA: {{ app.student_cgpa }}</span>
                  </div>
                </td>
                <td>
                  <div class="fw-semibold text-primary">{{ app.company_name || 'N/A' }}</div>
                  <div class="small text-muted">{{ app.drive_title || app.drive_role }}</div>
                  <small v-if="app.drive_package" class="text-success fw-medium">{{ app.drive_package }}</small>
                </td>
                <td>
                  <span class="small text-muted">{{ app.applied_at || 'N/A' }}</span>
                </td>
                <td>
                  <button
                    v-if="app.resume_url"
                    class="btn btn-sm btn-outline-primary rounded-pill px-3"
                    :disabled="openingResume === app.resume_path"
                    @click="openAdminResume(app.resume_path)"
                  >
                    <span v-if="openingResume === app.resume_path" class="spinner-border spinner-border-sm me-1"></span>
                    <i v-else class="bi bi-file-earmark-pdf me-1"></i>View Resume
                  </button>
                  <span v-else class="text-muted small">Not Uploaded</span>
                </td>
                <td>
                  <StatusBadge variant="admin_application" :status="app.application_status" :label="app.stage || app.application_status" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination Controls -->
        <div v-if="pagination.total_pages > 1" class="d-flex justify-content-between align-items-center mt-4">
          <small class="text-muted">
            Showing page {{ pagination.current_page }} of {{ pagination.total_pages }} ({{ pagination.total }} records)
          </small>
          <ul class="pagination mb-0">
            <li class="page-item" :class="{ disabled: !pagination.has_prev }">
              <button class="page-link" @click="changePage(pagination.current_page - 1)">Previous</button>
            </li>
            <li class="page-item disabled">
              <span class="page-link">{{ pagination.current_page }}</span>
            </li>
            <li class="page-item" :class="{ disabled: !pagination.has_next }">
              <button class="page-link" @click="changePage(pagination.current_page + 1)">Next</button>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/api/admin'
import httpClient from '@/api/axios'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import FeedbackAlert from '@/components/common/FeedbackAlert.vue'
import { usePageFeedback } from '@/composables/usePageFeedback'

const applications = ref([])
const loading = ref(true)
const statusFilter = ref('')
const openingResume = ref(null)

const { successMsg, errorMsg, showError, clearMessages } = usePageFeedback()

const pagination = ref({
  current_page: 1,
  total_pages: 1,
  total: 0,
  has_next: false,
  has_prev: false
})

async function fetchApplications(page = 1) {
  loading.value = true
  clearMessages()
  try {
    const { data } = await adminAPI.getApplications({
      status: statusFilter.value,
      page: page,
      per_page: 15
    })
    applications.value = data.applications || []
    pagination.value = {
      current_page: data.current_page || page,
      total_pages: data.total_pages || 1,
      total: data.total || 0,
      has_next: data.has_next || false,
      has_prev: data.has_prev || false
    }
  } catch (err) {
    showError(err.response?.data?.error || 'Failed to load applications.')
  } finally {
    loading.value = false
  }
}

async function openAdminResume(resumePath) {
  if (!resumePath) return
  openingResume.value = resumePath
  try {
    const response = await httpClient.get('/api/admin/resumes/' + resumePath, {
      responseType: 'blob'
    })
    const blobUrl = URL.createObjectURL(response.data)
    window.open(blobUrl, '_blank')
  } catch (err) {
    showError('Could not open resume. The file may no longer exist.')
  } finally {
    openingResume.value = null
  }
}

function changePage(newPage) {
  if (newPage >= 1 && newPage <= pagination.value.total_pages) {
    fetchApplications(newPage)
  }
}


onMounted(() => {
  fetchApplications(1)
})
</script>
