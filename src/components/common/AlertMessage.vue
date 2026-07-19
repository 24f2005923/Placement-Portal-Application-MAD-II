<template>
  <div class="alert d-flex align-items-center gap-2" :class="`alert-${variant}`" role="alert">
    <i :class="`bi bi-${icon}`"></i>
    <div>{{ message }}</div>
  </div>
</template>

<script setup>
defineProps({
  variant: { type: String, default: 'success' },
  icon: { type: String, default: 'check-circle' },
  message: { type: String, default: 'Action completed successfully.' }
})
</script>
