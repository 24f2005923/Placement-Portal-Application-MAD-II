<template>
  <div v-if="success || error" class="feedback-alert mb-3">
    <div v-if="success" class="alert alert-success alert-dismissible fade show" role="alert">
      <i class="bi bi-check-circle me-2"></i>{{ success }}
      <button type="button" class="btn-close" @click="$emit('clear-success')"></button>
    </div>
    <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
      <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
      <button type="button" class="btn-close" @click="$emit('clear-error')"></button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  success: {
    type: String,
    default: ''
  },
  error: {
    type: String,
    default: ''
  }
})

defineEmits(['clear-success', 'clear-error'])
</script>
