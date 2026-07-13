<template>
  <div class="row g-4">
    <div class="col-12 col-xl-8">
      <div class="portal-card p-4">
        <h3 class="section-heading mb-2">Profile Management</h3>
        <p class="text-muted mb-4">Update academic details, skills, and contact information.</p>
        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        <div v-if="success" class="alert alert-success">{{ success }}</div>
        <div v-if="loading" class="text-center py-4"><div class="spinner-border text-primary"></div></div>
        <form v-else class="row g-3" @submit.prevent="handleSave">
          <div class="col-md-6"><label class="form-label">Full Name</label><input v-model="form.name" class="form-control" required /></div>
          <div class="col-md-6"><label class="form-label">Roll Number</label><input v-model="form.register_number" class="form-control" readonly /></div>
          <div class="col-md-6"><label class="form-label">Email</label><input v-model="form.email" class="form-control" type="email" /></div>
          <div class="col-md-6"><label class="form-label">CGPA</label><input v-model.number="form.cgpa" class="form-control" type="number" step="0.01" /></div>
          <div class="col-md-6"><label class="form-label">Phone</label><input v-model="form.phone" class="form-control" /></div>
          <div class="col-md-6"><label class="form-label">Department</label><input v-model="form.department" class="form-control" /></div>
          <div class="col-12"><label class="form-label">Skills (comma-separated)</label><input v-model="skillsInput" class="form-control" placeholder="Vue.js, Node.js, SQL" /></div>
          <div class="col-md-6"><label class="form-label">Preferred Role</label><input v-model="form.preferred_role" class="form-control" /></div>
          <div class="col-md-6"><label class="form-label">Graduation Year</label><input v-model.number="form.graduation_year" class="form-control" type="number" /></div>
          <div class="col-12 d-grid">
            <button class="btn btn-primary" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
              {{ saving ? 'Saving...' : 'Save Profile' }}
            </button>
          </div>
        </form>
      </div>
    </div>
    <div class="col-12 col-xl-4">
      <div class="portal-card p-4 h-100">
        <h5 class="section-heading mb-3">Profile Completeness</h5>
        <div class="progress mb-2" style="height: 10px;">
          <div class="progress-bar" :style="{ width: completeness + '%' }"></div>
        </div>
        <small class="text-muted">{{ completeness }}% complete</small>
        <div class="mt-4">
          <div class="small text-muted mb-2">Placement Status</div>
          <span class="badge badge-soft-primary">{{ form.placement_status || 'Not Placed' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { studentAPI } from '@/api/student'

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref('')
const form = ref({ name: '', email: '', register_number: '', cgpa: '', phone: '', department: '', preferred_role: '', graduation_year: '', placement_status: '' })
const skillsInput = ref('')

const completeness = computed(() => {
  const fields = [form.value.name, form.value.email, form.value.cgpa, form.value.phone, form.value.department, skillsInput.value, form.value.preferred_role, form.value.graduation_year]
  const filled = fields.filter(Boolean).length
  return Math.round((filled / fields.length) * 100)
})

async function handleSave() {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    await studentAPI.updateProfile({ ...form.value, skills: skillsInput.value })
    success.value = 'Profile updated successfully.'
    setTimeout(() => { success.value = '' }, 3000)
  } catch (err) {
    error.value = err.response?.data?.error || 'Update failed.'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await studentAPI.getProfile()
    const s = data.student
    form.value = { name: s.name, email: s.email, register_number: s.register_number, cgpa: s.cgpa, phone: s.phone || '', department: s.department, preferred_role: s.preferred_role || '', graduation_year: s.graduation_year || '', placement_status: s.placement_status }
    skillsInput.value = (s.skills || []).join(', ')
  } catch (err) { console.error(err) } finally { loading.value = false }
})
</script>
