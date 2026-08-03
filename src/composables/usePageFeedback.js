import { ref } from 'vue'

export function usePageFeedback(timeoutMs = 4000) {
  const successMsg = ref('')
  const errorMsg = ref('')

  function showSuccess(msg) {
    successMsg.value = msg
    errorMsg.value = ''
    if (timeoutMs > 0) {
      setTimeout(() => { successMsg.value = '' }, timeoutMs)
    }
  }

  function showError(msg) {
    errorMsg.value = msg
    successMsg.value = ''
  }

  function clearMessages() {
    successMsg.value = ''
    errorMsg.value = ''
  }

  return {
    successMsg,
    errorMsg,
    showSuccess,
    showError,
    clearMessages
  }
}
