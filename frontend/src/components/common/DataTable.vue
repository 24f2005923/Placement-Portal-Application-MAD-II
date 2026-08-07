<template>
  <div class="table-responsive responsive-table">
    <table class="table align-middle mb-0">
      <thead class="table-light">
        <tr>
          <th v-for="header in headers" :key="header">{{ header }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, index) in rows" :key="index">
          <td v-for="key in columns" :key="key">
            <slot :name="key" :row="row">
              {{ row[key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({
  headers: { type: Array, default: () => [] },
  columns: { type: Array, default: () => [] },
  rows: { type: Array, default: () => [] }
})
</script>
