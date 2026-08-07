<template>
  <div class="portal-card hover-lift p-4 h-100">
    <div class="d-flex align-items-center justify-content-between gap-3">
      <div>
        <div class="text-muted small mb-1">{{ label }}</div>
        <div class="fs-2 fw-bold">{{ value }}</div>
        <div class="small text-muted">{{ delta }}</div>
      </div>
      <div class="stat-icon">
        <i :class="`bi ${icon}`"></i>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  value: String,
  delta: String,
  icon: String,
  tone: { type: String, default: 'primary' }
})
</script>
