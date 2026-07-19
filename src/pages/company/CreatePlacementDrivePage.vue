<template>
  <div class="portal-card p-4 p-md-5">
    <h3 class="section-heading mb-2">Create Placement Drive</h3>
    <p class="text-muted mb-4">Build a new placement drive and submit it for approval.</p>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>
    <form class="row g-3" @submit.prevent="handleSubmit">
      <div class="col-md-6"><label class="form-label">Job Role</label><input v-model="form.job_role" class="form-control" placeholder="Software Engineer" required /></div>
      <div class="col-md-6"><label class="form-label">Package</label><input v-model="form.package" class="form-control" placeholder="6.5 LPA" /></div>
      <div class="col-md-6"><label class="form-label">Openings</label><input v-model.number="form.openings" class="form-control" type="number" min="1" placeholder="50" /></div>
      <div class="col-md-6"><label class="form-label">Deadline</label><input v-model="form.deadline" class="form-control" type="date" /></div>
      <div class="col-12"><label class="form-label">Eligibility Criteria</label><textarea v-model="form.eligibility" class="form-control" rows="4" placeholder="CGPA >= 7.0, No active backlogs"></textarea></div>
      <div class="col-12"><label class="form-label">Description (optional)</label><textarea v-model="form.description" class="form-control" rows="3"></textarea></div>
      <div class="col-12 d-grid">
        <button class="btn btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? 'Submitting...' : 'Submit Drive' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { companyAPI } from '@/api/company'

const router = useRouter()
const loading = ref(false)
const error = ref('')
const success = ref('')
const form = ref({ job_role: '', package: '', openings: 1, deadline: '', eligibility: '', description: '' })

async function handleSubmit() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    await companyAPI.createDrive(form.value)
    success.value = 'Drive submitted for admin approval!'
    setTimeout(() => router.push('/company/dashboard'), 1500)
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to submit drive.'
  } finally {
    loading.value = false
  }
}
</script>
