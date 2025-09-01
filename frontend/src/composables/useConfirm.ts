// composables/useConfirm.ts
import { ref } from 'vue'

type ConfirmOptions = {
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  confirmClass?: string
}

const isOpen = ref(false)
const options = ref<ConfirmOptions | null>(null)
let resolver: ((value: boolean) => void) | null = null

export function useConfirm() {
  function confirm(
    title: string,
    message: string,
    confirmText = 'OK',
    cancelText = 'Cancel',
    confirmClass = 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500'
  ): Promise<boolean> {
    return new Promise(resolve => {
      options.value = { title, message, confirmText, cancelText, confirmClass }
      isOpen.value = true
      resolver = resolve
    })
  }

  function onConfirm() {
    if (resolver) resolver(true)
    close()
  }

  function onCancel() {
    if (resolver) resolver(false)
    close()
  }

  function close() {
    isOpen.value = false
    options.value = null
    resolver = null
  }

  return { isOpen, options, confirm, onConfirm, onCancel }
}
