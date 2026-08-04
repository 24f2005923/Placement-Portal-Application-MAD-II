<template>
  <div class="portal-card p-4 p-md-5">
    <h3 class="section-heading mb-2">Edit Placement Drive</h3>
    <p class="text-muted mb-4">Update the drive details before republishing.</p>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>
    <div v-if="loading" class="text-center py-4"><div class="spinner-border text-primary"></div></div>
    <form v-else class="row g-3" @submit.prevent="handleSave">
      <div class="col-md-6"><label class="form-label">Job Role</label><input v-model="form.job_role" class="form-control" required /></div>
      <div class="col-md-6"><label class="form-label">Package</label><input v-model="form.package" class="form-control" /></div>
      <div class="col-md-6"><label class="form-label">Openings</label><input v-model.number="form.openings" class="form-control" type="number" min="1" /></div>
      <div class="col-md-6"><label class="form-label">Deadline</label><input v-model="form.deadline" class="form-control" type="date" /></div>
      <div class="col-md-6">
        <label class="form-label">Status</label>
        <select v-model="form.status" class="form-select">
          <option value="pending">Pending</option>
          <option value="closed">Closed</option>
        </select>
      </div>
      <div class="col-12"><label class="form-label">Eligibility Criteria</label><textarea v-model="form.eligibility" class="form-control" rows="4"></textarea></div>
      <div class="col-12"><label class="form-label">Description</label><textarea v-model="form.description" class="form-control" rows="3"></textarea></div>
      <div class="col-12 d-grid">
        <button class="btn btn-primary" :disabled="saving">
          <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
          {{ saving ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { companyAPI } from '@/api/company'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref('')
const form = ref({ job_role: '', package: '', openings: 1, deadline: '', status: 'pending', eligibility: '', description: '' })

async function handleSave() {
  saving.value = true
  error.value = ''
  try {
    await companyAPI.updateDrive(route.params.id, form.value)
    success.value = 'Drive updated successfully.'
    setTimeout(() => router.push('/company/dashboard'), 1500)
  } catch (err) {
    error.value = err.response?.data?.error || 'Update failed.'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await companyAPI.getDrive(route.params.id)
    const d = data.drive
    form.value = { job_role: d.job_role, package: d.package || '', openings: d.openings, deadline: d.deadline || '', status: d.status, eligibility: d.eligibility || '', description: d.description || '' }
  } catch (err) { error.value = 'Failed to load drive.' } finally { loading.value = false }
})
</script>
