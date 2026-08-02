<script setup>
import { ref, onMounted } from 'vue'
import SectionCard from '@/components/common/SectionCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import { adminAPI } from '@/api/admin'

const drives = ref([])
const loading = ref(false)
const actionMsg = ref('')

const headers = ['Company', 'Role', 'Package', 'Eligibility', 'Deadline', 'Openings', 'Status', 'Actions']
const columns = ['company_name', 'job_role', 'package', 'eligibility', 'deadline', 'openings', 'status', 'actions']

async function fetchDrives() {
  loading.value = true
  try {
    const { data } = await adminAPI.getDrives()
    drives.value = data.drives || []
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function approveDrive(drive) {
  try {
    await adminAPI.approveDrive(drive.id)
    drive.status = 'open'
    actionMsg.value = `Drive for ${drive.company_name} approved and opened.`
    setTimeout(() => { actionMsg.value = '' }, 3000)
  } catch (err) {
    console.error(err)
  }
}

async function closeDrive(drive) {
  try {
    await adminAPI.closeDrive(drive.id)
    drive.status = 'closed'
    actionMsg.value = `Drive for ${drive.company_name} closed. New applications disabled.`
    setTimeout(() => { actionMsg.value = '' }, 3000)
  } catch (err) {
    console.error(err)
  }
}

async function rejectDrive(drive) {
  try {
    await adminAPI.rejectDrive(drive.id)
    drive.status = 'rejected'
    actionMsg.value = `Drive for ${drive.company_name} rejected.`
    setTimeout(() => { actionMsg.value = '' }, 3000)
  } catch (err) {
    console.error(err)
  }
}

onMounted(fetchDrives)
</script>

<template>
  <SectionCard title="Placement Drive Management" subtitle="Approval screen, status control, and drive posting management">
    <div v-if="actionMsg" class="alert alert-success alert-dismissible fade show mb-3" role="alert">
      <i class="bi bi-check-circle me-2"></i>{{ actionMsg }}
      <button type="button" class="btn-close" @click="actionMsg = ''"></button>
    </div>
    <div v-if="loading" class="text-center py-4"><div class="spinner-border text-primary"></div></div>
    <DataTable v-else :headers="headers" :columns="columns" :rows="drives">
      <template #status="{ row }">
        <span class="badge rounded-pill"
          :class="row.status === 'open' ? 'badge-soft-success' : row.status === 'pending' ? 'badge-soft-warning' : row.status === 'closed' ? 'badge-soft-secondary' : 'badge-soft-danger'">
          {{ row.status }}
        </span>
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
