import { createApp } from 'vue';
import { createPinia } from 'pinia';
import axios from 'axios';
import App from './App.vue';
import router from './router';
import './assets/main.css';
import { i18n } from '@/plugins/i18n';
import Toast, { PluginOptions as ToastOptions } from 'vue-toastification';
import 'vue-toastification/dist/index.css';
import { safeStorage } from './utils/storage';

// Configure axios
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

// Request interceptor - add auth token
axios.interceptors.request.use(
  (config) => {
    const token = safeStorage.getItem('access_token') || safeStorage.getItem('access_token', true);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('🔑 Token attached to request:', config.url);
    } else {
      console.warn('⚠️ No token found for request:', config.url);
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
    
    // Don't handle 401 errors during login/register
    const isAuthEndpoint = originalRequest.url?.includes('/auth/token') || 
                          originalRequest.url?.includes('/auth/register');
    
    // Log 401 errors for debugging
    if (error.response?.status === 401) {
      console.error('❌ 401 Error:', {
        url: originalRequest.url,
        isAuthEndpoint,
        hasToken: !!originalRequest.headers?.Authorization,
        errorData: error.response?.data
      });
    }
    
    // Only clear tokens if we get a 401 response from the server
    // Don't clear on network errors, auth endpoints, or other issues
    if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      originalRequest._retry = true;
      
      console.log('🔒 401 Unauthorized - Clearing session');
      
      // Clear invalid token and redirect to login
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

const pinia = createPinia();
const app = createApp(App);

app.use(pinia);
app.use(router);
app.use(i18n);
// Configure Vue Toastification with sensible defaults
const toastOptions: ToastOptions = {
  position: 'top-right',
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
app.mount('#app');

export { app, router, pinia };
