<script setup>
import { ref, onMounted } from 'vue'
import SectionCard from '@/components/common/SectionCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import { companyAPI } from '@/api/company'

const applications = ref([])
const loading = ref(false)
const msg = ref('')

const headers = ['Drive', 'Student', 'Status', 'Stage', 'Actions']
const columns = ['drive_title', 'student_name', 'application_status', 'stage', 'actions']

async function fetchApplications() {
  loading.value = true
  try {
    const { data } = await companyAPI.getApplications()
    applications.value = data.applications
  } catch (err) { console.error(err) } finally { loading.value = false }
}

async function shortlist(app) {
  try {
    await companyAPI.shortlistApplication(app.id)
    app.application_status = 'shortlisted'
    app.stage = 'HR Round'
    msg.value = `${app.student_name} shortlisted.`
    setTimeout(() => { msg.value = '' }, 3000)
  } catch (err) { console.error(err) }
}

onMounted(fetchApplications)
</script>

<template>
  <SectionCard title="View Applications" subtitle="All student applications received for your drives">
    <div v-if="msg" class="alert alert-success mb-3">{{ msg }}</div>
    <div v-if="loading" class="text-center py-4"><div class="spinner-border text-primary"></div></div>
    <DataTable v-else :headers="headers" :columns="columns" :rows="applications">
      <template #application_status="{ row }">
        <span class="badge rounded-pill"
          :class="row.application_status === 'selected' ? 'badge-soft-success' : row.application_status === 'shortlisted' ? 'badge-soft-warning' : row.application_status === 'rejected' ? 'badge-soft-danger' : 'badge-soft-primary'">
          {{ row.application_status }}
        </span>
      </template>
      <template #actions="{ row }">
        <div class="btn-group btn-group-sm">
          <button class="btn btn-outline-primary" @click="shortlist(row)"
            :disabled="['shortlisted','interview','selected','rejected'].includes(row.application_status)">
            Shortlist
          </button>
          <router-link to="/company/interviews" class="btn btn-outline-secondary">Schedule</router-link>
        </div>
      </template>
    </DataTable>
    <p v-if="!applications.length && !loading" class="text-muted text-center py-3">No applications yet.</p>
  </SectionCard>
</template>
