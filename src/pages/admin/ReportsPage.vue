<template>
  <div class="row g-4">
    <div class="col-12">
      <div class="portal-card p-4">
        <div class="d-flex flex-column flex-lg-row justify-content-between align-items-start align-items-lg-center gap-3 mb-4 pb-3 border-bottom">
          <div>
            <h3 class="section-heading mb-1">Monthly Activity Report</h3>
            <p class="text-muted mb-0">Generate the monthly placement activity CSV from live database records.</p>
          </div>
          <button class="btn btn-outline-secondary btn-sm rounded-pill px-3" @click="loadReport" :disabled="loading">
            <i class="bi bi-arrow-clockwise me-1"></i>Refresh
          </button>
        </div>

        <div v-if="toast.message" :class="`alert alert-${toast.tone} alert-dismissible fade show`" role="alert">
          {{ toast.message }}
          <button type="button" class="btn-close" @click="toast.message = ''"></button>
        </div>

        <SectionCard title="Generate Monthly Placement Activity Report" :subtitle="selectedPeriodLabel" class="mb-4">
          <div class="row g-3 align-items-end">
            <div class="col-md-5">
              <label class="form-label fw-semibold" for="report-month">Month</label>
              <select id="report-month" v-model.number="selectedMonth" class="form-select" :disabled="busy">
                <option v-for="month in months" :key="month.value" :value="month.value">{{ month.label }}</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label fw-semibold" for="report-year">Year</label>
              <input id="report-year" v-model.number="selectedYear" type="number" min="2000" max="2100" class="form-control" :disabled="busy">
            </div>
            <div class="col-md-4 d-grid">
              <button class="btn btn-primary" @click="generateReport" :disabled="busy">
                <span v-if="generating" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-filetype-csv me-2"></i>
                {{ generating ? 'Generating...' : 'Generate CSV Report' }}
              </button>
            </div>
          </div>
        </SectionCard>

        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary"></div>
          <p class="text-muted small mt-3 mb-0">Loading monthly activity...</p>
        </div>

        <template v-else>
          <div class="row g-3 mb-4">
            <div class="col-md-4">
              <div class="portal-card p-4 h-100">
                <div class="text-muted small mb-1">Selected Month</div>
                <div class="fs-4 fw-bold">{{ report.period }}</div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="portal-card p-4 h-100">
                <div class="text-muted small mb-1">Placement Drives Conducted</div>
                <div class="fs-2 fw-bold text-primary">{{ report.metrics.placement_drives_conducted }}</div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="portal-card p-4 h-100">
                <div class="text-muted small mb-1">Students Applied</div>
                <div class="fs-2 fw-bold text-success">{{ report.metrics.students_applied }}</div>
              </div>
            </div>
            <div class="col-md-4">
              <div class="portal-card p-4 h-100">
                <div class="text-muted small mb-1">Students Selected</div>
                <div class="fs-2 fw-bold text-warning">{{ report.metrics.students_selected }}</div>
              </div>
            </div>
          </div>

          <SectionCard title="CSV Export" subtitle="Downloads use the existing authenticated export endpoint.">
            <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3">
              <div>
                <div class="fw-semibold">{{ generatedFile || 'No CSV generated in this session' }}</div>
                <div class="text-muted small">{{ exportStatus }}</div>
              </div>
              <button class="btn btn-outline-primary" @click="downloadCsv" :disabled="!generatedFile || downloading">
                <span v-if="downloading" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-download me-2"></i>
                Download CSV
              </button>
            </div>
          </SectionCard>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import SectionCard from '@/components/common/SectionCard.vue'
import { adminAPI } from '@/api/admin'

const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]
const months = monthNames.map((label, index) => ({ label, value: index + 1 }))
const now = new Date()

