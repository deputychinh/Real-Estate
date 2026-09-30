export type ToastTone = 'success' | 'danger' | 'info'

export interface Toast {
  id: number
  tone: ToastTone
  message: string
}

const TOAST_MS = 4000

/** Small toast queue shared through useState (rendered by AppToasts). */
export function useNotify() {
  const toasts = useState<Toast[]>('toasts', () => [])
  let nextId = 0

  function push(tone: ToastTone, message: string): void {
    const id = Date.now() + nextId++
    toasts.value = [...toasts.value, { id, tone, message }]
    if (import.meta.client) setTimeout(() => dismiss(id), TOAST_MS)
  }

  function dismiss(id: number): void {
    toasts.value = toasts.value.filter((toast) => toast.id !== id)
  }

  return {
    toasts,
    dismiss,
    success: (message: string) => push('success', message),
    error: (message: string) => push('danger', message),
    info: (message: string) => push('info', message),
  }
}
