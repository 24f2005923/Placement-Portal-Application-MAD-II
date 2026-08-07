<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import SectionCard from '@/components/common/SectionCard.vue'
import AlertMessage from '@/components/common/AlertMessage.vue'
import { adminAPI } from '@/api/admin'
import { openResume } from '@/utils/resume'

const route = useRoute()
const student = ref(null)
const loading = ref(true)
const msg = ref('')

async function toggleStatus() {
  const newStatus = student.value.status === 'active' ? 'inactive' : 'active'
  await adminAPI.setStudentStatus(student.value.id, newStatus)
  student.value.status = newStatus
  msg.value = `Student ${newStatus === 'active' ? 'activated' : 'deactivated'}.`
  setTimeout(() => { msg.value = '' }, 3000)
}

onMounted(async () => {
  try {
    const { data } = await adminAPI.getStudent(route.params.id)
    student.value = data.student
  } catch (err) { console.error(err) } finally { loading.value = false }
})
</script>

<template>
  <div v-if="loading" class="text-center py-5"><div class="spinner-border text-primary"></div></div>
  <div v-else-if="student" class="row g-4">
    <div v-if="msg" class="col-12"><div class="alert alert-success">{{ msg }}</div></div>
    <div class="col-12 col-xl-4">
      <SectionCard title="Student Profile" subtitle="Profile snapshot and status controls">
        <div class="text-center">
          <div class="avatar-circle mx-auto mb-3" style="width: 72px; height: 72px; font-size: 1.5rem;">
            {{ (student.name || 'S').charAt(0) }}
          </div>
          <h4 class="mb-1">{{ student.name }}</h4>
          <p class="text-muted mb-3">{{ student.register_number }} | {{ student.department }}</p>
          <span class="badge rounded-pill" :class="student.status === 'active' ? 'badge-soft-success' : 'badge-soft-danger'">
            {{ student.status }}
          </span>
        </div>
        <hr />
        <div class="d-grid gap-2">
          <button class="btn btn-outline-danger" @click="toggleStatus">
            {{ student.status === 'inactive' ? 'Activate Student' : 'Deactivate Student' }}
          </button>
        </div>
      </SectionCard>
    </div>

    <div class="col-12 col-xl-8">
      <div class="row g-4">
        <div class="col-12">
          <SectionCard title="Personal Details" subtitle="Basic student information">
            <div class="row g-3">
              <div class="col-md-4"><label class="form-label">Name</label><input class="form-control" :value="student.name" readonly /></div>
              <div class="col-md-4"><label class="form-label">Roll No</label><input class="form-control" :value="student.register_number" readonly /></div>
              <div class="col-md-4"><label class="form-label">Department</label><input class="form-control" :value="student.department" readonly /></div>
              <div class="col-md-4"><label class="form-label">Email</label><input class="form-control" :value="student.email" readonly /></div>
              <div class="col-md-4"><label class="form-label">Phone</label><input class="form-control" :value="student.phone || 'N/A'" readonly /></div>
              <div class="col-md-4"><label class="form-label">CGPA</label><input class="form-control" :value="student.cgpa" readonly /></div>
            </div>
          </SectionCard>
        </div>
        <div class="col-12">
          <SectionCard title="Academic Information" subtitle="Education and placement readiness">
            <div class="row g-3">
              <div class="col-md-6"><label class="form-label">10th Marks (%)</label><input class="form-control" :value="student.marks_10th || 'N/A'" readonly /></div>
              <div class="col-md-6"><label class="form-label">12th Marks (%)</label><input class="form-control" :value="student.marks_12th || 'N/A'" readonly /></div>
              <div class="col-md-6"><label class="form-label">Backlogs</label><input class="form-control" :value="student.backlogs ?? 0" readonly /></div>
              <div class="col-md-6"><label class="form-label">Graduation Year</label><input class="form-control" :value="student.graduation_year || 'N/A'" readonly /></div>
              <div class="col-md-6"><label class="form-label">Preferred Role</label><input class="form-control" :value="student.preferred_role || 'N/A'" readonly /></div>
              <div class="col-md-6"><label class="form-label">Placement Status</label><input class="form-control" :value="student.placement_status" readonly /></div>
            </div>
          </SectionCard>
        </div>
        <div class="col-12 col-lg-6">
          <SectionCard title="Skills" subtitle="Key technical skills">
            <div class="d-flex flex-wrap gap-2">
              <span v-for="skill in (student.skills || [])" :key="skill" class="badge badge-soft-primary rounded-pill">{{ skill }}</span>
              <span v-if="!student.skills?.length" class="text-muted small">No skills listed.</span>
            </div>
          </SectionCard>
        </div>
        <div class="col-12 col-lg-6">
          <SectionCard title="Resume" subtitle="Latest uploaded resume">
            <div class="border border-dashed rounded-4 p-4 text-center">
              <i class="bi bi-file-earmark-pdf fs-1 text-primary"></i>
              <p class="mb-2 fw-medium mt-2">{{ student.resume_path || 'No resume uploaded' }}</p>
              <button v-if="student.resume_path" class="btn btn-sm btn-primary" @click="openResume(student.resume_path)">
                <i class="bi bi-download me-1"></i>View / Download Resume
              </button>
            </div>
          </SectionCard>
        </div>
        <div class="col-12">
          <SectionCard title="Placement History" subtitle="Past offers and final status">
            <AlertMessage message="Student profile is linked to verified placement history records." />
            <div v-if="student.placement_history?.length" class="row g-3">
              <div v-for="(h, i) in student.placement_history" :key="i" class="col-md-6">
                <div class="border rounded-4 p-3 h-100">
                  <div class="fw-semibold">{{ h.company }}</div>
                  <div class="text-muted small">{{ h.role }}</div>
                  <div class="mt-2 d-flex justify-content-between">
                    <span>{{ h.year }}</span>
                    <span class="badge badge-soft-success">{{ h.package }}</span>
                  </div>
                </div>
              </div>
            </div>
            <p v-else class="text-muted small mt-2">No placement history.</p>
          </SectionCard>
        </div>
      </div>
    </div>
  </div>
</template>
