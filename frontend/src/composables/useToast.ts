import { ref } from 'vue';

export interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
  duration?: number;
}

export function useToast() {
  const toasts = ref<Toast[]>([]);
  let toastId = 0;

  const showToast = (
    message: string, 
    type: Toast['type'] = 'info', 
    duration: number = 3000
  ) => {
    const id = toastId++;
    const toast: Toast = { id, message, type, duration };
    
    toasts.value.push(toast);
    
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, duration);
    }
    
    return id;
  };

  const removeToast = (id: number) => {
    const index = toasts.value.findIndex(toast => toast.id === id);
    if (index !== -1) {
      toasts.value.splice(index, 1);
    }
  };

  const showSuccess = (message: string, duration?: number) => {
    return showToast(message, 'success', duration);
  };

  const showError = (message: string, duration?: number) => {
    return showToast(message, 'error', duration || 5000);
  };

  const showWarning = (message: string, duration?: number) => {
    return showToast(message, 'warning', duration);
  };

  const showInfo = (message: string, duration?: number) => {
    return showToast(message, 'info', duration);
  };

  return {
    toasts,
    showToast,
    removeToast,
    showSuccess,
    showError,
    showWarning,
    showInfo
  };
}

export type UseToastReturn = ReturnType<typeof useToast>;

export const ToastContainer = {
  setup() {
    const { toasts, removeToast } = useToast();
    
    const toastClass = (type: string) => ({
      'bg-green-50 text-green-800': type === 'success',
      'bg-red-50 text-red-800': type === 'error',
      'bg-yellow-50 text-yellow-800': type === 'warning',
      'bg-blue-50 text-blue-800': type === 'info',
    });
    
    const iconClass = (type: string) => ({
      'text-green-400': type === 'success',
      'text-red-400': type === 'error',
      'text-yellow-400': type === 'warning',
      'text-blue-400': type === 'info',
    });
    
    return { toasts, removeToast, toastClass, iconClass };
  },
  template: `
    <div class="fixed top-4 right-4 z-50 space-y-4 w-80">
      <transition-group
        enter-active-class="transform ease-out duration-300 transition"
        enter-from="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
        enter-to="translate-y-0 opacity-100 sm:translate-x-0"
        leave-active-class="transition ease-in duration-100"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="rounded-md p-4 shadow-lg"
          :class="toastClass(toast.type)"
        >
          <div class="flex">
            <div class="flex-shrink-0">
              <svg
                class="h-5 w-5"
                :class="iconClass(toast.type)"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  v-if="toast.type === 'success'"
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clip-rule="evenodd"
                />
                <path
                  v-else-if="toast.type === 'error'"
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clip-rule="evenodd"
                />
                <path
                  v-else-if="toast.type === 'warning'"
                  fill-rule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clip-rule="evenodd"
                />
                <path
                  v-else
                  fill-rule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h2a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                  clip-rule="evenodd"
                />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm font-medium">
                {{ toast.message }}
              </p>
            </div>
            <div class="ml-auto pl-3">
              <div class="-mx-1.5 -my-1.5">
                <button
                  type="button"
                  class="inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2"
                  :class="{
                    'bg-green-50 text-green-500 hover:bg-green-100 focus:ring-offset-green-50 focus:ring-green-600': toast.type === 'success',
                    'bg-red-50 text-red-500 hover:bg-red-100 focus:ring-offset-red-50 focus:ring-red-600': toast.type === 'error',
                    'bg-yellow-50 text-yellow-500 hover:bg-yellow-100 focus:ring-offset-yellow-50 focus:ring-yellow-600': toast.type === 'warning',
                    'bg-blue-50 text-blue-500 hover:bg-blue-100 focus:ring-offset-blue-50 focus:ring-blue-600': toast.type === 'info',
                  }"
                  @click="removeToast(toast.id)"
                >
                  <span class="sr-only">Dismiss</span>
                  <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </transition-group>
    </div>
  `,
};
