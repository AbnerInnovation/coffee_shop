import { useToast as useVTToast } from 'vue-toastification';

export interface ToastOptions {
  duration?: number;
}

export function useToast() {
  const toast = useVTToast();

  const mapOptions = (duration?: number) => ({ timeout: duration });

  const showToast = (
    message: string,
    type: 'success' | 'error' | 'info' | 'warning' = 'info',
    duration: number = 3000
  ) => {
    switch (type) {
      case 'success':
        return toast.success(message, mapOptions(duration));
      case 'error':
        return toast.error(message, mapOptions(duration));
      case 'warning':
        return toast.warning(message, mapOptions(duration));
      case 'info':
      default:
        return toast.info(message, mapOptions(duration));
    }
  };

  const removeToast = (id?: string | number) => {
    if (id !== undefined) {
      toast.dismiss(id);
    } else {
      toast.clear();
    }
  };

  const showSuccess = (message: string, duration?: number) => showToast(message, 'success', duration);
  const showError = (message: string, duration?: number) => showToast(message, 'error', duration ?? 5000);
  const showWarning = (message: string, duration?: number) => showToast(message, 'warning', duration);
  const showInfo = (message: string, duration?: number) => showToast(message, 'info', duration);

  return {
    showToast,
    removeToast,
    showSuccess,
    showError,
    showWarning,
    showInfo,
  };
}

export type UseToastReturn = ReturnType<typeof useToast>;
