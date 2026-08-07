<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import SectionCard from '@/components/common/SectionCard.vue'
import { adminAPI } from '@/api/admin'

const route = useRoute()
const drive = ref(null)
const loading = ref(true)
const msg = ref('')

async function approveDrive() {
  await adminAPI.approveDrive(drive.value.id)
  drive.value.status = 'open'
  msg.value = 'Drive approved and opened.'
  setTimeout(() => { msg.value = '' }, 3000)
}

async function setStatus(status) {
  await adminAPI.setDriveStatus(drive.value.id, status)
  drive.value.status = status
  msg.value = `Drive status set to ${status}.`
  setTimeout(() => { msg.value = '' }, 3000)
}

onMounted(async () => {
  try {
    const { data } = await adminAPI.getDrive(route.params.id)
    drive.value = data.drive
  } catch (err) { console.error(err) } finally { loading.value = false }
})
</script>

<template>
  <div v-if="loading" class="text-center py-5"><div class="spinner-border text-primary"></div></div>
  <div v-else-if="drive" class="row g-4">
    <div v-if="msg" class="col-12"><div class="alert alert-success">{{ msg }}</div></div>
    <div class="col-12 col-xl-4">
      <SectionCard title="Drive Status" subtitle="Approval and publishing actions">
        <div class="mb-3">
          <h4 class="mb-1">{{ drive.company_name }}</h4>
          <div class="text-muted">{{ drive.job_role }}</div>
        </div>
        <div class="d-flex flex-wrap gap-2">
          <span class="badge badge-soft-primary">{{ drive.package }}</span>
          <span class="badge" :class="drive.status === 'open' ? 'badge-soft-success' : drive.status === 'pending' ? 'badge-soft-warning' : 'badge-soft-danger'">{{ drive.status }}</span>
        </div>
        <hr />
        <div class="d-grid gap-2">
          <button class="btn btn-primary" @click="approveDrive" :disabled="drive.status === 'open'">Approve Drive</button>
          <button class="btn btn-outline-secondary" @click="setStatus('closed')" :disabled="drive.status === 'closed'">Close Drive</button>
          <button class="btn btn-outline-danger" @click="setStatus('rejected')" :disabled="drive.status === 'rejected'">Reject Drive</button>
        </div>
      </SectionCard>
    </div>

    <div class="col-12 col-xl-8">
      <SectionCard title="Drive Details" subtitle="Complete drive configuration and eligibility">
        <div class="row g-3">
          <div class="col-md-6"><label class="form-label">Company Name</label><input class="form-control" :value="drive.company_name" readonly /></div>
          <div class="col-md-6"><label class="form-label">Job Role</label><input class="form-control" :value="drive.job_role" readonly /></div>
          <div class="col-md-6"><label class="form-label">Package</label><input class="form-control" :value="drive.package" readonly /></div>
          <div class="col-md-6"><label class="form-label">Application Deadline</label><input class="form-control" :value="drive.deadline" readonly /></div>
          <div class="col-md-6"><label class="form-label">Number of Openings</label><input class="form-control" :value="drive.openings" readonly /></div>
          <div class="col-md-6"><label class="form-label">Applications Received</label><input class="form-control" :value="drive.applications_count" readonly /></div>
          <div class="col-md-6"><label class="form-label">Drive Status</label><input class="form-control" :value="drive.status" readonly /></div>
          <div class="col-12"><label class="form-label">Eligibility Criteria</label><textarea class="form-control" rows="4" :value="drive.eligibility" readonly></textarea></div>
          <div class="col-12"><label class="form-label">Description</label><textarea class="form-control" rows="3" :value="drive.description" readonly></textarea></div>
        </div>
      </SectionCard>
    </div>
  </div>
</template>
