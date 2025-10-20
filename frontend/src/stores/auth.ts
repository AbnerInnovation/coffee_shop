import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

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
  const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/api/v1';
  // Get the router instance
  const router = useRouter();
  
  // State
  const user = ref<User | null>(null);
  const loading = ref<boolean>(false);
  const error = ref<string | null>(null);
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
      
      // ALWAYS use localStorage for tokens to ensure they persist across refreshes
      // sessionStorage can be cleared by browsers/extensions
      localStorage.setItem('access_token', access_token);
      
      if (refresh_token) {
        localStorage.setItem('refresh_token', refresh_token);
      }
      
      try {
        // Fetch user data
        const userResponse = await axios.get(`${API_BASE_URL}/users/me`, {
          headers: { Authorization: `Bearer ${access_token}` },
        });
        
        if (userResponse.data) {
          // Update store state
          user.value = userResponse.data;
          localStorage.setItem('user', JSON.stringify(user.value));
          
          // Navigate to menu if router is available
          if (router) {
            await router.push({ name: 'Menu' });
          }
          return true;
        }
      } catch (userError) {
        console.error('Failed to fetch user data:', userError);
        error.value = 'Failed to load user data';
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
      // Clear from both storages
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      sessionStorage.removeItem('access_token');
      sessionStorage.removeItem('refresh_token');
      sessionStorage.removeItem('user');
      user.value = null;
      
      // Navigate to login page
      await router.push({ name: 'Login' });
    } catch (error) {
      console.error('Error during logout:', error);
      throw error; // Re-throw to be handled by the caller
    } finally {
      loading.value = false;
    }
  }
  
  async function checkAuth() {
    try {
      loading.value = true;
      const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
      
      if (!token) {
        // No token means not authenticated
        user.value = null;
        localStorage.removeItem('user');
        sessionStorage.removeItem('user');
        return false;
      }
      
      // Verify token and get user data
      const response = await axios.get(`${API_BASE_URL}/users/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      
      if (response.data) {
        // Update store state with fresh user data
        user.value = response.data;
        // Persist user to the same storage as token
        if (sessionStorage.getItem('access_token')) {
          sessionStorage.setItem('user', JSON.stringify(user.value));
        } else {
          localStorage.setItem('user', JSON.stringify(user.value));
        }
        return true;
      }
      
      // If no user data, clear auth state
      user.value = null;
      localStorage.removeItem('user');
      sessionStorage.removeItem('user');
      localStorage.removeItem('access_token');
      sessionStorage.removeItem('access_token');
      return false;
    } catch (err: any) {
      console.error('Auth check failed:', err);
      
      // Only clear tokens if it's a 401 (unauthorized) error
      // Don't clear on network errors or other temporary issues
      if (err.response?.status === 401) {
        user.value = null;
        localStorage.removeItem('user');
        sessionStorage.removeItem('user');
        localStorage.removeItem('access_token');
        sessionStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        sessionStorage.removeItem('refresh_token');
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
    // Prefer localStorage (more reliable across refreshes)
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token');
    const storedUser = localStorage.getItem('user') || sessionStorage.getItem('user');
    
    if (token && storedUser) {
      try {
        user.value = JSON.parse(storedUser);
        // DON'T verify token here - let the router guard do it when needed
        // This prevents clearing tokens on every page load
        // checkAuth() will be called by router guard when navigating
      } catch (err) {
        console.error('Failed to parse stored user data:', err);
        logout();
      }
    } else if (!token && refreshToken) {
      // Attempt silent refresh to keep session
      axios.post(`${API_BASE_URL}/auth/refresh-token`, { refresh_token: refreshToken })
        .then((resp) => {
          const { access_token: newAccess, refresh_token: newRefresh } = resp.data || {};
          if (newAccess) {
            // Persist new token where refresh token was found
            if (sessionStorage.getItem('refresh_token')) {
              sessionStorage.setItem('access_token', newAccess);
            } else {
              localStorage.setItem('access_token', newAccess);
            }
          }
          if (newRefresh) {
            if (sessionStorage.getItem('refresh_token')) {
              sessionStorage.setItem('refresh_token', newRefresh);
            } else {
              localStorage.setItem('refresh_token', newRefresh);
            }
          }
          // After obtaining new token, try loading user
          return axios.get(`${API_BASE_URL}/users/me`, {
            headers: { Authorization: `Bearer ${newAccess}` },
          });
        })
        .then((userResp) => {
          if (userResp && userResp.data) {
            user.value = userResp.data;
            if (sessionStorage.getItem('access_token')) {
              sessionStorage.setItem('user', JSON.stringify(user.value));
            } else {
              localStorage.setItem('user', JSON.stringify(user.value));
            }
          }
        })
        .catch(() => {
          // If refresh fails, clear stored tokens
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          sessionStorage.removeItem('access_token');
          sessionStorage.removeItem('refresh_token');
          sessionStorage.removeItem('user');
          user.value = null;
        });
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
