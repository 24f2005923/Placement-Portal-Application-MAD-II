<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from '@/components/common/AppSidebar.vue'
import AppHeader from '@/components/common/AppHeader.vue'
import { adminNav, companyNav, studentNav } from '@/data/navigation'

const route = useRoute()
const mobileSidebarOpen = ref(false)

const navItems = computed(() => {
  if (route.path.startsWith('/company')) return companyNav
  if (route.path.startsWith('/student')) return studentNav
  return adminNav
})

watch(
  () => route.fullPath,
  () => {
    mobileSidebarOpen.value = false
  }
)
</script>

<template>
  <div class="portal-shell d-flex">
    <AppSidebar :items="navItems" :open="mobileSidebarOpen" @close="mobileSidebarOpen = false" />
    <div v-if="mobileSidebarOpen" class="mobile-sidebar-backdrop d-lg-none" @click="mobileSidebarOpen = false"></div>
    <div class="portal-main d-flex flex-column">
      <AppHeader @toggle-sidebar="mobileSidebarOpen = !mobileSidebarOpen" />
      <div class="container-fluid py-4 py-lg-5">
        <router-view />
      </div>
    </div>
  </div>
</template>
