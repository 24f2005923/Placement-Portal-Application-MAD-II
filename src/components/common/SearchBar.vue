<template>
  <div class="input-group rounded-pill overflow-hidden shadow-sm">
    <span class="input-group-text bg-white border-0 text-muted">
      <i class="bi bi-search"></i>
    </span>
    <input class="form-control border-0" type="search" :placeholder="placeholder" />
  </div>
</template>

<script setup>
defineProps({
  placeholder: { type: String, default: 'Search...' }
})
</script>
