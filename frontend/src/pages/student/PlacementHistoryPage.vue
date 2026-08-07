<template>
  <div class="row g-4">
    <div class="col-12">
      <div class="portal-card p-4">
        <h3 class="section-heading mb-2">Placement History & Offer Records</h3>
        <p class="text-muted mb-4">Review all successful placement offers, packages, company feedback, and official offer letters.</p>

        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary"></div>
        </div>
        <div v-else-if="history.length" class="row g-3">
          <div v-for="(item, i) in history" :key="i" class="col-12 col-md-6 col-xl-4">
            <div class="border rounded-4 p-4 bg-white shadow-sm h-100 d-flex flex-column justify-content-between">
              <div>
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <h5 class="fw-bold text-success mb-0">🎉 {{ item.company }}</h5>
                  <span class="badge badge-soft-success px-3 py-1">{{ item.package }}</span>
                </div>
                <div class="fw-medium text-dark mb-1">{{ item.drive_title || item.role }}</div>
                <div class="small text-muted mb-3">Role: {{ item.role }} • Year: {{ item.year }}</div>

                <div v-if="item.remarks" class="small bg-light p-2 rounded text-secondary mb-3">
                  <i class="bi bi-chat-quote me-1"></i><strong>Feedback:</strong> {{ item.remarks }}
                </div>
              </div>

              <div class="mt-3 pt-3 border-top d-grid" v-if="item.application_id">
                <a
                  :href="studentAPI.getOfferLetterUrl(item.application_id)"
                  target="_blank"
                  class="btn btn-outline-success btn-sm rounded-pill"
                >
                  <i class="bi bi-file-earmark-arrow-down me-1"></i>Download Offer Letter
                </a>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-muted text-center py-5">
          <i class="bi bi-award fs-1 d-block mb-2 text-secondary"></i>
          No placement records confirmed yet.
        </div>
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
    history.value = data.history || []
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})
</script>
