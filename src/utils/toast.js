export function showToast(message, variant = 'info', duration = 3000) {
  const event = new CustomEvent('app-toast', {
    detail: { message, variant, duration }
  })
  window.dispatchEvent(event)
}
