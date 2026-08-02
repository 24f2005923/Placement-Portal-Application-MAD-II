<template>
  <div class="row g-4">
    <!-- Header Card -->
    <div class="col-12">
      <div class="portal-card p-4">
        <div class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">
          <div>
            <h3 class="section-heading mb-1">Application Management</h3>
            <p class="text-muted mb-0">Monitor, filter, and manage all student placement applications across drives.</p>
          </div>
          <div class="d-flex align-items-center gap-2 flex-wrap">
            <span class="badge badge-soft-primary px-3 py-2">Total: {{ pagination.total || 0 }}</span>
          </div>
        </div>

        <!-- Feedback Alerts -->
        <div v-if="msg" class="alert alert-success alert-dismissible fade show" role="alert">
          <i class="bi bi-check-circle me-2"></i>{{ msg }}
          <button type="button" class="btn-close" @click="msg = ''"></button>
        </div>
        <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
          <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
          <button type="button" class="btn-close" @click="error = ''"></button>
        </div>

        <!-- Filters & Search Bar -->
        <div class="row g-3 mb-4 align-items-center">
          <div class="col-12 col-md-6 col-lg-5">
            <div class="input-group">
              <span class="input-group-text bg-white"><i class="bi bi-search text-muted"></i></span>
              <input
                v-model="search"
                type="search"
                class="form-control"
                placeholder="Search by student name, roll #, company, or role..."
                @input="debouncedSearch"
              />
            </div>
          </div>
          <div class="col-12 col-sm-6 col-md-4 col-lg-3">
            <select v-model="statusFilter" class="form-select" @change="fetchApplications">
              <option value="">All Statuses</option>
              <option value="applied">Applied (Screening)</option>
              <option value="shortlisted">Shortlisted</option>
              <option value="interview">Interview Scheduled</option>
              <option value="selected">Selected / Placed</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
          <div class="col-12 col-sm-6 col-md-2">
            <button class="btn btn-outline-secondary w-100" @click="resetFilters">
              <i class="bi bi-arrow-counterclockwise me-1"></i>Reset
            </button>
          </div>
        </div>

        <!-- Applications Data Table -->
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary"></div>
        </div>
        <div v-else-if="applications.length === 0" class="text-center py-5 text-muted">
          <i class="bi bi-inbox fs-1 d-block mb-2 text-secondary"></i>
          No applications match the current filter or search criteria.
        </div>
        <div v-else class="table-responsive">
          <table class="table align-middle table-hover border">
            <thead class="table-light">
              <tr>
                <th>Student Details</th>
                <th>Company & Job Role</th>
                <th>Applied Date</th>
                <th>Resume</th>
                <th>Current Status</th>
                <th class="text-end">Manage Status</th>
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
                  <a
                    v-if="app.resume_url"
                    :href="app.resume_url"
                    target="_blank"
                    class="btn btn-sm btn-outline-primary rounded-pill px-3"
                  >
                    <i class="bi bi-file-earmark-pdf me-1"></i>View Resume
                  </a>
                  <span v-else class="text-muted small">Not Uploaded</span>
                </td>
                <td>
                  <span class="badge rounded-pill px-3 py-2" :class="getStatusBadgeClass(app.application_status)">
                    {{ app.stage || app.application_status }}
                  </span>
                </td>
                <td class="text-end">
                  <div class="d-inline-block">
                    <select
                      :value="app.application_status"
                      class="form-select form-select-sm fw-medium border-secondary"
                      :disabled="updatingId === app.id"
                      @change="handleStatusChange(app.id, $event.target.value)"
                    >
                      <option value="applied">Applied</option>
                      <option value="shortlisted">Shortlisted</option>
                      <option value="interview">Interview</option>
                      <option value="selected">Selected</option>
                      <option value="rejected">Rejected</option>
                    </select>
                  </div>
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

const applications = ref([])
const loading = ref(true)
const search = ref('')
const statusFilter = ref('')
const msg = ref('')
const error = ref('')
const updatingId = ref(null)
let searchTimeout = null

const pagination = ref({
  current_page: 1,
  total_pages: 1,
  total: 0,
  has_next: false,
  has_prev: false
})

function getStatusBadgeClass(status) {
  switch (status) {
    case 'selected':
      return 'badge-soft-success'
    case 'shortlisted':
      return 'badge-soft-info'
    case 'interview':
      return 'badge-soft-warning'
    case 'rejected':
      return 'badge-soft-danger'
    default:
      return 'badge-soft-secondary'
  }
}

async function fetchApplications(page = 1) {
  loading.value = true
  msg.value = ''
  error.value = ''
  try {
    const { data } = await adminAPI.getApplications({
      search: search.value,
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
    error.value = err.response?.data?.error || 'Failed to load applications.'
  } finally {
    loading.value = false
  }
}

function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchApplications(1)
  }, 350)
}

function resetFilters() {
  search.value = ''
  statusFilter.value = ''
  fetchApplications(1)
}

function changePage(newPage) {
  if (newPage >= 1 && newPage <= pagination.value.total_pages) {
    fetchApplications(newPage)
  }
}

async function handleStatusChange(appId, newStatus) {
  updatingId.value = appId
  msg.value = ''
  error.value = ''
  try {
    const { data } = await adminAPI.setApplicationStatus(appId, newStatus)
    msg.value = data.message || `Application status updated to ${newStatus}.`
    // Update local state item
    const target = applications.value.find((a) => a.id === appId)
    if (target) {
      target.application_status = newStatus
      if (data.application) {
        target.stage = data.application.stage
      }
    }
    setTimeout(() => { msg.value = '' }, 3000)
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to update application status.'
    fetchApplications(pagination.value.current_page)
  } finally {
    updatingId.value = null
  }
}

onMounted(() => {
  fetchApplications(1)
})
</script>
