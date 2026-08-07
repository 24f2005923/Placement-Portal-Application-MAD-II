<template>
  <section class="portal-card p-4 h-100">
    <div class="d-flex align-items-start justify-content-between mb-3">
      <div>
        <h5 class="section-heading mb-1">{{ title }}</h5>
        <p class="text-muted mb-0">{{ subtitle }}</p>
      </div>
      <slot name="actions" />
    </div>
    <slot />
  </section>
</template>

<script setup>
defineProps({
  title: String,
  subtitle: String
})
</script>
