import { ref } from 'vue'

export function useAsyncCsvExport(options = {}) {
  const busy = ref(false)
  const statusText = ref(options.idleText || 'Exporting...')

  async function run({ start, status, download, success, queuedText = 'Processing...', maxPolls = 20 }) {
    busy.value = true
    statusText.value = 'Queuing...'

    try {
      const { data } = await start()
      if (data.state === 'SUCCESS') {
        await downloadResult(download, data.result)
        if (success) success(data.result)
        return data.result
      }

      statusText.value = queuedText
      const result = await waitForResult(status, data.task_id, maxPolls)
      await downloadResult(download, result)
      if (success) success(result)
      return result
    } finally {
      busy.value = false
      statusText.value = options.idleText || 'Exporting...'
    }
  }

  return { busy, statusText, run }
}

async function waitForResult(statusRequest, taskId, maxPolls) {
  for (let attempt = 0; attempt < maxPolls; attempt += 1) {
    await wait(1500)
    const { data } = await statusRequest(taskId)

    if (data.state === 'SUCCESS') return data.result
    if (data.state === 'FAILURE') throw new Error(data.error || 'Export task failed.')
  }

  throw new Error('Export is still processing. Try again shortly to download the completed CSV.')
}

async function downloadResult(downloadRequest, result) {
  const filename = result?.filename
  if (!filename) throw new Error('Export completed without a filename.')

  const { data } = await downloadRequest(filename)
  const blobUrl = URL.createObjectURL(new Blob([data], { type: 'text/csv;charset=utf-8;' }))
  const link = document.createElement('a')
  link.href = blobUrl
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(blobUrl)
}

function wait(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}
