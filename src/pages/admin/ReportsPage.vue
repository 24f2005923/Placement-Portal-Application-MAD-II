<script setup>
import { ref, onMounted } from 'vue'
import StatCard from '@/components/common/StatCard.vue'
import ChartPlaceholder from '@/components/common/ChartPlaceholder.vue'
import SectionCard from '@/components/common/SectionCard.vue'
import { adminAPI } from '@/api/admin'

const reportStats = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await adminAPI.getReportStats()
    reportStats.value = data.stats
  } catch (err) {
    console.error(err)
    reportStats.value = [
      { label: 'Placement Rate', value: 'N/A', icon: 'bi-graph-up-arrow', tone: 'primary' },
      { label: 'Drive Conversion', value: 'N/A', icon: 'bi-bar-chart-line', tone: 'success' },
      { label: 'Average Package', value: 'N/A', icon: 'bi-currency-rupee', tone: 'warning' },
      { label: 'Interview Success', value: 'N/A', icon: 'bi-check2-circle', tone: 'danger' }
    ]
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="row g-4">
    <div v-if="loading" class="col-12 text-center py-5"><div class="spinner-border text-primary"></div></div>
    <template v-else>
      <div v-for="item in reportStats" :key="item.label" class="col-12 col-sm-6 col-xl-3">
        <StatCard v-bind="item" />
      </div>
      <div class="col-12 col-xl-6">
        <ChartPlaceholder title="Placement Statistics" subtitle="Batch-wise placement trend and overall conversion." />
      </div>
      <div class="col-12 col-xl-6">
        <ChartPlaceholder title="Company Participation" subtitle="Company engagement and drive activity for the year." />
      </div>
      <div class="col-12">
        <SectionCard title="Report Modules" subtitle="Available report views">
          <div class="row g-3">
            <div class="col-md-4"><div class="border rounded-4 p-3">Student Placement Report</div></div>
            <div class="col-md-4"><div class="border rounded-4 p-3">Company Participation Report</div></div>
            <div class="col-md-4"><div class="border rounded-4 p-3">Drive Performance Report</div></div>
          </div>
        </SectionCard>
      </div>
    </template>
  </div>
</template>
