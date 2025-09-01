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
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  },

  // Get stored auth token
  getToken(): string | null {
    return localStorage.getItem('access_token');
  },

  // Store auth data
  storeAuthData(data: AuthResponse): void {
    localStorage.setItem('access_token', data.access_token);
    if (data.refresh_token) {
      localStorage.setItem('refresh_token', data.refresh_token);
    }
    if (data.user) {
      localStorage.setItem('user', JSON.stringify(data.user));
    }
  },

  // Refresh access token
  async refreshToken(): Promise<AuthResponse | null> {
    const refreshToken = localStorage.getItem('refresh_token');
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
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },
};
