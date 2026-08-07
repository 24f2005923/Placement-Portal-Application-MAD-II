<script setup>
import { ref, onMounted } from 'vue'
import SectionCard from '@/components/common/SectionCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import Pagination from '@/components/common/Pagination.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import FeedbackAlert from '@/components/common/FeedbackAlert.vue'
import { adminAPI } from '@/api/admin'
import { usePageFeedback } from '@/composables/usePageFeedback'

const query = ref('')
const students = ref([])
const total = ref(0)
const page = ref(1)
const pages = ref(1)
const loading = ref(false)
const { successMsg, errorMsg, showSuccess, clearMessages } = usePageFeedback()

const headers = ['Student', 'Roll No', 'Department', 'CGPA', 'Status', 'Actions']
const columns = ['name', 'register_number', 'department', 'cgpa', 'placement_status', 'actions']

async function fetchStudents() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: 20 }
    if (query.value) params.search = query.value
    const { data } = await adminAPI.getStudents(params)
    students.value = data.students
    total.value = data.total
    pages.value = data.pages
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function toggleStatus(student) {
  const newStatus = student.status === 'active' ? 'inactive' : 'active'
  try {
    await adminAPI.setStudentStatus(student.id, newStatus)
    student.status = newStatus
    showSuccess(`Student ${newStatus === 'active' ? 'activated' : 'deactivated'}.`)
  } catch (err) {
    console.error(err)
  }
}

onMounted(fetchStudents)
</script>

<template>
  <div class="row g-4">
    <div class="col-12">
      <SectionCard title="Student Management" subtitle="Search and manage student placement records">
        <FeedbackAlert 
          :success="successMsg"
          :error="errorMsg"
          @clear-success="clearMessages"
          @clear-error="clearMessages"
        />
        <div class="row g-3 mb-4">
          <div class="col-12 col-lg-9">
            <input v-model="query" type="search" class="form-control form-control-lg" placeholder="Search student by name or roll number" />
          </div>
          <div class="col-12 col-lg-3 d-grid">
            <button class="btn btn-primary btn-lg" @click="fetchStudents" :disabled="loading">
              <i class="bi bi-search me-2"></i>Search
            </button>
          </div>
        </div>

        <LoadingSpinner v-if="loading" />
        <EmptyState 
          v-else-if="students.length === 0" 
          title="No students found." 
          icon="bi-people"
        />
        <DataTable v-else :headers="headers" :columns="columns" :rows="students">
          <template #name="{ row }">
            <div class="fw-semibold">{{ row.name }}</div>
            <small class="text-muted">{{ (row.skills || []).join(' • ') }}</small>
          </template>
          <template #placement_status="{ row }">
            <StatusBadge 
              variant="student" 
              :row="row" 
              :label="row.status === 'inactive' ? 'Inactive' : row.placement_status" 
            />
          </template>
          <template #actions="{ row }">
            <div class="btn-group btn-group-sm">
              <router-link :to="`/admin/students/${row.id}`" class="btn btn-outline-primary">View</router-link>
              <button class="btn btn-outline-danger" @click="toggleStatus(row)">
                {{ row.status === 'inactive' ? 'Activate' : 'Deactivate' }}
              </button>
            </div>
          </template>
        </DataTable>

        <div class="d-flex justify-content-between align-items-center mt-4">
          <small class="text-muted">Showing {{ students.length }} of {{ total }} students</small>
          <Pagination :page="page" :total="pages" />
        </div>
      </SectionCard>
    </div>
  </div>
</template>
