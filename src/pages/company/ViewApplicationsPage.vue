<script setup>
import { ref, onMounted } from 'vue'
import SectionCard from '@/components/common/SectionCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import FeedbackAlert from '@/components/common/FeedbackAlert.vue'
import { companyAPI } from '@/api/company'
import { openResume } from '@/utils/resume'
import { useAsyncCsvExport } from '@/composables/useAsyncCsvExport'
import { usePageFeedback } from '@/composables/usePageFeedback'

const applications = ref([])
const drives = ref([])
const loading = ref(false)
const { successMsg, errorMsg, showSuccess, showError, clearMessages } = usePageFeedback()

const selectedStudent = ref(null)
const selectedDriveId = ref('')
const {
  busy: exporting,
  statusText: exportStatus,
  run: runApplicationExport
} = useAsyncCsvExport({ idleText: 'Exporting...' })

const headers = ['Drive', 'Student', 'Resume', 'Status', 'Stage', 'Actions']
const columns = ['drive_title', 'student_name', 'resume', 'application_status', 'stage', 'actions']

async function fetchApplications() {
  loading.value = true
  errorMsg.value = ''
  try {
    const { data } = await companyAPI.getApplications()
    applications.value = data.applications || []
  } catch (err) {
    console.error(err)
    const status = err.response?.status
    if (status === 401 || status === 403) {
      errorMsg.value = 'Session expired or unauthorized. Please log out and log back in.'
    } else if (status === 404) {
      showError('Company profile not found. Please log out, log in again, and ensure your account is approved.')
    } else {
      showError(err.response?.data?.error || 'Failed to load applications. Please try again.')
    }
  } finally {
    loading.value = false
  }
}

async function fetchDrives() {
  try {
    const { data } = await companyAPI.getDrives()
    drives.value = data.drives || []
  } catch (err) {
    console.error(err)
    showError(err.response?.data?.error || 'Failed to load placement drives.')
  }
}

async function shortlist(app) {
  clearMessages()
  try {
    const { data } = await companyAPI.shortlistApplication(app.id)
    app.application_status = 'shortlisted'
    if (data.application) {
      app.stage = data.application.stage
    }
    showSuccess(`Candidate ${app.student_name} shortlisted. Notification sent.`)
  } catch (err) {
    showError(err.response?.data?.error || 'Failed to shortlist candidate.')
  }
}

async function reject(app) {
  clearMessages()
  try {
    const { data } = await companyAPI.rejectApplication(app.id)
    app.application_status = 'rejected'
    if (data.application) {
      app.stage = data.application.stage
    }
    showSuccess(`Application for ${app.student_name} rejected. Notification sent.`)
  } catch (err) {
    showError(err.response?.data?.error || 'Failed to reject application.')
  }
}

async function exportApplications() {
  clearMessages()

  if (!selectedDriveId.value) {
    showError('Please select a placement drive before exporting applications.')
    return
  }

  try {
    await runApplicationExport({
      start: () => companyAPI.exportApplicationsCsv(selectedDriveId.value),
      status: taskId => companyAPI.getApplicationsExportStatus(taskId),
      download: filename => companyAPI.downloadApplicationsExport(filename),
      success: () => showSuccess('Applications CSV exported. Notification sent.')
    })
  } catch (err) {
    showError(err.response?.data?.error || err.message || 'Failed to export applications.')
  }
}

onMounted(() => {
  fetchApplications()
  fetchDrives()
})
</script>

