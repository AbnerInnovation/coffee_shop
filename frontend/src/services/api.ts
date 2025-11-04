import axios, { AxiosError, type AxiosInstance, type InternalAxiosRequestConfig, type AxiosRequestConfig } from 'axios';
import API_CONFIG from '@/config/api';

declare module 'axios' {
  export interface AxiosRequestConfig {
    _retry?: boolean;
  }
}
import { authService } from './authService';

// Create axios instance with base URL and common headers
const api: AxiosInstance = axios.create({
  baseURL: API_CONFIG.getUrl(''),
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor to add auth token to requests
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = authService.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to flatten responses and handle token refresh
api.interceptors.response.use(
  (response) => response.data,  // Flatten the response
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    
    // If error is 401 and we haven't tried to refresh yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh the token
        const newTokens = await authService.refreshToken();
        
        if (newTokens) {
          // Store the new token (preserve existing persistence automatically)
          authService.storeAuthData(newTokens);
          
          // Update the Authorization header
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${newTokens.access_token}`;
          }
          
          // Retry the original request with the new token
          return api(originalRequest);
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        // If refresh fails, clear auth and redirect to login
        authService.logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    // If we've already tried to refresh or it's a 401 error
    if (error.response?.status === 401) {
      // Clear auth and redirect to login
      authService.logout();
      window.location.href = '/login';
    }
    
    // For 403 errors, check if it's a subscription issue
    if (error.response?.status === 403) {
      const errorMessage = (error.response?.data as any)?.detail || '';
      
      // Check if error is subscription-related
      const isSubscriptionError = 
        errorMessage.includes('suscripción') ||
        errorMessage.includes('subscription') ||
        errorMessage.includes('expirado') ||
        errorMessage.includes('expired') ||
        errorMessage.includes('suspendida') ||
        errorMessage.includes('suspended');
      
      if (isSubscriptionError) {
        // Dispatch custom event for subscription error
        window.dispatchEvent(new CustomEvent('subscription-error', {
          detail: { message: errorMessage }
        }));
      }
      
      // DON'T logout users for 403 errors
      // Permission errors are not authentication errors
      // User is authenticated, just lacks permission for this resource
    }
    
    return Promise.reject(error);
  }
);

export default api;
