<script setup>
import { ref, onMounted } from 'vue'
import SectionCard from '@/components/common/SectionCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import FeedbackAlert from '@/components/common/FeedbackAlert.vue'
import { adminAPI } from '@/api/admin'
import { usePageFeedback } from '@/composables/usePageFeedback'

const drives = ref([])
const loading = ref(false)
const { successMsg, errorMsg, showSuccess, showError, clearMessages } = usePageFeedback()

const headers = ['Company', 'Role', 'Package', 'Eligibility', 'Deadline', 'Openings', 'Status', 'Actions']
const columns = ['company_name', 'job_role', 'package', 'eligibility', 'deadline', 'openings', 'status', 'actions']

async function fetchDrives() {
  loading.value = true
  try {
    const { data } = await adminAPI.getDrives()
    drives.value = data.drives || []
  } catch (err) {
    showError(err.response?.data?.error || 'Failed to fetch drives.')
  } finally {
    loading.value = false
  }
}

async function approveDrive(drive) {
  try {
    const { data } = await adminAPI.approveDrive(drive.id)
    drive.status = data.drive.status
    showSuccess(`Drive for ${drive.company_name} approved.`)
  } catch (err) {
    showError(err.response?.data?.error || 'Failed to approve drive.')
  }
}

async function closeDrive(drive) {
  try {
    await adminAPI.closeDrive(drive.id)
    drive.status = 'closed'
    showSuccess(`Drive for ${drive.company_name} closed.`)
  } catch (err) {
    showError(err.response?.data?.error || 'Failed to close drive.')
  }
}

async function rejectDrive(drive) {
  try {
    await adminAPI.rejectDrive(drive.id)
    drive.status = 'rejected'
    showSuccess(`Drive for ${drive.company_name} rejected.`)
  } catch (err) {
    showError(err.response?.data?.error || 'Failed to reject drive.')
  }
}

onMounted(fetchDrives)
</script>

<template>
  <SectionCard title="Placement Drives" subtitle="Monitor and manage all campus placement drives">
    <FeedbackAlert 
      :success="successMsg"
      :error="errorMsg"
      @clear-success="clearMessages"
      @clear-error="clearMessages"
    />
    
    <LoadingSpinner v-if="loading" />
    <EmptyState 
      v-else-if="drives.length === 0" 
      title="No placement drives found." 
      icon="bi-briefcase"
    />
    <DataTable v-else :headers="headers" :columns="columns" :rows="drives">
      <template #status="{ row }">
        <StatusBadge :status="row.status" />
      </template>
      <template #actions="{ row }">
        <div class="btn-group btn-group-sm">
          <router-link :to="`/admin/drives/${row.id}`" class="btn btn-outline-primary">Details</router-link>
          <button class="btn btn-outline-success" @click="approveDrive(row)" :disabled="row.status === 'open'">Approve</button>
          <button class="btn btn-outline-secondary" @click="closeDrive(row)" :disabled="row.status === 'closed'">Close</button>
          <button class="btn btn-outline-danger" @click="rejectDrive(row)" :disabled="row.status === 'rejected'">Reject</button>
        </div>
      </template>
    </DataTable>
  </SectionCard>
</template>
