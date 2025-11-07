import { createI18n } from 'vue-i18n';
import en from '@/locales/en.json';
import es from '@/locales/es.json';
import { safeStorage } from '@/utils/storage';

export type AppLocale = 'en' | 'es';

const STORAGE_KEY = 'app_locale';

function getInitialLocale(): AppLocale {
  const stored = safeStorage.getItem(STORAGE_KEY) as AppLocale | null;
  if (stored === 'en' || stored === 'es') return stored;
  // Default to Spanish
  return 'es';
}

export const i18n = createI18n({
  legacy: false,
  globalInjection: true,
  locale: getInitialLocale(),
  fallbackLocale: 'en',
  messages: {
    en,
    es,
  },
});

export function setLocale(locale: AppLocale) {
  i18n.global.locale.value = locale;
  safeStorage.setItem(STORAGE_KEY, locale);
  if (typeof document !== 'undefined') {
    document.documentElement.setAttribute('lang', locale);
  }
}

// Set html lang on load
if (typeof document !== 'undefined') {
  document.documentElement.setAttribute('lang', (i18n.global.locale.value as string) || 'es');
}
