<script setup>
import { ref, onMounted } from 'vue'
import StatCard from '@/components/common/StatCard.vue'
import SectionCard from '@/components/common/SectionCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import { studentAPI } from '@/api/student'

const stats = ref([])
const drives = ref([])
const loading = ref(true)

const headers = ['Company', 'Role', 'Package', 'Deadline', 'Status']
const columns = ['company_name', 'job_role', 'package', 'deadline', 'status']

onMounted(async () => {
  try {
    const [statsRes, drivesRes] = await Promise.all([
      studentAPI.getStats(),
      studentAPI.getDrives()
    ])
    stats.value = statsRes.data.stats
    drives.value = drivesRes.data.drives.slice(0, 5)
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
      <div class="col-12">
        <SectionCard title="Available Drives" subtitle="Latest placement opportunities">
          <DataTable :headers="headers" :columns="columns" :rows="drives">
            <template #status="{ row }">
              <span class="badge rounded-pill badge-soft-success">{{ row.status }}</span>
            </template>
          </DataTable>
          <p v-if="!drives.length" class="text-muted text-center py-3">No open drives right now.</p>
        </SectionCard>
      </div>
    </template>
  </div>
</template>
