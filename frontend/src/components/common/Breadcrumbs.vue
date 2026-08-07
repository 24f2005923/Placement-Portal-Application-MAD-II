<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const crumbs = computed(() => {
  const path = route.path
  if (path.startsWith('/admin/students/')) return ['Admin', 'Students', 'Profile']
  if (path.startsWith('/admin/companies/')) return ['Admin', 'Companies', 'Details']
  if (path.startsWith('/admin/drives/')) return ['Admin', 'Placement Drives', 'Details']
  if (path.startsWith('/company/drives/') && path.endsWith('/edit')) return ['Company', 'Placement Drives', 'Edit']
  if (path.startsWith('/student/drives/') && path.endsWith('/apply')) return ['Student', 'Placement Drives', 'Apply']
  return path.split('/').filter(Boolean).map((part) => part.replace(/-/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase()))
})
</script>

<template>
  <nav aria-label="breadcrumb">
    <ol class="breadcrumb mb-0 small">
      <li class="breadcrumb-item">
        <router-link to="/">Home</router-link>
      </li>
      <li v-for="crumb in crumbs" :key="crumb" class="breadcrumb-item">
        <span>{{ crumb }}</span>
      </li>
    </ol>
  </nav>
</template>
