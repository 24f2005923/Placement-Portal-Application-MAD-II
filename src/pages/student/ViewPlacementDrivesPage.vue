<script setup>
import { ref, onMounted } from 'vue'
import SectionCard from '@/components/common/SectionCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import { studentAPI } from '@/api/student'

const drives = ref([])
const loading = ref(false)
const search = ref('')

const headers = ['Company', 'Role', 'Package', 'Deadline', 'Openings', 'Status', 'Action']
const columns = ['company_name', 'job_role', 'package', 'deadline', 'openings', 'status', 'action']

async function fetchDrives() {
  loading.value = true
  try {
    const params = {}
    if (search.value) params.search = search.value
    const { data } = await studentAPI.getDrives(params)
    drives.value = data.drives
  } catch (err) { console.error(err) } finally { loading.value = false }
}

onMounted(fetchDrives)
</script>

<template>
  <SectionCard title="View Placement Drives" subtitle="Browse active drives and apply instantly">
    <div class="row g-3 mb-4">
      <div class="col-12 col-lg-9">
        <input v-model="search" type="search" class="form-control" placeholder="Search by role or company..." />
      </div>
      <div class="col-12 col-lg-3 d-grid">
        <button class="btn btn-primary" @click="fetchDrives" :disabled="loading">Search</button>
      </div>
    </div>
    <div v-if="loading" class="text-center py-4"><div class="spinner-border text-primary"></div></div>
    <DataTable v-else :headers="headers" :columns="columns" :rows="drives">
      <template #status="{ row }">
        <span class="badge rounded-pill badge-soft-success">{{ row.status }}</span>
      </template>
      <template #action="{ row }">
        <router-link v-if="!row.already_applied" :to="`/student/drives/${row.id}/apply`" class="btn btn-sm btn-primary">Apply</router-link>
        <span v-else class="badge badge-soft-success">Applied</span>
      </template>
    </DataTable>
    <p v-if="!drives.length && !loading" class="text-muted text-center py-3">No open placement drives at the moment.</p>
  </SectionCard>
</template>