<template>
  <SectionCard title="View Applications" subtitle="Manage student applications received for your placement drives">
    <FeedbackAlert 
      :success="successMsg" 
      :error="errorMsg" 
      @clear-success="clearMessages"
      @clear-error="clearMessages"
    />

    <div class="row g-3 align-items-end mb-3">
      <div class="col-12 col-lg-6">
        <label class="form-label fw-semibold" for="export-drive">Placement Drive</label>
        <select id="export-drive" v-model="selectedDriveId" class="form-select" :disabled="exporting">
          <option value="">Select a drive to export</option>
          <option v-for="drive in drives" :key="drive.id" :value="drive.id">
            {{ drive.title || drive.job_role }}
          </option>
        </select>
      </div>
      <div class="col-12 col-lg-auto">
        <button class="btn btn-outline-primary rounded-pill px-4" @click="exportApplications" :disabled="exporting">
          <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bi bi-filetype-csv me-2"></i>
          {{ exporting ? exportStatus : 'Export Applications (CSV)' }}
        </button>
      </div>
    </div>

    <LoadingSpinner v-if="loading" />
    <DataTable v-else :headers="headers" :columns="columns" :rows="applications">
      <template #resume="{ row }">
        <button v-if="row.resume_path || row.student_resume_path"
          class="btn btn-sm btn-outline-info"
          @click="openResume(row.resume_path || row.student_resume_path)">
          <i class="bi bi-file-earmark-pdf me-1"></i>Resume
        </button>
        <span v-else class="text-muted small">No Resume</span>
      </template>

      <template #application_status="{ row }">
        <StatusBadge variant="application" :status="row.application_status" />
      </template>

      <template #actions="{ row }">
        <div class="btn-group btn-group-sm">
          <!-- Shortlist Button -->
          <button
            class="btn btn-outline-primary"
            @click="shortlist(row)"
            :disabled="['shortlisted', 'interview', 'selected', 'rejected'].includes(row.application_status)"
          >
            Shortlist
          </button>

          <!-- Reject Button -->
          <button
            class="btn btn-outline-danger"
            @click="reject(row)"
            :disabled="['rejected', 'selected'].includes(row.application_status)"
          >
            Reject
          </button>

          <!-- Schedule Interview (Only enabled for shortlisted or interview) -->
          <router-link
            to="/company/interviews"
            class="btn btn-outline-secondary"
            :class="{ disabled: !['shortlisted', 'interview'].includes(row.application_status) }"
            :tabindex="!['shortlisted', 'interview'].includes(row.application_status) ? -1 : 0"
          >
            Schedule
          </router-link>
          <button class="btn btn-outline-info" @click="selectedStudent = row">
            Profile
          </button>
        </div>
      </template>
    </DataTable>
    
    <EmptyState 
      v-if="!applications.length && !loading" 
      title="No applications received yet."
      icon="bi-journal-x"
    />

    <div v-if="selectedStudent" class="modal fade show d-block" tabindex="-1" role="dialog">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <div>
              <h5 class="modal-title mb-0">{{ selectedStudent.student_name || 'Student Profile' }}</h5>
              <small class="text-muted">{{ selectedStudent.student_register_number || 'Register number unavailable' }}</small>
            </div>
            <button type="button" class="btn-close" @click="selectedStudent = null"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label">Name</label>
                <input class="form-control" :value="selectedStudent.student_name || 'N/A'" readonly />
              </div>
              <div class="col-md-6">
                <label class="form-label">Register Number</label>
                <input class="form-control" :value="selectedStudent.student_register_number || 'N/A'" readonly />
              </div>
              <div class="col-md-6">
                <label class="form-label">Department</label>
                <input class="form-control" :value="selectedStudent.student_department || 'N/A'" readonly />
              </div>
              <div class="col-md-6">
                <label class="form-label">CGPA</label>
                <input class="form-control" :value="selectedStudent.student_cgpa || 'N/A'" readonly />
              </div>
              <div class="col-md-6">
                <label class="form-label">Applied Drive</label>
                <input class="form-control" :value="selectedStudent.drive_title || selectedStudent.drive_role || 'N/A'" readonly />
              </div>
              <div class="col-md-6">
                <label class="form-label">Application Status</label>
                <div>
                  <StatusBadge variant="application" :status="selectedStudent.application_status" />
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button
              v-if="selectedStudent.resume_path || selectedStudent.student_resume_path"
              class="btn btn-outline-primary"
              @click="openResume(selectedStudent.resume_path || selectedStudent.student_resume_path)"
            >
              <i class="bi bi-file-earmark-pdf me-1"></i>View Resume
            </button>
            <button class="btn btn-secondary" @click="selectedStudent = null">Close</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="selectedStudent" class="modal-backdrop fade show"></div>
  </SectionCard>
</template>
