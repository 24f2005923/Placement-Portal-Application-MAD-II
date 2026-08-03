import { ref } from 'vue'

export function useDataLoader(loaderFn) {
  const data = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function load(...args) {
    loading.value = true
    error.value = null
    try {
      const response = await loaderFn(...args)
      data.value = response?.data || response
      return data.value
    } catch (err) {
      console.error(err)
      error.value = err?.response?.data?.error || err.message || 'An error occurred while loading data.'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    data,
    loading,
    error,
    load
  }
}
