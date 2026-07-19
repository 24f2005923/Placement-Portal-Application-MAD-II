<script setup>
import { ref, onMounted } from 'vue'
import SectionCard from '@/components/common/SectionCard.vue'
import DataTable from '@/components/common/DataTable.vue'
import { adminAPI } from '@/api/admin'

const companies = ref([])
const loading = ref(false)
const actionMsg = ref('')
const query = ref('')

const headers = ['Company', 'Industry', 'City', 'Contact', 'Drives', 'Status', 'Actions']
const columns = ['company_name', 'industry', 'city', 'contact_email', 'drives_count', 'approval_status', 'actions']

async function fetchCompanies() {
  loading.value = true
  try {
    const params = {}
    if (query.value) params.search = query.value
    const { data } = await adminAPI.getCompanies(params)
    companies.value = data.companies
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

async function approveCompany(company) {
  try {
    await adminAPI.approveCompany(company.id)
    company.approval_status = 'approved'
    actionMsg.value = `${company.company_name} approved.`
    setTimeout(() => { actionMsg.value = '' }, 3000)
  } catch (err) { console.error(err) }
}

async function blacklistCompany(company) {
  const bl = !company.blacklisted
  try {
    await adminAPI.blacklistCompany(company.id, bl)
    company.blacklisted = bl
    actionMsg.value = bl ? `${company.company_name} blacklisted.` : `${company.company_name} removed from blacklist.`
    setTimeout(() => { actionMsg.value = '' }, 3000)
  } catch (err) { console.error(err) }
}

function statusLabel(c) {
  if (c.blacklisted) return 'Blacklisted'
  return c.approval_status.charAt(0).toUpperCase() + c.approval_status.slice(1)
}

onMounted(fetchCompanies)
</script>

<template>
  <SectionCard title="Company Management" subtitle="Registration approvals, status tracking, and blacklist controls">
    <div v-if="actionMsg" class="alert alert-success mb-3">{{ actionMsg }}</div>
    <div class="row g-3 mb-4">
      <div class="col-12 col-lg-8">
        <input v-model="query" type="search" class="form-control" placeholder="Search by company name, industry, or city" />
      </div>
      <div class="col-12 col-lg-4 d-grid">
        <button class="btn btn-primary" @click="fetchCompanies" :disabled="loading">
          <i class="bi bi-search me-2"></i>Search
        </button>
      </div>
    </div>
    <div v-if="loading" class="text-center py-4"><div class="spinner-border text-primary"></div></div>
    <DataTable v-else :headers="headers" :columns="columns" :rows="companies">
      <template #approval_status="{ row }">
        <span class="badge rounded-pill"
          :class="row.blacklisted ? 'badge-soft-danger' : row.approval_status === 'approved' ? 'badge-soft-success' : row.approval_status === 'pending' ? 'badge-soft-warning' : 'badge-soft-danger'">
          {{ statusLabel(row) }}
        </span>
      </template>
      <template #actions="{ row }">
        <div class="btn-group btn-group-sm">
          <router-link :to="`/admin/companies/${row.id}`" class="btn btn-outline-primary">Details</router-link>
          <button class="btn btn-outline-success" @click="approveCompany(row)" :disabled="row.approval_status === 'approved'">Approve</button>
          <button class="btn btn-outline-danger" @click="blacklistCompany(row)">
            {{ row.blacklisted ? 'Unblacklist' : 'Blacklist' }}
          </button>
        </div>
      </template>
    </DataTable>
  </SectionCard>
</template>
