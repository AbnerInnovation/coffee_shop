import { computed } from 'vue';

/**
 * Exposes the current frontend application version.
 * Priority: VITE_APP_VERSION env var > package.json version (__APP_VERSION__) > '1.0.0'
 */
export function useAppVersion() {
  const appVersion = computed(() => {
    return import.meta.env.VITE_APP_VERSION || __APP_VERSION__ || '1.0.0';
  });

  return {
    appVersion
  };
}
