// API Configuration
const API_CONFIG = {
  // Base URL for all API requests
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  
  // API version
  VERSION: 'v1',
  
  // API endpoints
  ENDPOINTS: {
    AUTH: '/auth',
    MENU: '/menu',
    TABLES: '/tables',
    ORDERS: '/orders',
    CASH_REGISTER: '/cash-register',
    // Add other endpoints here as needed
  },
  
  // Helper function to get full API URL
  getUrl: function(endpoint: string, path = '') {
    return `${this.BASE_URL}/api/${this.VERSION}${endpoint}${path}`;
  }
};

export default API_CONFIG;
