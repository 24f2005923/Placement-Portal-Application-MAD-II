<template>
  <div class="portal-card p-4 h-100 placeholder-chart">
    <div class="d-flex align-items-start justify-content-between">
      <div>
        <h5 class="mb-1">{{ title }}</h5>
        <p class="text-muted mb-0">{{ subtitle }}</p>
      </div>
      <span class="badge badge-soft-primary rounded-pill">Demo Chart</span>
    </div>
    <div class="chart-bars">
      <span v-for="bar in bars" :key="bar" :style="{ height: bar }"></span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: 'Chart' },
  subtitle: { type: String, default: 'Static analytics placeholder' },
  bars: {
    type: Array,
    default: () => ['96px', '142px', '118px', '164px', '128px', '198px', '138px', '112px', '175px', '124px', '186px', '152px']
  }
})
</script>
