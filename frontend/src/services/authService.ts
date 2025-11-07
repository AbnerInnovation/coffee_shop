import api from './api';
import { safeStorage } from '@/utils/storage';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData extends LoginCredentials {
  full_name: string;
  role?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  refresh_token?: string;
  user: {
    id: string;
    email: string;
    full_name: string;
    role: string;
    is_active: boolean;
  };
}

export const authService = {
  // Note: Storage is now handled by safeStorage utility
  // which provides fallback for iOS/Safari restrictions

  // Login user
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const formData = new URLSearchParams();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    // Axios interceptor already returns response.data
    return await api.post<AuthResponse>(
      '/auth/token',
      formData,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    ) as unknown as AuthResponse;
  },

  // Register new user
  async register(userData: RegisterData): Promise<AuthResponse> {
    // Axios interceptor already returns response.data
    return await api.post<AuthResponse>(
      '/auth/register',
      userData
    ) as unknown as AuthResponse;
  },

  // Get current user
  async getCurrentUser(token: string) {
    // Axios interceptor already returns response.data
    return await api.get('/users/me');
  },

  // Logout (client-side only)
  logout(): void {
    // Clear storage using safe storage
    safeStorage.removeItem('access_token');
    safeStorage.removeItem('refresh_token');
    safeStorage.removeItem('user');
    safeStorage.removeItem('access_token', true);
    safeStorage.removeItem('refresh_token', true);
    safeStorage.removeItem('user', true);
  },

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!(safeStorage.getItem('access_token') || safeStorage.getItem('access_token', true));
  },

  // Get stored auth token
  getToken(): string | null {
    return safeStorage.getItem('access_token') || safeStorage.getItem('access_token', true);
  },

  // Store auth data
  storeAuthData(data: AuthResponse, persistence?: 'local' | 'session'): void {
    const useSession = persistence === 'session';
    safeStorage.setItem('access_token', data.access_token, useSession);
    if (data.refresh_token) {
      safeStorage.setItem('refresh_token', data.refresh_token, useSession);
    }
    if (data.user) {
      safeStorage.setItem('user', JSON.stringify(data.user), useSession);
    }
  },

  // Refresh access token
  async refreshToken(): Promise<AuthResponse | null> {
    const refreshToken = safeStorage.getItem('refresh_token') || safeStorage.getItem('refresh_token', true);
    if (!refreshToken) return null;

    try {
      const response = await api.post<AuthResponse>(
        '/auth/refresh-token',
        { refresh_token: refreshToken },
        {
          headers: {
            'Content-Type': 'application/json',
          },
          _retry: true  // Mark this request to avoid infinite refresh loops
        }
      ) as unknown as AuthResponse; // Axios interceptor already returns response.data
      return response;
    } catch (error) {
      console.error('Failed to refresh token:', error);
      return null;
    }
  },

  // Get stored user data
  getStoredUser() {
    const user = safeStorage.getItem('user') || safeStorage.getItem('user', true);
    return user ? JSON.parse(user) : null;
  },
};
