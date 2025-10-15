import { getApiBaseUrl } from '@/utils/subdomain';

// API Configuration
const API_CONFIG = {
  // Base URL for all API requests (subdomain-aware)
  get BASE_URL() {
    // Use environment variable if set, otherwise use subdomain-aware URL
    return import.meta.env.VITE_API_URL || getApiBaseUrl();
  },
  
  // API endpoints
  ENDPOINTS: {
    AUTH: '/auth',
    MENU: '/menu',
    TABLES: '/tables',
    ORDERS: '/orders',
    CASH_REGISTER: '/cash-register',
    RESTAURANTS: '/restaurants',
    // Add other endpoints here as needed
  },
  
  // Helper function to get full API URL
  getUrl: function(endpoint: string, path = '') {
    return `${this.BASE_URL}/api/v1${endpoint}${path}`;
  }
};

export default API_CONFIG;
