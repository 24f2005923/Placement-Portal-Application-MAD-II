<template>
  <div class="text-center py-5 border rounded-4 bg-light">
    <i :class="`bi ${icon} fs-1 d-block mb-2 text-secondary`"></i>
    <h5 class="fw-semibold text-muted">{{ title }}</h5>
    <p v-if="message" class="text-muted small mb-3">{{ message }}</p>
    <router-link v-if="actionTo && actionLabel" :to="actionTo" class="btn btn-sm btn-outline-primary rounded-pill px-3">
      {{ actionLabel }}
    </router-link>
  </div>
</template>

<script setup>
defineProps({
  icon: {
    type: String,
    default: 'bi-inbox'
  },
  title: {
    type: String,
    required: true
  },
  message: {
    type: String,
    default: ''
  },
  actionLabel: {
    type: String,
    default: ''
  },
  actionTo: {
    type: String,
    default: ''
  }
})
</script>
