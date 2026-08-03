<template>
  <SectionCard title="View Placement Drives" subtitle="Search and browse active placement drives, then apply instantly">
    <div class="row g-3 mb-4 align-items-center">
      <div class="col-12 col-md-9 col-lg-10">
        <div class="input-group">
          <span class="input-group-text bg-white"><i class="bi bi-search text-muted"></i></span>
          <input
            v-model="search"
            type="search"
            class="form-control form-control-lg"
            placeholder="Search drives by company name, job role, title, package, or eligibility..."
            @input="debouncedSearch"
          />
        </div>
      </div>
      <div class="col-12 col-md-3 col-lg-2 d-grid">
        <button class="btn btn-primary btn-lg" @click="fetchDrives(1)" :disabled="loading">
          <i class="bi bi-search me-1"></i>Search
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
    </div>
    <div v-else-if="drives.length === 0" class="text-center py-5 text-muted">
      <i class="bi bi-briefcase fs-1 d-block mb-2 text-secondary"></i>
      No active placement drives found matching your search.
    </div>
    <DataTable v-else :headers="headers" :columns="columns" :rows="drives">
      <template #company_name="{ row }">
        <div class="fw-semibold text-dark">{{ row.company_name || 'N/A' }}</div>
        <small class="text-muted">{{ row.title || row.job_role }}</small>
      </template>

      <template #package="{ row }">
        <span class="fw-semibold text-success">{{ row.package || 'As per policy' }}</span>
      </template>

      <template #status="{ row }">
        <span class="badge rounded-pill" :class="driveBadge(row.status)">
          {{ row.status }}
        </span>
      </template>

      <template #action="{ row }">
        <router-link
          v-if="!row.already_applied && row.is_active"
          :to="`/student/drives/${row.id}/apply`"
          class="btn btn-sm btn-primary rounded-pill px-3"
        >
          <i class="bi bi-send me-1"></i>Apply
        </router-link>
        <span v-else-if="row.already_applied" class="badge badge-soft-success px-3 py-2">Applied</span>
        <span v-else class="badge badge-soft-secondary px-3 py-2">Closed</span>
      </template>
    </DataTable>
  </SectionCard>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import SectionCard from '@/components/common/SectionCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import { studentAPI } from '@/api/student'
import { driveBadge } from '@/utils/statusMeta'

const drives = ref([])
const loading = ref(false)
const search = ref('')
let searchTimeout = null

const headers = ['Company & Drive', 'Role', 'Package', 'Deadline', 'Openings', 'Status', 'Action']
const columns = ['company_name', 'job_role', 'package', 'deadline', 'openings', 'status', 'action']

async function fetchDrives() {
  loading.value = true
  try {
    const params = {}
    if (search.value) params.search = search.value.trim()
    const { data } = await studentAPI.getDrives(params)
    drives.value = data.drives || []
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchDrives()
  }, 350)
}

onMounted(fetchDrives)
</script>
