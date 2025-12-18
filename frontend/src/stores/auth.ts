import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/services/api';
import { safeStorage, checkStorageAndWarn } from '@/utils/storage';
import { setGlobalToken } from '@/utils/tokenCache';
import type { Restaurant } from '@/composables/useRestaurant';

// Types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData extends LoginCredentials {
  full_name: string;
  role?: string;
}

export interface User {
  id: string | number;
  email: string;
  full_name: string;
  role: string;
  staff_type?: string | null;
  is_active: boolean;
}

interface AuthState {
  user: User | null;
  loading: boolean;
  error: string | null;
}

export const useAuthStore = defineStore('auth', () => {
  const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8001') + '/api/v1';
  
  // State
  const user = ref<User | null>(null);
  const restaurant = ref<Restaurant | null>(null);
  const loading = ref<boolean>(false);
  const error = ref<string | null>(null);
  const accessToken = ref<string | null>(null); // In-memory token for Safari
  const isAuthenticated = computed<boolean>(() => !!user.value);
  const isAdmin = computed<boolean>(() => user.value?.role === 'admin');
  
  // Actions
  async function login(credentials: LoginCredentials, remember: boolean = true) {
    try {
      loading.value = true;
      error.value = null;
      
      // Use OAuth2 password flow
      const formData = new URLSearchParams();
      formData.append('username', credentials.email);
      formData.append('password', credentials.password);
      formData.append('grant_type', 'password');
      formData.append('scope', '');

      const response = await api.post('/auth/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }) as any;

      const { access_token, refresh_token } = response;
      
      if (!access_token) {
        throw new Error('No access token received');
      }
      
      // Store tokens in memory FIRST (for Safari)
      accessToken.value = access_token;
      setGlobalToken(access_token); // Set global cache
      
      // Then store in storage
      safeStorage.setItem('access_token', access_token);
      if (refresh_token) {
        safeStorage.setItem('refresh_token', refresh_token);
      }
      
      try {
        // Fetch user data
        const userResponse = await api.get('/users/me', {
          headers: { Authorization: `Bearer ${access_token}` },
        });
        
        if (userResponse) {
          // Update store state FIRST (interceptor already flattened response)
          const userData = userResponse as unknown as User;
          user.value = userData;
          
          // Save to BOTH localStorage and sessionStorage for Safari compatibility
          safeStorage.setItem('user', JSON.stringify(userData));
          safeStorage.setItem('user', JSON.stringify(userData), true); // sessionStorage
          
          // Re-save tokens to ensure they persist
          safeStorage.setItem('access_token', access_token);
          safeStorage.setItem('access_token', access_token, true); // sessionStorage
          
          if (refresh_token) {
            safeStorage.setItem('refresh_token', refresh_token);
            safeStorage.setItem('refresh_token', refresh_token, true); // sessionStorage
          }
          
          // Wait to ensure Safari persists the data
          await new Promise(resolve => setTimeout(resolve, 300));
          
          // Load restaurant data for printing configurations
          try {
            await loadRestaurant();

          } catch (restaurantError) {
            console.warn('⚠️ Failed to load restaurant data on login:', restaurantError);
            // Don't fail login if restaurant load fails
          }
          
          // Note: Redirect is now handled by LoginView.vue component
          return true;
        }
      } catch (userError) {
        console.error('❌ Failed to fetch user data:', userError);
        error.value = 'Failed to load user data';
        // Clear tokens if user fetch fails
        safeStorage.removeItem('access_token');
        safeStorage.removeItem('refresh_token');
        safeStorage.removeItem('user');
        safeStorage.removeItem('access_token', true);
        safeStorage.removeItem('refresh_token', true);
        safeStorage.removeItem('user', true);
        return false;
      }
    } catch (err: any) {
      // Extract error message from new centralized error format
      error.value = err.response?.data?.error?.message || err.response?.data?.detail || 'Login failed';
      return false;
    } finally {
      loading.value = false;
    }
  }
  
  async function register(registerData: RegisterData) {
    try {
      loading.value = true;
      error.value = null;
      
      // Register new user
      const response = await api.post('/auth/register', {
        email: registerData.email,
        password: registerData.password,
        full_name: registerData.full_name,
        role: registerData.role || 'customer',
      });
      
      // Auto-login after registration
      return await login({
        email: registerData.email,
        password: registerData.password
      });
    } catch (err: any) {
      // Extract error message from new centralized error format
      error.value = err.response?.data?.error?.message || err.response?.data?.detail || 'Registration failed';
      return false;
    } finally {
      loading.value = false;
    }
  }
  
  async function logout() {
    try {
      loading.value = true;
      
      // Call backend logout to clear HTTPOnly cookies
      try {
        await api.post('/auth/logout');
      } catch (err) {
        console.warn('Backend logout failed, continuing with client cleanup:', err);
      }
      
      // Clear user state
      user.value = null;
      accessToken.value = null;
      setGlobalToken(null);
      
      // Clear tokens from storage
      safeStorage.removeItem('access_token');
      safeStorage.removeItem('refresh_token');
      safeStorage.removeItem('user');
      safeStorage.removeItem('access_token', true);
      safeStorage.removeItem('refresh_token', true);
      safeStorage.removeItem('user', true);
      
      // Note: Navigation is handled by the calling component (e.g., AppNavbar.vue)
      // Store should not handle routing directly
    } catch (error) {
      console.error('Error during logout:', error);
      // Even if there's an error, ensure we're logged out
      user.value = null;
      accessToken.value = null;
      setGlobalToken(null);
    } finally {
      loading.value = false;
    }
  }
  
  async function checkAuth() {
    try {
      loading.value = true;
      const token = safeStorage.getItem('access_token') || safeStorage.getItem('access_token', true);
      
      if (!token) {
        // No token means not authenticated
        user.value = null;
        safeStorage.removeItem('user');
        safeStorage.removeItem('user', true);
        return false;
      }
      
      // Verify token and get user data
      const response = await api.get('/users/me', {
        headers: { Authorization: `Bearer ${token}` },
      });
      
      if (response) {
        // Update store state with fresh user data (interceptor already flattened)
        user.value = response as unknown as User;
        // Persist user to storage
        safeStorage.setItem('user', JSON.stringify(user.value));
        
        // Load restaurant data for printing configurations
        try {
          await loadRestaurant();
        } catch (restaurantError) {
          console.warn('⚠️ Failed to load restaurant data on auth check:', restaurantError);
          // Don't fail auth check if restaurant load fails
        }
        
        return true;
      }
      
      // If no user data, clear auth state
      user.value = null;
      safeStorage.removeItem('user');
      safeStorage.removeItem('user', true);
      safeStorage.removeItem('access_token');
      safeStorage.removeItem('access_token', true);
      return false;
    } catch (err: any) {
      console.error('Auth check failed:', err);
      
      // Only clear tokens if it's a 401 (unauthorized) error
      // Don't clear on network errors or other temporary issues
      if (err.response?.status === 401) {
        user.value = null;
        safeStorage.removeItem('user');
        safeStorage.removeItem('user', true);
        safeStorage.removeItem('access_token');
        safeStorage.removeItem('access_token', true);
        safeStorage.removeItem('refresh_token');
        safeStorage.removeItem('refresh_token', true);
      } else {
        // For other errors (network, 500, etc), keep the token
        // Just clear the user from memory
        user.value = null;
      }
      
      return false;
    } finally {
      loading.value = false;
    }
  }
  
  // Load restaurant information
  async function loadRestaurant() {
    try {
      restaurant.value = await api.get('/restaurants/current');
    } catch (err) {
      console.error('Failed to load restaurant:', err);
      restaurant.value = null;
    }
  }
  
  // Initialize the store
  function init() {
    // Check storage availability and warn if needed
    checkStorageAndWarn();
    
    // Get token and user from safe storage
    const token = safeStorage.getItem('access_token') || safeStorage.getItem('access_token', true);
    const storedUser = safeStorage.getItem('user') || safeStorage.getItem('user', true);
    
    if (token && storedUser) {
      try {
        // Restore token to memory cache (CRITICAL for Safari)
        accessToken.value = token;
        setGlobalToken(token);
        
        user.value = JSON.parse(storedUser);
      } catch (err) {
        console.error('Failed to parse stored user data:', err);
        // Clear invalid data
        safeStorage.removeItem('user');
        safeStorage.removeItem('user', true);
        safeStorage.removeItem('access_token');
        safeStorage.removeItem('access_token', true);
        user.value = null;
      }
    } else if (!token && storedUser) {
      // If we have user data but no token, clear the stale user data
      safeStorage.removeItem('user');
      safeStorage.removeItem('user', true);
      user.value = null;
    } else if (!token && !storedUser) {
      user.value = null;
    }
  }
  
  // Initialize on store creation
  init();
  
  return {
    // State
    user,
    restaurant,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    
    // Actions
    login,
    register,
    logout,
    checkAuth,
    loadRestaurant,
  };
});

// Export the store instance
export default useAuthStore;
