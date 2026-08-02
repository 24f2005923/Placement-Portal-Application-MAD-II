<template>
  <div class="row g-4">
    <div v-if="loading" class="col-12 text-center py-5">
      <div class="spinner-border text-primary"></div>
    </div>
    <template v-else>
      <!-- Stat Cards -->
      <div v-for="item in stats" :key="item.label" class="col-12 col-sm-6 col-xl-3">
        <StatCard v-bind="item" />
      </div>

      <!-- Upcoming Interviews Card -->
      <div class="col-12 col-xl-6">
        <SectionCard title="Scheduled Interviews" subtitle="Upcoming interview rounds and meeting details">
          <div v-if="interviews.length === 0" class="border rounded-4 p-4 text-center text-muted">
            <i class="bi bi-calendar-check fs-2 d-block mb-1 text-secondary"></i>
            No interviews scheduled at the moment.
          </div>
          <div v-else class="list-group list-group-flush">
            <div v-for="iv in interviews" :key="iv.id" class="list-group-item px-0 py-3 border-bottom">
              <div class="d-flex justify-content-between align-items-start mb-1">
                <div>
                  <h6 class="fw-semibold text-primary mb-1">{{ iv.company_name }}</h6>
                  <div class="small fw-medium text-dark">{{ iv.drive_title }} — {{ iv.round_name || 'Interview Round' }}</div>
                </div>
                <span class="badge badge-soft-info text-capitalize">{{ iv.interview_mode || 'online' }}</span>
              </div>
              <div class="small text-muted mb-2">
                <i class="bi bi-calendar3 me-1"></i>{{ iv.interview_date || 'Date TBD' }}
                <i class="bi bi-clock ms-2 me-1"></i>{{ iv.interview_time || 'Time TBD' }}
              </div>
              <div v-if="iv.interview_link" class="small mb-2">
                <a :href="iv.interview_link" target="_blank" class="btn btn-sm btn-outline-primary rounded-pill px-3">
                  <i class="bi bi-camera-video me-1"></i>Join Interview Link
                </a>
              </div>
              <div v-if="iv.remarks" class="small bg-light p-2 rounded text-secondary">
                <i class="bi bi-chat-quote me-1"></i><strong>Company Note:</strong> {{ iv.remarks }}
              </div>
            </div>
          </div>
        </SectionCard>
      </div>

      <!-- Placements & Offer Letters Card -->
      <div class="col-12 col-xl-6">
        <SectionCard title="Placement Confirmations & Offers" subtitle="Official offer letters and placement results">
          <div v-if="placedApplications.length === 0" class="border rounded-4 p-4 text-center text-muted">
            <i class="bi bi-award fs-2 d-block mb-1 text-secondary"></i>
            No placement offers finalized yet.
          </div>
          <div v-else class="list-group list-group-flush">
            <div v-for="app in placedApplications" :key="app.id" class="list-group-item px-0 py-3 border-bottom">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <h6 class="fw-bold text-success mb-1">🎉 {{ app.company_name }}</h6>
                  <div class="small fw-medium text-dark">{{ app.drive_title || app.drive_role }}</div>
                  <div class="small text-muted">{{ app.drive_package }}</div>
                </div>
                <a
                  :href="studentAPI.getOfferLetterUrl(app.id)"
                  target="_blank"
                  class="btn btn-sm btn-success rounded-pill px-3"
                >
                  <i class="bi bi-file-earmark-arrow-down me-1"></i>Offer Letter
                </a>
              </div>
              <div v-if="app.result?.remarks" class="small bg-light p-2 rounded mt-2 text-secondary">
                <i class="bi bi-chat-left-text me-1"></i><strong>Company Feedback:</strong> {{ app.result.remarks }}
              </div>
            </div>
          </div>
        </SectionCard>
      </div>

      <!-- Available Drives Table -->
      <div class="col-12">
        <SectionCard title="Available Placement Drives" subtitle="Latest opportunities open for application">
          <DataTable :headers="driveHeaders" :columns="driveColumns" :rows="drives">
            <template #company_name="{ row }">
              <div class="fw-semibold text-dark">{{ row.company_name }}</div>
              <small class="text-muted">{{ row.title }}</small>
            </template>
            <template #package="{ row }">
              <span class="fw-semibold text-success">{{ row.package || 'As per policy' }}</span>
            </template>
            <template #status="{ row }">
              <span class="badge rounded-pill badge-soft-success">{{ row.status }}</span>
            </template>
            <template #action="{ row }">
              <router-link
                v-if="!row.already_applied"
                :to="`/student/drives/${row.id}/apply`"
                class="btn btn-sm btn-primary rounded-pill px-3"
              >
                Apply
              </router-link>
              <span v-else class="badge badge-soft-success">Applied</span>
            </template>
          </DataTable>
          <p v-if="!drives.length" class="text-muted text-center py-3">No open placement drives at the moment.</p>
        </SectionCard>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import StatCard from '@/components/common/StatCard.vue'
import SectionCard from '@/components/common/SectionCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import { studentAPI } from '@/api/student'

const stats = ref([])
const drives = ref([])
const interviews = ref([])
const applications = ref([])
const loading = ref(true)

const driveHeaders = ['Company & Drive', 'Role', 'Package', 'Deadline', 'Status', 'Action']
const driveColumns = ['company_name', 'job_role', 'package', 'deadline', 'status', 'action']

const placedApplications = computed(() => {
  return applications.value.filter((a) => a.application_status === 'selected')
})

onMounted(async () => {
  try {
    const [statsRes, drivesRes, interviewsRes, appsRes] = await Promise.all([
      studentAPI.getStats(),
      studentAPI.getDrives(),
      studentAPI.getInterviews(),
      studentAPI.getApplications()
    ])
    stats.value = statsRes.data.stats
    drives.value = (drivesRes.data.drives || []).slice(0, 5)
    interviews.value = interviewsRes.data.interviews || []
    applications.value = appsRes.data.applications || []
  } catch (err) {
    console.error('Dashboard error:', err)
  } finally {
    loading.value = false
  }
})
</script>
