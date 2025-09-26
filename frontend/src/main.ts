import { createApp } from 'vue';
import { createPinia } from 'pinia';
import axios from 'axios';
import App from './App.vue';
import router from './router';
import './assets/main.css';
import { i18n } from '@/plugins/i18n';
import Toast, { PluginOptions as ToastOptions } from 'vue-toastification';
import 'vue-toastification/dist/index.css';

// Configure axios
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
axios.interceptors.request.use(
  (config) => {
    const token = sessionStorage.getItem('access_token') || localStorage.getItem('access_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
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
