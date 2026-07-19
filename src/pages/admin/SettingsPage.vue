<template>
  <div class="row g-4">
    <div v-if="loading" class="col-12 text-center py-5"><div class="spinner-border text-primary"></div></div>
    <template v-else>
      <div v-if="msg" class="col-12"><div class="alert alert-success">{{ msg }}</div></div>
      <div class="col-12 col-xl-6">
        <div class="portal-card p-4">
          <h5 class="section-heading mb-3">General Settings</h5>
          <form class="row g-3" @submit.prevent="saveGeneral">
            <div class="col-12">
              <label class="form-label">Portal Name</label>
              <input v-model="settings.portal_name" class="form-control" />
            </div>
            <div class="col-md-6">
              <label class="form-label">Academic Year</label>
              <input v-model="settings.academic_year" class="form-control" />
            </div>
            <div class="col-md-6">
              <label class="form-label">Notification Email</label>
              <input v-model="settings.notification_email" class="form-control" />
            </div>
            <div class="col-12 d-grid">
              <button class="btn btn-primary" :disabled="saving">
                {{ saving ? 'Saving...' : 'Save Settings' }}
              </button>
            </div>
          </form>
        </div>
      </div>
      <div class="col-12 col-xl-6">
        <div class="portal-card p-4">
          <h5 class="section-heading mb-3">Access Controls</h5>
          <div class="form-check form-switch mb-3">
            <input v-model="settings.self_registration" class="form-check-input" type="checkbox" />
            <label class="form-check-label">Allow self registration</label>
          </div>
          <div class="form-check form-switch mb-3">
            <input v-model="settings.company_approvals" class="form-check-input" type="checkbox" />
            <label class="form-check-label">Enable company approvals</label>
          </div>
          <div class="form-check form-switch mb-3">
            <input v-model="settings.instant_notifications" class="form-check-input" type="checkbox" />
            <label class="form-check-label">Publish drive notifications instantly</label>
          </div>
          <button class="btn btn-outline-primary" @click="saveGeneral" :disabled="saving">Update Access Rules</button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/api/admin'

const loading = ref(true)
const saving = ref(false)
const msg = ref('')
const settings = ref({
  portal_name: '',
  academic_year: '',
  notification_email: '',
  self_registration: true,
  company_approvals: true,
  instant_notifications: false
})

async function saveGeneral() {
  saving.value = true
  try {
    await adminAPI.updateSettings(settings.value)
    msg.value = 'Settings saved successfully.'
    setTimeout(() => { msg.value = '' }, 3000)
  } catch (err) { console.error(err) } finally { saving.value = false }
}

onMounted(async () => {
  try {
    const { data } = await adminAPI.getSettings()
    settings.value = { ...settings.value, ...data.settings }
  } catch (err) { console.error(err) } finally { loading.value = false }
})
</script>
