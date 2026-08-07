<script setup>
import { ref, computed, onMounted } from 'vue'
import StatCard from '@/components/common/StatCard.vue'
import SectionCard from '@/components/common/SectionCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import { companyAPI } from '@/api/company'

const stats = ref([])
const applications = ref([])
const loading = ref(true)

// Derive simple funnel counts from the stats cards the API already returns
const funnelData = computed(() => {
  const shortlisted = stats.value.find(s => s.label === 'Shortlisted Students')
  const selected    = stats.value.find(s => s.label === 'Selected Students')
  const total       = stats.value.find(s => s.label === 'Applications Received')
  return {
    total:       parseInt(total?.value       ?? '0', 10),
    shortlisted: parseInt(shortlisted?.value ?? '0', 10),
    selected:    parseInt(selected?.value    ?? '0', 10)
  }
})

const headers = ['Drive', 'Student', 'Status', 'Stage']
const columns = ['drive_title', 'student_name', 'application_status', 'stage']

onMounted(async () => {
  try {
    const [statsRes, appsRes] = await Promise.all([
      companyAPI.getStats(),
      companyAPI.getApplications()
    ])
    stats.value = statsRes.data.stats
    applications.value = appsRes.data.applications.slice(0, 10)
  } catch (err) { console.error(err) } finally { loading.value = false }
})
</script>

<template>
  <div class="row g-4">
    <div v-if="loading" class="col-12 text-center py-5"><div class="spinner-border text-primary"></div></div>
    <template v-else>
      <div v-for="item in stats" :key="item.label" class="col-12 col-sm-6 col-xl-3">
        <StatCard v-bind="item" />
      </div>
      <div class="col-12 col-xl-7">
        <SectionCard title="Application Pipeline" subtitle="Funnel summary across all your placement drives">
          <div v-if="funnelData.total === 0" class="text-center text-muted py-4">
            <i class="bi bi-funnel fs-2 d-block mb-2 text-secondary"></i>
            No applications received yet.
          </div>
          <div v-else class="row g-3 text-center">
            <div class="col-4">
              <div class="border rounded-3 p-3">
                <div class="fs-3 fw-bold text-secondary">{{ funnelData.total }}</div>
                <div class="small text-muted">Applied</div>
              </div>
            </div>
            <div class="col-4">
              <div class="border rounded-3 p-3 border-warning">
                <div class="fs-3 fw-bold text-warning">{{ funnelData.shortlisted }}</div>
                <div class="small text-muted">Shortlisted</div>
              </div>
            </div>
            <div class="col-4">
              <div class="border rounded-3 p-3 border-success">
                <div class="fs-3 fw-bold text-success">{{ funnelData.selected }}</div>
                <div class="small text-muted">Selected</div>
              </div>
            </div>
          </div>
        </SectionCard>
      </div>
      <div class="col-12 col-xl-5">
        <SectionCard title="Latest Applications" subtitle="Recent student submissions for your drives">
          <DataTable :headers="headers" :columns="columns" :rows="applications">
            <template #application_status="{ row }">
              <span class="badge rounded-pill"
                :class="row.application_status === 'selected' ? 'badge-soft-success' : row.application_status === 'interview' ? 'badge-soft-warning' : row.application_status === 'rejected' ? 'badge-soft-danger' : 'badge-soft-primary'">
                {{ row.application_status }}
              </span>
            </template>
          </DataTable>
          <p v-if="!applications.length" class="text-muted text-center py-3">No applications yet.</p>
        </SectionCard>
      </div>
    </template>
  </div>
</template>
