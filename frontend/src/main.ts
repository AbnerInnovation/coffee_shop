import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';

// Initialize Pinia
const pinia = createPinia();
import axios from 'axios';
import App from './App.vue';
import './assets/main.css';
import { useAuthStore } from './stores/auth';

// Define routes
const publicRoutes: RouteRecordRaw[] = [
  { path: '/login', name: 'Login', component: () => import('./views/LoginView.vue'), meta: { requiresAuth: false } },
  { path: '/register', name: 'Register', component: () => import('./views/RegisterView.vue'), meta: { requiresAuth: false } },
];

const protectedRoutes: RouteRecordRaw[] = [
  { path: '/', name: 'Dashboard', component: () => import('./views/DashboardView.vue'), meta: { requiresAuth: true } },
  { path: '/tables', name: 'Tables', component: () => import('./views/TablesView.vue'), meta: { requiresAuth: true } },
  { path: '/menu', name: 'Menu', component: () => import('./views/MenuView.vue'), meta: { requiresAuth: true } },
  { path: '/orders', name: 'Orders', component: () => import('./views/OrdersView.vue'), meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('./views/NotFoundView.vue') },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    ...publicRoutes,
    ...protectedRoutes,
    { path: '/:pathMatch(.*)*', name: 'NotFound', component: () => import('./views/NotFoundView.vue') },
  ],
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 }
  }
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } });
  } else if ((to.name === 'Login' || to.name === 'Register') && authStore.isAuthenticated) {
    next({ name: 'Dashboard' });
  } else {
    next();
  }
});

router.onError((error) => {
  console.error('Router error:', error);
});

// Configure axios
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
}, (error) => Promise.reject(error));

const app = createApp(App);

app.use(pinia);
app.use(router);
app.mount('#app');

export { app, router, pinia };
