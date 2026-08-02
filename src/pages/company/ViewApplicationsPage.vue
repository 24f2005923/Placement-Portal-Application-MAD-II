<script setup>
import { ref, onMounted } from 'vue'
import SectionCard from '@/components/common/SectionCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import { companyAPI } from '@/api/company'
import { openResume } from '@/utils/resume'

const applications = ref([])
const loading = ref(false)
const msg = ref('')
const errorMsg = ref('')

const headers = ['Drive', 'Student', 'Resume', 'Status', 'Stage', 'Actions']
const columns = ['drive_title', 'student_name', 'resume', 'application_status', 'stage', 'actions']

async function fetchApplications() {
  loading.value = true
  try {
    const { data } = await companyAPI.getApplications()
    applications.value = data.applications || []
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function shortlist(app) {
  msg.value = ''
  errorMsg.value = ''
  try {
    const { data } = await companyAPI.shortlistApplication(app.id)
    app.application_status = 'shortlisted'
    if (data.application) {
      app.stage = data.application.stage
    }
    msg.value = `Candidate ${app.student_name} shortlisted. Notification sent.`
    setTimeout(() => { msg.value = '' }, 4000)
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to shortlist candidate.'
  }
}

async function reject(app) {
  msg.value = ''
  errorMsg.value = ''
  try {
    const { data } = await companyAPI.rejectApplication(app.id)
    app.application_status = 'rejected'
    if (data.application) {
      app.stage = data.application.stage
    }
    msg.value = `Application for ${app.student_name} rejected. Notification sent.`
    setTimeout(() => { msg.value = '' }, 4000)
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to reject application.'
  }
}

async function updateStatus(app, newStatus) {
  msg.value = ''
  errorMsg.value = ''
  try {
    const { data } = await companyAPI.updateApplicationStatus(app.id, newStatus)
    app.application_status = newStatus
    if (data.application) {
      app.stage = data.application.stage
    }
    msg.value = `Status for ${app.student_name} updated to ${newStatus}. Notification sent.`
    setTimeout(() => { msg.value = '' }, 4000)
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to update status.'
  }
}

onMounted(fetchApplications)
</script>

<template>
  <SectionCard title="View Applications" subtitle="Manage student applications received for your placement drives">
    <div v-if="msg" class="alert alert-success alert-dismissible fade show mb-3" role="alert">
      <i class="bi bi-check-circle me-2"></i>{{ msg }}
      <button type="button" class="btn-close" @click="msg = ''"></button>
    </div>
    <div v-if="errorMsg" class="alert alert-danger alert-dismissible fade show mb-3" role="alert">
      <i class="bi bi-exclamation-triangle me-2"></i>{{ errorMsg }}
      <button type="button" class="btn-close" @click="errorMsg = ''"></button>
    </div>

    <div v-if="loading" class="text-center py-4"><div class="spinner-border text-primary"></div></div>
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
        <span class="badge rounded-pill"
          :class="row.application_status === 'selected' ? 'badge-soft-success' : row.application_status === 'shortlisted' ? 'badge-soft-warning' : row.application_status === 'rejected' ? 'badge-soft-danger' : row.application_status === 'interview' ? 'badge-soft-info' : 'badge-soft-secondary'">
          {{ row.application_status }}
        </span>
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
        </div>
      </template>
    </DataTable>
    <p v-if="!applications.length && !loading" class="text-muted text-center py-3">No applications received yet.</p>
  </SectionCard>
</template>
