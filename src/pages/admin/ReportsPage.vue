<template>
  <div class="row g-4">
    <div class="col-12">
      <div class="portal-card p-4">

        <!-- Page header -->
        <div class="d-flex flex-column flex-md-row justify-content-between
                    align-items-start align-items-md-center mb-4 pb-3 border-bottom gap-3">
          <div>
            <h3 class="section-heading mb-1">Placement Reports &amp; Analytics</h3>
            <p class="text-muted mb-0">
              All metrics are computed live from the database — no sample or demo data.
            </p>
          </div>
          <div class="d-flex gap-2 flex-wrap">
            <button class="btn btn-outline-secondary btn-sm rounded-pill px-3"
                    @click="refreshAll" :disabled="loading" id="btn-refresh-reports">
              <i class="bi bi-arrow-clockwise me-1"></i>Refresh
            </button>
            <button class="btn btn-primary rounded-pill px-4"
                    @click="handleGenerateReport" :disabled="generating"
                    id="btn-generate-report">
              <span v-if="generating" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-file-earmark-bar-graph me-2"></i>
              {{ generating ? 'Queuing...' : 'Generate Monthly Report' }}
            </button>
          </div>
        </div>

        <!-- Toast notification -->
        <div v-if="toast.msg" :class="`alert alert-${toast.tone} alert-dismissible fade show mb-4`" role="alert">
          <i :class="`bi ${toast.icon} me-2`"></i>{{ toast.msg }}
          <button type="button" class="btn-close" @click="toast.msg = ''"></button>
        </div>

        <!-- Global loading -->
        <div v-if="loading" class="text-center py-5" id="reports-loading">
          <div class="spinner-border text-primary"></div>
          <p class="text-muted mt-3 small">Loading analytics from database…</p>
        </div>

        <!-- Error state -->
        <div v-else-if="loadError" class="text-center py-5" id="reports-error">
          <i class="bi bi-exclamation-triangle fs-2 text-danger d-block mb-2"></i>
          <p class="text-danger fw-semibold">Failed to load analytics data.</p>
          <p class="text-muted small">{{ loadError }}</p>
          <button class="btn btn-outline-primary btn-sm rounded-pill mt-2"
                  @click="refreshAll">Try again</button>
        </div>

        <template v-else>

          <!-- ─── KPI Cards ────────────────────────────────────────────── -->
          <div class="row g-3 mb-4">
            <div class="col-6 col-lg-3">
              <div class="portal-card hover-lift p-4 h-100 text-center">
                <div class="text-muted small mb-1">Total Students</div>
                <div class="fs-2 fw-bold">{{ a.students.total }}</div>
                <div class="small text-success">{{ a.students.placed }} placed</div>
              </div>
            </div>
            <div class="col-6 col-lg-3">
              <div class="portal-card hover-lift p-4 h-100 text-center">
                <div class="text-muted small mb-1">Placement Rate</div>
                <div class="fs-2 fw-bold text-primary">{{ a.students.placement_rate }}%</div>
                <div class="small text-muted">of all registered students</div>
              </div>
            </div>
            <div class="col-6 col-lg-3">
              <div class="portal-card hover-lift p-4 h-100 text-center">
                <div class="text-muted small mb-1">Placement Drives</div>
                <div class="fs-2 fw-bold">{{ a.drives.total }}</div>
                <div class="small text-muted">{{ a.drives.open }} open · {{ a.drives.closed }} closed</div>
              </div>
            </div>
            <div class="col-6 col-lg-3">
              <div class="portal-card hover-lift p-4 h-100 text-center">
                <div class="text-muted small mb-1">Total Applications</div>
                <div class="fs-2 fw-bold">{{ a.applications.total }}</div>
                <div class="small text-success">{{ a.applications.selected }} final selections</div>
              </div>
            </div>
          </div>

          <!-- ─── Application Funnel ───────────────────────────────────── -->
          <SectionCard title="Application Pipeline" subtitle="Funnel breakdown across all drives" class="mb-4">
            <div v-if="a.applications.total === 0" class="text-center text-muted py-4">
              <i class="bi bi-funnel fs-2 d-block mb-2 text-secondary"></i>
              No applications have been submitted yet.
            </div>
            <div v-else>
              <div class="row g-3 mb-3">
                <div class="col-6 col-md-3" v-for="stage in funnelStages" :key="stage.label">
                  <div :class="`border rounded-3 p-3 text-center border-${stage.tone}`">
                    <div :class="`fs-4 fw-bold text-${stage.tone}`">{{ stage.count }}</div>
                    <div class="small text-muted">{{ stage.label }}</div>
                    <div :class="`small fw-semibold text-${stage.tone}`">{{ stage.pct }}%</div>
                  </div>
                </div>
              </div>
              <!-- Funnel progress bars -->
              <div class="mt-3">
                <div v-for="stage in funnelStages" :key="stage.label + '-bar'" class="mb-2">
                  <div class="d-flex justify-content-between small text-muted mb-1">
                    <span>{{ stage.label }}</span>
                    <span>{{ stage.count }} / {{ a.applications.total }}</span>
                  </div>
                  <div class="progress" style="height:8px;">
                    <div :class="`progress-bar bg-${stage.tone}`"
                         :style="{ width: stage.pct + '%' }" role="progressbar"></div>
                  </div>
                </div>
              </div>
            </div>
          </SectionCard>

          <!-- ─── Department Breakdown ─────────────────────────────────── -->
          <SectionCard title="Department-wise Placement" subtitle="Placement rate per department" class="mb-4">
            <div v-if="a.department_breakdown.length === 0" class="text-center text-muted py-4">
              <i class="bi bi-diagram-3 fs-2 d-block mb-2 text-secondary"></i>
              No student department data available.
            </div>
            <div v-else class="table-responsive">
              <table class="table align-middle table-hover" id="table-dept-breakdown">
                <thead class="table-light">
                  <tr>
                    <th>Department</th>
                    <th class="text-center">Total Students</th>
                    <th class="text-center">Placed</th>
                    <th class="text-center">Placement Rate</th>
                    <th>Progress</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="dept in a.department_breakdown" :key="dept.department">
                    <td class="fw-semibold">{{ dept.department }}</td>
                    <td class="text-center">{{ dept.total }}</td>
                    <td class="text-center text-success fw-semibold">{{ dept.placed }}</td>
                    <td class="text-center">
                      <span :class="rateBadge(dept.rate)">{{ dept.rate }}%</span>
                    </td>
                    <td style="min-width:120px;">
                      <div class="progress" style="height:7px;">
                        <div class="progress-bar bg-success"
                             :style="{ width: dept.rate + '%' }" role="progressbar"></div>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </SectionCard>

          <!-- ─── Top Hiring Companies ─────────────────────────────────── -->
          <SectionCard title="Top Hiring Partners" subtitle="Approved companies ranked by student selections" class="mb-4">
            <div v-if="companiesLoading" class="text-center py-4">
              <div class="spinner-border spinner-border-sm text-primary"></div>
            </div>
            <div v-else-if="topCompanies.length === 0" class="text-center text-muted py-4">
              <i class="bi bi-buildings fs-2 d-block mb-2 text-secondary"></i>
              No approved company data available yet.
            </div>
            <div v-else class="table-responsive">
              <table class="table align-middle table-hover" id="table-top-companies">
                <thead class="table-light">
                  <tr>
                    <th>#</th>
                    <th>Company</th>
                    <th>Industry</th>
                    <th class="text-center">Drives</th>
                    <th class="text-center">Applications</th>
                    <th class="text-center">Selections</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(co, idx) in topCompanies" :key="co.company_name">
                    <td class="text-muted">{{ idx + 1 }}</td>
                    <td class="fw-semibold">{{ co.company_name }}</td>
                    <td class="text-muted small">{{ co.industry }}</td>
                    <td class="text-center">{{ co.drives }}</td>
                    <td class="text-center">{{ co.total_applications }}</td>
                    <td class="text-center">
                      <span class="badge bg-success">{{ co.selections }} placed</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </SectionCard>

          <!-- ─── Generated Reports Archive ───────────────────────────── -->
          <SectionCard title="Generated Monthly Reports" subtitle="HTML reports produced by the background report task">
            <div v-if="reportsArchive.length === 0" class="text-center text-muted py-4">
              <i class="bi bi-journal-text fs-2 d-block mb-2 text-secondary"></i>
              No monthly reports generated yet.
              Click <strong>Generate Monthly Report</strong> to produce one in the background.
            </div>
            <div v-else class="table-responsive">
              <table class="table align-middle table-hover" id="table-reports-archive">
                <thead class="table-light">
                  <tr>
                    <th>Period</th>
                    <th>File</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="rpt in reportsArchive" :key="rpt.month">
                    <td class="fw-semibold text-primary">{{ rpt.month }}</td>
                    <td><code>{{ rpt.html_filename }}</code></td>
                    <td>
                      <a :href="rpt.download_url" target="_blank"
                         class="btn btn-sm btn-outline-primary rounded-pill px-3">
                        <i class="bi bi-eye me-1"></i>View
                      </a>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </SectionCard>

          <!-- ─── Data Exports ─────────────────────────────────────────── -->
          <div class="mt-4">
            <SectionCard title="Data Exports" subtitle="Trigger background CSV exports — files are ready to download once the task completes">
              <div class="row g-3">
                <div class="col-md-6">
                  <div class="border rounded-4 p-4 bg-white h-100 d-flex flex-column justify-content-between">
                    <div>
                      <h5 class="fw-bold text-dark mb-2">
                        <i class="bi bi-people text-primary me-2"></i>Export Student Dataset
                      </h5>
                      <p class="small text-muted mb-3">
                        Generates a CSV of all student profiles including academic records,
                        contact details, and placement status.
                      </p>
                    </div>
                    <button class="btn btn-outline-primary btn-sm rounded-pill w-100"
                            @click="handleExportStudents" :disabled="exportingStudent"
                            id="btn-export-students">
                      <span v-if="exportingStudent" class="spinner-border spinner-border-sm me-1"></span>
                      {{ exportingStudent ? 'Queuing…' : 'Export Students CSV' }}
                    </button>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="border rounded-4 p-4 bg-white h-100 d-flex flex-column justify-content-between">
                    <div>
                      <h5 class="fw-bold text-dark mb-2">
                        <i class="bi bi-buildings text-success me-2"></i>Export Company Dataset
                      </h5>
                      <p class="small text-muted mb-3">
                        Generates a CSV of registered companies with approval status,
                        drive counts, and selection totals.
                      </p>
                    </div>
                    <button class="btn btn-outline-success btn-sm rounded-pill w-100"
                            @click="handleExportCompanies" :disabled="exportingCompany"
                            id="btn-export-companies">
                      <span v-if="exportingCompany" class="spinner-border spinner-border-sm me-1"></span>
                      {{ exportingCompany ? 'Queuing…' : 'Export Companies CSV' }}
                    </button>
                  </div>
                </div>
              </div>
            </SectionCard>
          </div>

        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import SectionCard from '@/components/common/SectionCard.vue'
