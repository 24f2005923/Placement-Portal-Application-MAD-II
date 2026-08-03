<template>
  <span class="badge rounded-pill" :class="[badgeClass, customClass]">
    {{ label || status }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
import {
  applicationBadge,
  adminApplicationBadge,
  driveBadge,
  studentPlacementBadge,
  companyApprovalBadge
} from '@/utils/statusMeta'

const props = defineProps({
  status: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'application', // application, admin_application, drive, student, company
    validator(value) {
      return ['application', 'admin_application', 'drive', 'student', 'company'].includes(value)
    }
  },
  row: {
    type: Object,
    default: () => ({})
  },
  customClass: {
    type: String,
    default: 'px-3 py-2'
  }
})

const badgeClass = computed(() => {
  if (props.variant === 'application') return applicationBadge(props.status)
  if (props.variant === 'admin_application') return adminApplicationBadge(props.status)
  if (props.variant === 'drive') return driveBadge(props.status)
  if (props.variant === 'student') return studentPlacementBadge(props.row)
  if (props.variant === 'company') return companyApprovalBadge(props.row)
  return 'badge-soft-secondary'
})
</script>
