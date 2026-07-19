<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import SectionCard from '@/components/common/SectionCard.vue'
import { adminAPI } from '@/api/admin'

const route = useRoute()
const company = ref(null)
const loading = ref(true)
const msg = ref('')

async function approve() {
  await adminAPI.approveCompany(company.value.id)
  company.value.approval_status = 'approved'
  msg.value = 'Company approved.'
  setTimeout(() => { msg.value = '' }, 3000)
}

async function toggleBlacklist() {
  const bl = !company.value.blacklisted
  await adminAPI.blacklistCompany(company.value.id, bl)
  company.value.blacklisted = bl
  msg.value = bl ? 'Company blacklisted.' : 'Company removed from blacklist.'
  setTimeout(() => { msg.value = '' }, 3000)
}

onMounted(async () => {
  try {
    const { data } = await adminAPI.getCompany(route.params.id)
    company.value = data.company
  } catch (err) { console.error(err) } finally { loading.value = false }
})
</script>

<template>
  <div v-if="loading" class="text-center py-5"><div class="spinner-border text-primary"></div></div>
  <div v-else-if="company" class="row g-4">
    <div v-if="msg" class="col-12"><div class="alert alert-success">{{ msg }}</div></div>
    <div class="col-12 col-xl-4">
      <SectionCard title="Company Details" subtitle="Information and action summary">
        <h4 class="mb-1">{{ company.company_name }}</h4>
        <p class="text-muted">{{ company.industry }} | {{ company.city }}</p>
        <div class="d-flex gap-2 flex-wrap">
          <span class="badge rounded-pill" :class="company.blacklisted ? 'badge-soft-danger' : company.approval_status === 'approved' ? 'badge-soft-success' : 'badge-soft-warning'">
            {{ company.blacklisted ? 'Blacklisted' : company.approval_status }}
          </span>
          <span class="badge rounded-pill badge-soft-primary">{{ company.drives_count }} Drives</span>
        </div>
        <hr />
        <div class="d-grid gap-2">
          <button class="btn btn-primary" @click="approve" :disabled="company.approval_status === 'approved'">Approve</button>
          <button class="btn btn-outline-danger" @click="toggleBlacklist">
            {{ company.blacklisted ? 'Remove Blacklist' : 'Blacklist Company' }}
          </button>
        </div>
      </SectionCard>
    </div>
    <div class="col-12 col-xl-8">
      <div class="row g-4">
        <div class="col-md-6">
          <SectionCard title="Company Information" subtitle="Registered profile details">
            <div class="text-muted small">Company Name</div>
            <div class="fw-semibold mb-3">{{ company.company_name }}</div>
            <div class="text-muted small">Industry</div>
            <div class="fw-semibold mb-3">{{ company.industry || 'N/A' }}</div>
            <div class="text-muted small">City</div>
            <div class="fw-semibold mb-3">{{ company.city || 'N/A' }}</div>
            <div class="text-muted small">Website</div>
            <div class="fw-semibold">{{ company.website || 'N/A' }}</div>
          </SectionCard>
        </div>
        <div class="col-md-6">
          <SectionCard title="Contact Information" subtitle="Primary point of contact">
            <div class="text-muted small">Email</div>
            <div class="fw-semibold mb-3">{{ company.contact_email || company.email || 'N/A' }}</div>
            <div class="text-muted small">Phone</div>
            <div class="fw-semibold mb-3">{{ company.contact_phone || 'N/A' }}</div>
            <div class="text-muted small">Contact Person</div>
            <div class="fw-semibold">{{ company.contact_person || 'N/A' }}</div>
          </SectionCard>
        </div>
        <div class="col-12">
          <SectionCard title="Active Placement Drives" subtitle="Drives associated with this company">
            <div v-if="company.drives?.length" class="row g-3">
              <div v-for="drive in company.drives" :key="drive.id" class="col-md-6">
                <div class="border rounded-4 p-3">
                  <div class="fw-semibold">{{ drive.job_role }}</div>
                  <div class="text-muted small">{{ drive.package }} | {{ drive.openings }} openings</div>
                  <div class="mt-2 d-flex justify-content-between">
                    <span class="badge badge-soft-primary">{{ drive.deadline || 'TBD' }}</span>
                    <span class="badge" :class="drive.status === 'open' ? 'badge-soft-success' : 'badge-soft-warning'">{{ drive.status }}</span>
                  </div>
                </div>
              </div>
            </div>
            <p v-else class="text-muted small">No drives yet.</p>
          </SectionCard>
        </div>
      </div>
    </div>
  </div>
</template>
