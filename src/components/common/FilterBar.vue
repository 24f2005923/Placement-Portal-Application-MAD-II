<template>
  <div class="row g-3 mb-4 align-items-center">
    <div class="col-12 col-lg-6">
      <input
        :value="searchQuery"
        @input="$emit('update:searchQuery', $event.target.value)"
        type="search"
        class="form-control form-control-lg"
        :placeholder="searchPlaceholder"
        @keyup.enter="$emit('filter')"
      />
    </div>
    <div class="col-12 col-lg-3" v-if="statusOptions && statusOptions.length > 0">
      <select
        :value="statusFilter"
        @change="$emit('update:statusFilter', $event.target.value)"
        class="form-select form-select-lg"
      >
        <option v-for="opt in statusOptions" :key="opt" :value="opt">
          {{ opt }}
        </option>
      </select>
    </div>
    <div class="col-12 col-lg-3 d-grid">
      <button class="btn btn-primary btn-lg" @click="$emit('filter')" :disabled="loading">
        <i class="bi bi-funnel me-2"></i>Apply Filters
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  searchQuery: { type: String, default: '' },
  searchPlaceholder: { type: String, default: 'Search...' },
  statusFilter: { type: String, default: 'All' },
  statusOptions: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false }
})

defineEmits(['update:searchQuery', 'update:statusFilter', 'filter'])
</script>