import { adminAPI } from '@/api/admin'

// ── Reactive state ────────────────────────────────────────────────────────
const loading         = ref(true)
const loadError       = ref('')
const companiesLoading = ref(false)
const generating      = ref(false)
const exportingStudent = ref(false)
const exportingCompany = ref(false)

const a = ref({
  students:             { total: 0, placed: 0, placement_rate: 0 },
  drives:               { total: 0, open: 0, closed: 0 },
  applications:         { total: 0, shortlisted: 0, in_interview: 0, selected: 0, rejected: 0,
                          shortlist_rate: 0, selection_rate: 0, interview_rate: 0 },
  department_breakdown: [],
})
const topCompanies  = ref([])
const reportsArchive = ref([])
const toast = ref({ msg: '', tone: 'info', icon: 'bi-info-circle' })

// ── Application funnel stages from live data ──────────────────────────────
const funnelStages = computed(() => {
  const apps = a.value.applications
  const total = apps.total || 1   // avoid /0; progress bars stay at 0% anyway
  return [
    { label: 'Applied',      count: apps.total,        pct: 100,                                     tone: 'secondary' },
    { label: 'Shortlisted',  count: apps.shortlisted,  pct: round1((apps.shortlisted  / total) * 100), tone: 'primary'   },
    { label: 'In Interview', count: apps.in_interview, pct: round1((apps.in_interview / total) * 100), tone: 'warning'   },
    { label: 'Selected',     count: apps.selected,     pct: round1((apps.selected     / total) * 100), tone: 'success'   },
  ]
})

