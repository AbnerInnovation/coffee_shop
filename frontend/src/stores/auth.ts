import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { safeStorage, checkStorageAndWarn } from '@/utils/storage';
import { setGlobalToken } from '@/utils/tokenCache';

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
  // Get the router instance
  const router = useRouter();
  
  // State
  const user = ref<User | null>(null);
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

      const response = await axios.post(`${API_BASE_URL}/auth/token`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const { access_token, refresh_token } = response.data;
      
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
        const userResponse = await axios.get(`${API_BASE_URL}/users/me`, {
          headers: { Authorization: `Bearer ${access_token}` },
        });
        
        if (userResponse.data) {
          // Update store state FIRST
          const userData = userResponse.data;
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
          
          // Navigate based on user role and staff type
          if (router) {
            let redirectRoute = 'Dashboard'; // Default to Dashboard for all
            
            // Redirect based on role and staff_type
            if (userData.role === 'staff' && userData.staff_type) {
              switch (userData.staff_type) {
                case 'cashier':
                  redirectRoute = 'CashRegister';
                  break;
                case 'waiter':
                  redirectRoute = 'Orders';
                  break;
                case 'kitchen':
                  redirectRoute = 'Kitchen';
                  break;
                default:
                  redirectRoute = 'Dashboard';
              }
            }
            
            // Use router.replace instead of push to avoid back button issues
            await router.replace({ name: redirectRoute });
          }
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
      const response = await axios.post(`${API_BASE_URL}/auth/register`, {
        email: registerData.email,
        password: registerData.password,
        full_name: registerData.full_name,
        role: registerData.role || 'user'
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
        await axios.post(`${API_BASE_URL}/auth/logout`);
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
      
      // Use window.location to force a full page reload
      // This avoids issues with dynamic module loading after logout
      window.location.href = '/login';
    } catch (error) {
      console.error('Error during logout:', error);
      // Even if navigation fails, ensure we're logged out
      user.value = null;
      accessToken.value = null;
      setGlobalToken(null);
      // Fallback to window.location
      window.location.href = '/login';
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
      const response = await axios.get(`${API_BASE_URL}/users/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      
      if (response.data) {
        // Update store state with fresh user data
        user.value = response.data;
        // Persist user to storage
        safeStorage.setItem('user', JSON.stringify(user.value));
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
      if (import.meta.env.DEV) {
        console.log('⚠️ User data without token, clearing...');
      }
      safeStorage.removeItem('user');
      safeStorage.removeItem('user', true);
      user.value = null;
    } else if (!token && !storedUser) {
      if (import.meta.env.DEV) {
        console.log('ℹ️ No stored credentials found');
      }
      user.value = null;
    }
  }
  
  // Initialize on store creation
  init();
  
  return {
    // State
    user,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    
    // Actions
    login,
    register,
    logout,
    checkAuth,
  };
});

// Export the store instance
export default useAuthStore;
