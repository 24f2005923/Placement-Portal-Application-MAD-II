<template>
  <div class="modal fade" tabindex="-1" :id="id">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content rounded-4 border-0">
        <div class="modal-header">
          <h5 class="modal-title">{{ title }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <p class="mb-0">{{ message }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-light" data-bs-dismiss="modal">Cancel</button>
          <button class="btn btn-danger" data-bs-dismiss="modal" @click="$emit('confirm')">
            Confirm
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  id: { type: String, required: true },
  title: { type: String, default: 'Confirm action' },
  message: { type: String, default: 'Are you sure?' }
})

defineEmits(['confirm'])
</script>
