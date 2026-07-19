<script setup>
import { ref, onMounted } from 'vue'
import StatCard from '@/components/common/StatCard.vue'
import ChartPlaceholder from '@/components/common/ChartPlaceholder.vue'
import SectionCard from '@/components/common/SectionCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import { companyAPI } from '@/api/company'

const stats = ref([])
const applications = ref([])
const loading = ref(true)

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
        <ChartPlaceholder title="Application Funnel" subtitle="Applications received, shortlist rate, and final selections." />
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
