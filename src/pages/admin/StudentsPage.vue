<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import SectionCard from '@/components/common/SectionCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import Pagination from '@/components/common/Pagination.vue'
import { adminAPI } from '@/api/admin'

const router = useRouter()
const query = ref('')
const status = ref('All')
const students = ref([])
const total = ref(0)
const page = ref(1)
const pages = ref(1)
const loading = ref(false)
const actionMsg = ref('')

const headers = ['Student', 'Roll No', 'Department', 'CGPA', 'Status', 'Actions']
const columns = ['name', 'register_number', 'department', 'cgpa', 'placement_status', 'actions']

async function fetchStudents() {
  loading.value = true
  try {
    const params = { page: page.value, per_page: 20 }
    if (query.value) params.search = query.value
    if (status.value !== 'All') params.status = status.value
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
    actionMsg.value = `Student ${newStatus === 'active' ? 'activated' : 'deactivated'}.`
    setTimeout(() => { actionMsg.value = '' }, 3000)
  } catch (err) {
    console.error(err)
  }
}

onMounted(fetchStudents)
</script>

<template>
  <div class="row g-4">
    <div class="col-12">
      <SectionCard title="Student Management" subtitle="Search, filter, and manage student placement records">
        <div v-if="actionMsg" class="alert alert-success alert-dismissible">{{ actionMsg }}</div>
        <div class="row g-3 mb-4">
          <div class="col-12 col-lg-6">
            <input v-model="query" type="search" class="form-control form-control-lg" placeholder="Search student by name or roll number" />
          </div>
          <div class="col-12 col-lg-3">
            <select v-model="status" class="form-select form-select-lg">
              <option>All</option>
              <option>Placed</option>
              <option>Applied</option>
              <option>Interview</option>
              <option>Inactive</option>
            </select>
          </div>
          <div class="col-12 col-lg-3 d-grid">
            <button class="btn btn-primary btn-lg" @click="fetchStudents" :disabled="loading">
              <i class="bi bi-funnel me-2"></i>Apply Filters
            </button>
          </div>
        </div>

        <div v-if="loading" class="text-center py-4"><div class="spinner-border text-primary"></div></div>
        <DataTable v-else :headers="headers" :columns="columns" :rows="students">
          <template #name="{ row }">
            <div class="fw-semibold">{{ row.name }}</div>
            <small class="text-muted">{{ (row.skills || []).join(' • ') }}</small>
          </template>
          <template #placement_status="{ row }">
            <span class="badge rounded-pill"
              :class="row.placement_status === 'Placed' ? 'badge-soft-success' : row.placement_status === 'Interview' ? 'badge-soft-warning' : row.status === 'inactive' ? 'badge-soft-danger' : 'badge-soft-primary'">
              {{ row.status === 'inactive' ? 'Inactive' : row.placement_status }}
            </span>
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
