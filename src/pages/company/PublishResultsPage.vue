<template>
  <div class="portal-card p-4">
    <h3 class="section-heading mb-2">Publish Results</h3>
    <p class="text-muted mb-4">Mark selected students and publish the final offer list.</p>
    <div v-if="msg" class="alert alert-success">{{ msg }}</div>
    <div v-if="loading" class="text-center py-4"><div class="spinner-border text-primary"></div></div>
    <div v-else class="table-responsive">
      <table class="table align-middle">
        <thead class="table-light">
          <tr>
            <th>Student</th>
            <th>Role</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="candidate in candidates" :key="candidate.application_id">
            <td>{{ candidate.student_name }}</td>
            <td>{{ candidate.drive_role }}</td>
            <td>
              <span class="badge rounded-pill"
                :class="candidate.result?.result_status === 'selected' ? 'badge-soft-success' : candidate.result ? 'badge-soft-danger' : 'badge-soft-warning'">
                {{ candidate.result?.result_status || 'Pending' }}
              </span>
            </td>
            <td>
              <div class="btn-group btn-group-sm">
                <button class="btn btn-outline-success"
                  :disabled="candidate.result?.result_status === 'selected'"
                  @click="publishResult(candidate, 'selected')">
                  Select
                </button>
                <button class="btn btn-outline-danger"
                  :disabled="candidate.result?.result_status === 'rejected'"
                  @click="publishResult(candidate, 'rejected')">
                  Reject
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="!candidates.length">
            <td colspan="4" class="text-center text-muted py-4">No candidates in interview stage.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { companyAPI } from '@/api/company'

const candidates = ref([])
const loading = ref(false)
const msg = ref('')

async function publishResult(candidate, status) {
  try {
    await companyAPI.publishResult({ application_id: candidate.application_id, result_status: status })
    if (!candidate.result) candidate.result = {}
    candidate.result.result_status = status
    msg.value = `Result published: ${candidate.student_name} — ${status}.`
    setTimeout(() => { msg.value = '' }, 3000)
  } catch (err) { console.error(err) }
}

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await companyAPI.getResults()
    candidates.value = data.candidates
  } catch (err) { console.error(err) } finally { loading.value = false }
})
</script>
