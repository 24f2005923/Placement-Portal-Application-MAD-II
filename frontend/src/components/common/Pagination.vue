<template>
  <nav>
    <ul class="pagination mb-0">
      <li class="page-item" :class="{ disabled: page === 1 }">
        <button class="page-link" @click="$emit('change', page - 1)">Prev</button>
      </li>
      <li class="page-item active">
        <span class="page-link">{{ page }}</span>
      </li>
      <li class="page-item" :class="{ disabled: page === total }">
        <button class="page-link" @click="$emit('change', page + 1)">Next</button>
      </li>
    </ul>
  </nav>
</template>

<script setup>
defineProps({
  page: { type: Number, default: 1 },
  total: { type: Number, default: 1 }
})

defineEmits(['change'])
</script>
