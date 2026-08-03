<template>
  <div class="toast-container position-fixed bottom-0 end-0 p-3" style="z-index: 1055;">
    <div
      v-for="toast in toasts"
      :key="toast.id"
      class="toast show align-items-center text-white border-0"
      :class="[`bg-${toast.variant}`]"
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      <div class="d-flex">
        <div class="toast-body">
          {{ toast.message }}
        </div>
        <button
          type="button"
          class="btn-close btn-close-white me-2 m-auto"
          @click="removeToast(toast.id)"
          aria-label="Close"
        ></button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const toasts = ref([])
let nextId = 1

const handleToastEvent = (e) => {
  const id = nextId++
  const { message, variant, duration } = e.detail
  
  toasts.value.push({ id, message, variant })
  
  if (duration > 0) {
    setTimeout(() => {
      removeToast(id)
    }, duration)
  }
}

const removeToast = (id) => {
  toasts.value = toasts.value.filter(t => t.id !== id)
}

onMounted(() => {
  window.addEventListener('app-toast', handleToastEvent)
})

onUnmounted(() => {
  window.removeEventListener('app-toast', handleToastEvent)
})
</script>
