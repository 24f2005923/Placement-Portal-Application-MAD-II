<script setup>
import { ref, onMounted } from 'vue'
import StatCard from '@/components/common/StatCard.vue'
import SectionCard from '@/components/common/SectionCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import { adminAPI } from '@/api/admin'

const stats = ref([])
const drives = ref([])
const activities = ref([])
const loading = ref(true)

const driveHeaders = ['Company', 'Role', 'Package', 'Deadline', 'Status']
const driveColumns = ['company_name', 'job_role', 'package', 'deadline', 'status']

onMounted(async () => {
  try {
    const [statsRes, drivesRes, activitiesRes] = await Promise.all([
      adminAPI.getStats(),
      adminAPI.getDrives({ per_page: 5 }),
      adminAPI.getActivities()
    ])
    stats.value = statsRes.data.stats
    drives.value = drivesRes.data.drives
    activities.value = activitiesRes.data.activities || []
  } catch (err) {
    console.error('Dashboard load error:', err)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="row g-4">
    <div v-if="loading" class="col-12 text-center py-5">
      <div class="spinner-border text-primary"></div>
    </div>
    <template v-else>
      <div v-for="item in stats" :key="item.label" class="col-12 col-sm-6 col-xl-3">
        <StatCard v-bind="item" />
      </div>

      <div class="col-12 col-xl-8">
        <SectionCard title="Active Placement Drives" subtitle="Current drives in progress">
          <DataTable :headers="driveHeaders" :columns="driveColumns" :rows="drives">
            <template #status="{ row }">
              <span class="badge rounded-pill" :class="row.status === 'open' ? 'badge-soft-success' : row.status === 'pending' ? 'badge-soft-warning' : 'badge-soft-danger'">
                {{ row.status }}
              </span>
            </template>
          </DataTable>
        </SectionCard>
      </div>

      <div class="col-12 col-xl-4">
        <SectionCard title="Recent Activity" subtitle="Latest portal events">
          <div v-if="activities.length === 0" class="text-muted small py-3 text-center">No recent activity.</div>
          <ul v-else class="list-group list-group-flush">
            <li v-for="(act, idx) in activities" :key="idx" class="list-group-item px-0 bg-transparent">
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <div class="fw-medium small">{{ act.title }}</div>
                  <div class="text-muted extra-small" style="font-size: 0.75rem;">{{ act.meta }}</div>
                </div>
                <span class="badge badge-soft-info ms-2">Activity</span>
              </div>
            </li>
          </ul>
        </SectionCard>
      </div>
    </template>
  </div>
</template>
