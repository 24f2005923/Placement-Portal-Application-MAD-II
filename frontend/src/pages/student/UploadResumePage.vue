<template>
  <div class="portal-card p-4 p-md-5">
    <h3 class="section-heading mb-2">Upload Resume</h3>
    <p class="text-muted mb-4">Upload your latest resume in PDF format for placement applications.</p>
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>
    <div
      class="border border-dashed rounded-4 p-5 text-center mb-4"
      :class="{ 'border-primary': dragging }"
      @dragover.prevent="dragging = true"
      @dragleave="dragging = false"
      @drop.prevent="onDrop"
      @click="$refs.fileInput.click()"
      style="cursor: pointer;"
    >
      <i class="bi bi-cloud-arrow-up fs-1 text-primary"></i>
      <div class="fw-semibold mt-2">{{ selectedFile ? selectedFile.name : 'Drag and drop file here or click to browse' }}</div>
      <small class="text-muted">PDF, DOC, DOCX supported (max 5 MB)</small>
      <input ref="fileInput" type="file" accept=".pdf,.doc,.docx" class="d-none" @change="onFileChange" />
    </div>
    <div v-if="currentResume" class="mb-3 p-3 bg-light rounded-3 d-flex align-items-center justify-content-between">
      <div class="small">
        <i class="bi bi-file-earmark-pdf text-primary me-2 fs-5"></i>
        Current Profile Resume: <strong>{{ currentResume }}</strong>
      </div>
      <button class="btn btn-sm btn-outline-primary" @click="openResume(currentResume)">
        <i class="bi bi-eye me-1"></i>View Resume
      </button>
    </div>
    <button class="btn btn-primary" :disabled="!selectedFile || uploading" @click="handleUpload">
      <span v-if="uploading" class="spinner-border spinner-border-sm me-2"></span>
      {{ uploading ? 'Uploading...' : 'Upload Resume' }}
    </button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { studentAPI } from '@/api/student'
import { openResume } from '@/utils/resume'

const selectedFile = ref(null)
const uploading = ref(false)
const dragging = ref(false)
const error = ref('')
const success = ref('')
const currentResume = ref('')

function onFileChange(e) {
  selectedFile.value = e.target.files[0] || null
}

function onDrop(e) {
  dragging.value = false
  selectedFile.value = e.dataTransfer.files[0] || null
}

async function handleUpload() {
  if (!selectedFile.value) return
  uploading.value = true
  error.value = ''
  success.value = ''
  try {
    const { data } = await studentAPI.uploadResume(selectedFile.value)
    success.value = 'Resume uploaded successfully!'
    currentResume.value = data.resume_path
    selectedFile.value = null
  } catch (err) {
    error.value = err.response?.data?.error || 'Upload failed.'
  } finally {
    uploading.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await studentAPI.getProfile()
    currentResume.value = data.student.resume_path || ''
  } catch (err) { console.error(err) }
})
</script>