// ── Helpers ───────────────────────────────────────────────────────────────
function round1(val) { return Math.round(val * 10) / 10 }

function rateBadge(rate) {
  if (rate >= 75) return 'badge bg-success'
  if (rate >= 40) return 'badge bg-warning text-dark'
  return 'badge bg-secondary'
}

function showToast(msg, tone = 'info', icon = 'bi-info-circle') {
  toast.value = { msg, tone, icon }
  setTimeout(() => { toast.value.msg = '' }, 5000)
}

// ── Data loaders ──────────────────────────────────────────────────────────
async function loadAnalytics() {
  const res = await adminAPI.getPlacementAnalytics()
  a.value = res.data.analytics
}

async function loadTopCompanies() {
  companiesLoading.value = true
  try {
    const res = await adminAPI.getTopCompanies(10)
    topCompanies.value = res.data.companies || []
  } finally {
    companiesLoading.value = false
  }
}

async function loadReportsArchive() {
  const res = await adminAPI.listReports()
  reportsArchive.value = res.data.reports || []
}

async function refreshAll() {
  loading.value = true
  loadError.value = ''
  try {
    await Promise.all([loadAnalytics(), loadTopCompanies(), loadReportsArchive()])
  } catch (err) {
    loadError.value = err?.response?.data?.error || err.message || 'Unexpected error'
  } finally {
    loading.value = false
  }
}

// ── Action handlers ───────────────────────────────────────────────────────
async function handleGenerateReport() {
  generating.value = true
  try {
    const { data } = await adminAPI.generateReport()
    showToast(data.message || 'Report generation queued.', 'info', 'bi-info-circle')
    setTimeout(loadReportsArchive, 2500)
  } catch {
    showToast('Failed to queue report generation. Is Celery running?', 'danger', 'bi-exclamation-triangle')
  } finally {
    generating.value = false
  }
}

async function handleExportStudents() {
  exportingStudent.value = true
  try {
    const { data } = await adminAPI.triggerStudentExport()
    showToast(data.message || 'Student CSV export queued.', 'success', 'bi-check-circle')
  } catch {
    showToast('Student export failed to queue.', 'danger', 'bi-exclamation-triangle')
  } finally {
    exportingStudent.value = false
  }
}

async function handleExportCompanies() {
  exportingCompany.value = true
  try {
    const { data } = await adminAPI.triggerCompanyExport()
    showToast(data.message || 'Company CSV export queued.', 'success', 'bi-check-circle')
  } catch {
    showToast('Company export failed to queue.', 'danger', 'bi-exclamation-triangle')
  } finally {
    exportingCompany.value = false
  }
}

onMounted(refreshAll)
</script>