const selectedMonth = ref(now.getMonth() + 1)
const selectedYear = ref(now.getFullYear())
const loading = ref(false)
const generating = ref(false)
const downloading = ref(false)
const generatedFile = ref('')
const exportStatus = ref('Generate a report to create a downloadable CSV.')
const toast = ref({ message: '', tone: 'info' })
const report = ref(emptyReport(selectedYear.value, selectedMonth.value))

const busy = computed(() => loading.value || generating.value)
const selectedPeriodLabel = computed(() => `${monthNames[selectedMonth.value - 1]} ${selectedYear.value}`)

watch([selectedMonth, selectedYear], () => {
  generatedFile.value = ''
  exportStatus.value = 'Generate a report to create a downloadable CSV.'
  loadReport()
})

function emptyReport(year, month) {
  return {
    month,
    month_name: monthNames[month - 1],
    year,
    period: `${monthNames[month - 1]} ${year}`,
    metrics: {
      placement_drives_conducted: 0,
      students_applied: 0,
      students_selected: 0
    }
  }
}

function showToast(message, tone = 'info') {
  toast.value = { message, tone }
  setTimeout(() => { toast.value.message = '' }, 4500)
}

async function loadReport() {
  loading.value = true
  try {
    const { data } = await adminAPI.getMonthlyActivityReport({
      year: selectedYear.value,
      month: selectedMonth.value
    })
    report.value = data.report || emptyReport(selectedYear.value, selectedMonth.value)
  } catch (err) {
    showToast(err?.response?.data?.error || 'Unable to load monthly report.', 'danger')
  } finally {
    loading.value = false
  }
}

async function generateReport() {
  generating.value = true
  generatedFile.value = ''
  exportStatus.value = 'Report generation is running.'
  try {
    const { data } = await adminAPI.generateReport({
      year: selectedYear.value,
      month: selectedMonth.value
    })

    if (data.state === 'SUCCESS') {
      applyTaskResult(data.result)
      showToast('Monthly activity report generated and emailed.', 'success')
      return
    }

    exportStatus.value = data.message || 'Report queued. Waiting for completion...'
    await pollReportStatus(data.task_id)
  } catch (err) {
    exportStatus.value = 'Report generation failed.'
    showToast(err?.response?.data?.error || 'Unable to generate report.', 'danger')
  } finally {
    generating.value = false
  }
}

async function pollReportStatus(taskId) {
  for (let attempt = 0; attempt < 20; attempt += 1) {
    await wait(1500)
    const { data } = await adminAPI.getReportStatus(taskId)

    if (data.state === 'SUCCESS') {
      applyTaskResult(data.result)
      showToast('Monthly activity report generated and emailed.', 'success')
      return
    }

    if (data.state === 'FAILURE') {
      throw new Error(data.error || 'Report task failed.')
    }

    exportStatus.value = data.message || 'Report generation is still running.'
  }

  exportStatus.value = 'Report is still processing. Refresh and try downloading after it completes.'
}

function applyTaskResult(result) {
  generatedFile.value = result?.filename || ''
  exportStatus.value = generatedFile.value
    ? `CSV ready for ${result.period}. Email notifications sent: ${result.emails_sent || 0}.`
    : 'Report completed, but no CSV filename was returned.'
  if (result?.period) {
    report.value = {
      month: result.month,
      month_name: result.month_name,
      year: result.year,
      period: result.period,
      metrics: {
        placement_drives_conducted: result.placement_drives_conducted,
        students_applied: result.students_applied,
        students_selected: result.students_selected
      }
    }
  }
}

async function downloadCsv() {
  downloading.value = true
  try {
    const { data } = await adminAPI.downloadExportFile(generatedFile.value)
    const blobUrl = URL.createObjectURL(new Blob([data], { type: 'text/csv;charset=utf-8;' }))
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = generatedFile.value
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(blobUrl)
  } catch (err) {
    showToast(err?.response?.data?.error || 'CSV download failed.', 'danger')
  } finally {
    downloading.value = false
  }
}

function wait(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

onMounted(loadReport)
</script>
