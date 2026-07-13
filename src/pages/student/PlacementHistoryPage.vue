<template>
  <div class="row g-4">
    <div class="col-12">
      <div class="portal-card p-4">
        <h3 class="section-heading mb-2">Placement History</h3>
        <p class="text-muted mb-4">Past offers, joined companies, and placement timeline.</p>
        <div v-if="loading" class="text-center py-4"><div class="spinner-border text-primary"></div></div>
        <div v-else-if="history.length" class="row g-3">
          <div v-for="(item, i) in history" :key="i" class="col-md-6">
            <div class="border rounded-4 p-3">
              <div class="fw-semibold">{{ item.company }}</div>
              <div class="text-muted small">{{ item.role }} | {{ item.year }}</div>
              <div class="mt-1 small">
                <span class="badge badge-soft-success">{{ item.package }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-muted text-center py-4">No placement history yet.</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { studentAPI } from '@/api/student'

const history = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await studentAPI.getHistory()
    history.value = data.history
  } catch (err) { console.error(err) } finally { loading.value = false }
})
</script>
