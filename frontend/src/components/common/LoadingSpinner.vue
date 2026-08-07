<template>
  <div class="text-center py-5">
    <div :class="`spinner-border text-${color}`" role="status"></div>
    <div v-if="message" class="text-muted small mt-2">{{ message }}</div>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: ''
  },
  color: {
    type: String,
    default: 'primary'
  }
})
</script>
