<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const props = defineProps({
  items: { type: Array, default: () => [] },
  open: { type: Boolean, default: false }
})

const emit = defineEmits(['close'])
const route = useRoute()
const router = useRouter()

const activePath = computed(() => route.path)

const navigate = (item) => {
  if (item.label === 'Logout') {
    router.push(item.to)
    emit('close')
    return
  }
  router.push(item.to)
  emit('close')
}
</script>

<template>
  <aside class="portal-sidebar p-3 p-lg-4" :class="{ 'is-open': open }">
    <div class="d-flex align-items-center justify-content-between mb-4">
      <div class="d-flex align-items-center gap-3">
        <div class="avatar-circle bg-white text-primary">P</div>
        <div>
          <div class="fw-semibold">Placement Portal</div>
          <small class="text-white-50">Management System</small>
        </div>
      </div>
      <button class="btn btn-sm btn-outline-light d-lg-none" type="button" @click="emit('close')">
        <i class="bi bi-x-lg"></i>
      </button>
    </div>

    <nav class="nav flex-column gap-1">
      <button
        v-for="item in props.items"
        :key="item.to"
        type="button"
        class="nav-link text-start border-0 bg-transparent d-flex align-items-center gap-3"
        :class="{ active: activePath.startsWith(item.to) }"
        @click="navigate(item)"
      >
        <i :class="`bi ${item.icon} fs-5`"></i>
        <span>{{ item.label }}</span>
      </button>
    </nav>
  </aside>
</template>
