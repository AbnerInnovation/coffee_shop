import { createApp } from 'vue';
import { createPinia } from 'pinia';
import axios from 'axios';
import App from './App.vue';
import router from './router';
import './assets/main.css';
import { i18n } from '@/plugins/i18n';
import Toast, { PluginOptions as ToastOptions, POSITION } from 'vue-toastification';
import 'vue-toastification/dist/index.css';
import { safeStorage } from './utils/storage';
import { setGlobalToken, getGlobalToken } from './utils/tokenCache';
import { registerSW } from 'virtual:pwa-register';
import { initializeElectronConfig } from './utils/subdomain';

// Configure axios
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8001';
axios.defaults.withCredentials = true; // Send cookies with requests

// Request interceptor - add auth token
axios.interceptors.request.use(
  (config) => {
    // Try in-memory token first (for Safari), then storage
    let token = getGlobalToken() || safeStorage.getItem('access_token') || safeStorage.getItem('access_token', true);
    
    // If token found in storage but not in memory, restore it to memory
    if (!getGlobalToken() && token) {
      setGlobalToken(token);
    }
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - handle 401 errors
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const isAuthEndpoint = originalRequest.url?.includes('/auth/token') ||
                           originalRequest.url?.includes('/auth/register');
    
    // Only clear tokens if we get a 401 response from the server
    // Don't clear on network errors, auth endpoints, or other issues
    if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      originalRequest._retry = true;
      
      // Clear invalid token and redirect to login
      setGlobalToken(null);
      safeStorage.removeItem('access_token');
      safeStorage.removeItem('refresh_token');
      safeStorage.removeItem('user');
      safeStorage.removeItem('access_token', true);
      safeStorage.removeItem('refresh_token', true);
      safeStorage.removeItem('user', true);
      
      // Redirect to login only if not already there
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Initialize Electron configuration before creating the app
async function initializeApp() {
  await initializeElectronConfig();
  
  // Set axios default header for Electron subdomain
  const subdomain = (await import('./utils/subdomain')).getSubdomain();
  if (subdomain) {
    const api = (await import('./services/api')).default;
    api.defaults.headers.common['x-restaurant-subdomain'] = subdomain;
    console.log('[main.ts] Set default x-restaurant-subdomain header:', subdomain);
  }
  
  const pinia = createPinia();
  const app = createApp(App);

  app.use(pinia);
  app.use(i18n);
  
  // Initialize auth store before router
  const { useAuthStore } = await import('./stores/auth');
  const authStore = useAuthStore();
  await authStore.checkAuth();
  
  app.use(router);
  
  // Configure Vue Toastification with sensible defaults
  const toastOptions: ToastOptions = {
    position: POSITION.BOTTOM_RIGHT,
    timeout: 3500,
    closeOnClick: true,
    pauseOnFocusLoss: true,
    pauseOnHover: true,
    draggable: true,
    draggablePercent: 0.6,
    showCloseButtonOnHover: false,
    hideProgressBar: false,
    closeButton: 'button',
    icon: true,
    rtl: false,
  };
  app.use(Toast, toastOptions);
  
  // Wait for router to be ready before mounting
  await router.isReady();
  
  console.log('[main.ts] Router ready, mounting app...');
  app.mount('#app');
}

initializeApp();

// Register PWA Service Worker and notify the app when a new version is available
if ('serviceWorker' in navigator) {
  const updateSW = registerSW({
    onNeedRefresh() {
      // Notify Vue app so it can show a toast and decide when to reload
      window.dispatchEvent(
        new CustomEvent('pwa-update-available', {
          detail: {
            updateSW,
          },
        })
      );
    },
  });
}
