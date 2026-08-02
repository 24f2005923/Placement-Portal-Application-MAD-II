<template>
  <div class="row g-4">
    <div v-if="loading" class="col-12 text-center py-5"><div class="spinner-border text-primary"></div></div>
    <template v-else>
      <div v-if="msg" class="col-12"><div class="alert alert-success">{{ msg }}</div></div>
      <div v-if="error" class="col-12"><div class="alert alert-danger">{{ error }}</div></div>
      <div class="col-12 col-xl-4">
        <div class="portal-card p-4">
          <div class="avatar-circle mx-auto mb-3" style="width: 72px; height: 72px; font-size: 1.5rem;">
            {{ (form.company_name || 'C').charAt(0) }}
          </div>
          <h4 class="text-center mb-1">{{ form.company_name }}</h4>
          <p class="text-center text-muted">{{ form.industry }}</p>
          <div class="d-flex justify-content-center gap-2 flex-wrap">
            <span class="badge" :class="company?.approval_status === 'approved' ? 'badge-soft-success' : 'badge-soft-warning'">
              {{ company?.approval_status || 'pending' }}
            </span>
          </div>
        </div>
      </div>
      <div class="col-12 col-xl-8">
        <div class="portal-card p-4">
          <h5 class="section-heading mb-3">Company Profile</h5>
          <form class="row g-3" @submit.prevent="handleSave">
            <div class="col-md-6"><label class="form-label">Company Name</label><input v-model="form.company_name" class="form-control" /></div>
            <div class="col-md-6"><label class="form-label">Industry</label><input v-model="form.industry" class="form-control" /></div>
            <div class="col-md-6"><label class="form-label">Contact Person</label><input v-model="form.contact_person" class="form-control" /></div>
            <div class="col-md-6"><label class="form-label">Contact Email</label><input v-model="form.contact_email" class="form-control" /></div>
            <div class="col-md-6">
              <label class="form-label">Contact Phone</label>
              <input
                v-model="form.contact_phone"
                type="tel"
                maxlength="10"
                class="form-control"
                placeholder="10-digit phone number"
                @input="onPhoneInput"
              />
            </div>
            <div class="col-md-6"><label class="form-label">Website</label><input v-model="form.website" class="form-control" /></div>
            <div class="col-12"><label class="form-label">Description</label><textarea v-model="form.description" class="form-control" rows="4"></textarea></div>
            <div class="col-12 d-grid d-md-flex gap-2">
              <button class="btn btn-primary" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                {{ saving ? 'Saving...' : 'Update Profile' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { companyAPI } from '@/api/company'
import { isValidPhone } from '@/utils/validators'

const company = ref(null)
const loading = ref(true)
const saving = ref(false)
const msg = ref('')
const error = ref('')
const form = ref({ company_name: '', industry: '', contact_person: '', contact_email: '', contact_phone: '', website: '', description: '' })

function onPhoneInput(e) {
  if (form.value.contact_phone) {
    form.value.contact_phone = e.target.value.replace(/\D/g, '').slice(0, 10)
  }
}

async function handleSave() {
  if (form.value.contact_phone && !isValidPhone(form.value.contact_phone)) {
    error.value = 'Contact phone must be exactly 10 digits.'
    return
  }

  saving.value = true
  error.value = ''
  msg.value = ''
  try {
    const { data } = await companyAPI.updateProfile(form.value)
    company.value = data.company
    msg.value = 'Profile updated successfully.'
    setTimeout(() => { msg.value = '' }, 3000)
  } catch (err) {
    error.value = err.response?.data?.error || 'Update failed.'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await companyAPI.getProfile()
    company.value = data.company
    Object.assign(form.value, {
      company_name: data.company.company_name,
      industry: data.company.industry || '',
      contact_person: data.company.contact_person || '',
      contact_email: data.company.contact_email || '',
      contact_phone: data.company.contact_phone || '',
      website: data.company.website || '',
      description: data.company.description || ''
    })
  } catch (err) { console.error(err) } finally { loading.value = false }
})
</script>
