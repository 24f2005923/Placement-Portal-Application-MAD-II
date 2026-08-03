<template>
  <div class="d-flex flex-column gap-4">
    <!-- Existing Placement Drives Section -->
    <SectionCard title="Your Placement Drives" subtitle="Manage and monitor all placement drives submitted by your company">
      <div v-if="drivesError" class="alert alert-danger mb-3">{{ drivesError }}</div>
      <div v-if="loadingDrives" class="text-center py-4">
        <div class="spinner-border text-primary"></div>
      </div>
      <template v-else>
        <DataTable v-if="drives.length" :headers="headers" :columns="columns" :rows="drives">
          <template #deadline="{ row }">
            {{ row.deadline || 'N/A' }}
          </template>
          <template #applications_count="{ row }">
            <span class="badge badge-soft-info">{{ row.applications_count || 0 }} Applications</span>
          </template>
          <template #status="{ row }">
            <span class="badge rounded-pill"
              :class="row.status === 'open' || row.status === 'approved' ? 'badge-soft-success' : row.status === 'pending' ? 'badge-soft-warning' : 'badge-soft-danger'">
              {{ row.status }}
            </span>
          </template>
          <template #actions="{ row }">
            <div class="btn-group btn-group-sm">
              <router-link :to="`/company/drives/${row.id}/edit`" class="btn btn-outline-primary">
                <i class="bi bi-pencil me-1"></i>Edit
              </router-link>
              <button class="btn btn-outline-danger" @click="handleDelete(row.id)" :disabled="deletingId === row.id">
                <span v-if="deletingId === row.id" class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-trash me-1"></i>Delete
              </button>
            </div>
          </template>
        </DataTable>
        <p v-else class="text-muted text-center py-4 mb-0">No placement drives found. Create your first drive using the form below.</p>
      </template>
    </SectionCard>

    <!-- Create Placement Drive Form Section -->
    <div class="portal-card p-4 p-md-5">
      <h3 class="section-heading mb-2">Create Placement Drive</h3>
      <p class="text-muted mb-4">Build a new placement drive and submit it for approval.</p>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>
      <div v-if="success" class="alert alert-success">{{ success }}</div>

      <form class="row g-3" @submit.prevent="handleSubmit">
        <div class="col-md-6">
          <label class="form-label">Job Role</label>
          <input v-model="form.job_role" class="form-control" placeholder="Software Engineer" required />
        </div>
        <div class="col-md-6">
          <label class="form-label">Package</label>
          <input v-model="form.package" class="form-control" placeholder="6.5 LPA" />
        </div>
        <div class="col-md-6">
          <label class="form-label">Openings</label>
          <input v-model.number="form.openings" class="form-control" type="number" min="1" placeholder="50" />
        </div>
        <div class="col-md-6">
          <label class="form-label">Deadline</label>
          <input v-model="form.deadline" class="form-control" type="date" />
        </div>
        <div class="col-12">
          <label class="form-label">Eligibility Criteria</label>
          <textarea v-model="form.eligibility" class="form-control" rows="4" placeholder="CGPA >= 7.0, No active backlogs"></textarea>
        </div>
        <div class="col-12">
          <label class="form-label">Description (optional)</label>
          <textarea v-model="form.description" class="form-control" rows="3"></textarea>
        </div>
        <div class="col-12 d-grid">
          <button class="btn btn-primary" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            {{ loading ? 'Submitting...' : 'Submit Drive' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import SectionCard from '@/components/common/SectionCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import { companyAPI } from '@/api/company'

const router = useRouter()

const drives = ref([])
const loadingDrives = ref(true)
const drivesError = ref('')
const deletingId = ref(null)

const loading = ref(false)
const error = ref('')
const success = ref('')
const form = ref({ job_role: '', package: '', openings: 1, deadline: '', eligibility: '', description: '' })

const headers = ['Job Role', 'Package', 'Openings', 'Deadline', 'Applications', 'Status', 'Actions']
const columns = ['job_role', 'package', 'openings', 'deadline', 'applications_count', 'status', 'actions']

async function fetchDrives() {
  loadingDrives.value = true
  drivesError.value = ''
  try {
    const { data } = await companyAPI.getDrives()
    drives.value = data.drives || []
  } catch (err) {
    drivesError.value = err.response?.data?.error || 'Failed to fetch placement drives.'
  } finally {
    loadingDrives.value = false
  }
}

async function handleSubmit() {
  loading.value = true
  error.value = ''
  success.value = ''
  try {
    await companyAPI.createDrive(form.value)
    success.value = 'Placement drive created successfully!'
    form.value = { job_role: '', package: '', openings: 1, deadline: '', eligibility: '', description: '' }
    await fetchDrives()
    setTimeout(() => { success.value = '' }, 4000)
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to submit drive.'
  } finally {
    loading.value = false
  }
}

async function handleDelete(id) {
  if (!confirm('Are you sure you want to delete this placement drive?')) return
  deletingId.value = id
  try {
    await companyAPI.deleteDrive(id)
    drives.value = drives.value.filter(d => d.id !== id)
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to delete drive.')
  } finally {
    deletingId.value = null
  }
}

onMounted(fetchDrives)
</script>
