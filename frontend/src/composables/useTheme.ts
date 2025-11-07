import { ref, onMounted } from 'vue';
import { safeStorage } from '@/utils/storage';

const STORAGE_KEY = 'app_theme'; // 'light' | 'dark'

export function useTheme() {
  const isDark = ref(false);

  function applyTheme(dark: boolean) {
    const root = document.documentElement;
    if (dark) {
      root.classList.add('dark');
      safeStorage.setItem(STORAGE_KEY, 'dark');
    } else {
      root.classList.remove('dark');
      safeStorage.setItem(STORAGE_KEY, 'light');
    }
    isDark.value = dark;
  }

  function setTheme(theme: 'light' | 'dark') {
    applyTheme(theme === 'dark');
  }

  function toggleTheme() {
    applyTheme(!isDark.value);
  }

  function initTheme() {
    const stored = safeStorage.getItem(STORAGE_KEY);
    if (stored === 'light' || stored === 'dark') {
      applyTheme(stored === 'dark');
      return;
    }
    // Fallback to system preference
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    applyTheme(prefersDark);
  }

  onMounted(() => {
    // Ensure re-sync after mount in case initial inline script wasn't present
    initTheme();
  });

  return {
    isDark,
    setTheme,
    toggleTheme,
    initTheme,
  };
}
