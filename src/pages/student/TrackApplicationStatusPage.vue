<template>
  <div class="portal-card p-4">
    <h3 class="section-heading mb-2">Track Application Status</h3>
    <p class="text-muted mb-4">Monitor the progress of your submitted applications.</p>
    <div v-if="loading" class="text-center py-4"><div class="spinner-border text-primary"></div></div>
    <div v-else class="table-responsive">
      <table class="table align-middle">
        <thead class="table-light">
          <tr>
            <th>Drive</th>
            <th>Company</th>
            <th>Status</th>
            <th>Stage</th>
            <th>Progress</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="app in applications" :key="app.id">
            <td>{{ app.drive_title }}</td>
            <td>{{ app.company_name }}</td>
            <td>
              <span class="badge rounded-pill"
                :class="app.application_status === 'selected' ? 'badge-soft-success' : app.application_status === 'rejected' ? 'badge-soft-danger' : app.application_status === 'interview' ? 'badge-soft-warning' : 'badge-soft-primary'">
                {{ app.application_status }}
              </span>
            </td>
            <td>{{ app.stage }}</td>
            <td style="min-width: 120px;">
              <div class="progress" style="height: 8px;">
                <div class="progress-bar" :style="{ width: app.progress + '%' }"></div>
              </div>
              <small class="text-muted">{{ app.progress }}%</small>
            </td>
          </tr>
          <tr v-if="!applications.length">
            <td colspan="5" class="text-center text-muted py-4">No applications yet.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { studentAPI } from '@/api/student'

const applications = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await studentAPI.getApplications()
    applications.value = data.applications
  } catch (err) { console.error(err) } finally { loading.value = false }
})
</script>
