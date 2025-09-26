import api from './api';

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
  // Decide which storage to use. If explicit persistence provided, use it; otherwise detect existing.
  getPersistence(): 'local' | 'session' {
    // Prefer session if tokens exist there
    if (sessionStorage.getItem('access_token') || sessionStorage.getItem('refresh_token')) return 'session';
    return 'local';
  },

  getStorage(persistence?: 'local' | 'session'): Storage {
    const mode = persistence || authService.getPersistence();
    return mode === 'session' ? sessionStorage : localStorage;
  },

  // Login user
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const formData = new URLSearchParams();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const response = await api.post<AuthResponse>(
      '/auth/token',
      formData,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );
    return response.data;
  },

  // Register new user
  async register(userData: RegisterData): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>(
      '/auth/register',
      userData
    );
    return response.data;
  },

  // Get current user
  async getCurrentUser(token: string) {
    const response = await api.get('/users/me');
    return response.data;
  },

  // Logout (client-side only)
  logout(): void {
    // Clear both storages to be safe
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    sessionStorage.removeItem('user');
  },

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!(sessionStorage.getItem('access_token') || localStorage.getItem('access_token'));
  },

  // Get stored auth token
  getToken(): string | null {
    return sessionStorage.getItem('access_token') || localStorage.getItem('access_token');
  },

  // Store auth data
  storeAuthData(data: AuthResponse, persistence?: 'local' | 'session'): void {
    const storage = authService.getStorage(persistence);
    storage.setItem('access_token', data.access_token);
    if (data.refresh_token) {
      storage.setItem('refresh_token', data.refresh_token);
    }
    if (data.user) {
      storage.setItem('user', JSON.stringify(data.user));
    }
  },

  // Refresh access token
  async refreshToken(): Promise<AuthResponse | null> {
    const refreshToken = sessionStorage.getItem('refresh_token') || localStorage.getItem('refresh_token');
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
      ) as { data: AuthResponse }; // Type assertion to ensure correct type
      return response.data;
    } catch (error) {
      console.error('Failed to refresh token:', error);
      return null;
    }
  },

  // Get stored user data
  getStoredUser() {
    const user = sessionStorage.getItem('user') || localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },
};
