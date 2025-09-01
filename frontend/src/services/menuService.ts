import api from './api';
import API_CONFIG from '@/config/api';
import type { AxiosResponse } from 'axios';
import type { MenuItem, MenuItemVariant } from '@/components/menu/MenuList.vue';

export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  error?: string;
}

export interface Category {
  id: string | number;
  name: string;
  description?: string;
}

export interface MenuItemResponse {
  id: string | number;
  name: string;
  description?: string;
  price: number | string;
  category: Category;
  is_available?: boolean;
  isAvailable?: boolean;
  image_url?: string;
  variants?: Array<{
    id: string | number;
    name: string;
    price: number | string;
    is_available?: boolean;
    isAvailable?: boolean;
  }>;
}

// Use the configured API instance from api.ts
const apiInstance = api;

// Get menu base path from config
const MENU_BASE_PATH = API_CONFIG.ENDPOINTS.MENU;

// Add request interceptor to include auth token
apiInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    console.log('Request interceptor - Token from localStorage:', token ? 'Token exists' : 'No token found');
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('Authorization header set:', config.headers.Authorization);
    } else {
      console.warn('No access token found in localStorage');
    }
    
    console.log('Request config:', {
      url: config.url,
      method: config.method,
      headers: config.headers,
      data: config.data
    });
    
    return config;
  },
  (error: any) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor to handle errors
apiInstance.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log('Response received:', {
      status: response.status,
      statusText: response.statusText,
      data: response.data,
      headers: response.headers
    });
    return response;
  },
  (error: any) => {
    console.error('Response error:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      headers: error.response?.headers,
      config: {
        url: error.config?.url,
        method: error.config?.method,
        headers: error.config?.headers
      }
    });
    
    if (error.response?.status === 401) {
      console.error('Unauthorized access - Token might be missing, invalid, or expired');
      // Handle unauthorized access (e.g., redirect to login)
      console.error('Unauthorized access - please log in');
      // You might want to redirect to login page here
    }
    return Promise.reject(error);
  }
);

export const menuService = {
  // Get all menu items
  async getMenuItems(category?: string, available?: boolean): Promise<MenuItemResponse[]> {
    try {
      const params = new URLSearchParams();
      if (category) params.append('category', category);
      if (available !== undefined) params.append('available', String(available));
      
      const response = await apiInstance.get<MenuItemResponse[]>(`${MENU_BASE_PATH}/items`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching menu items:', error);
      throw error;
    }
  },

  // Get a single menu item by ID
  async getMenuItem(id: string | number): Promise<MenuItemResponse> {
    try {
      console.log(`Fetching menu item with ID: ${id}`);
      const response = await apiInstance.get<MenuItemResponse>(`${MENU_BASE_PATH}/items/${id}`);
      console.log('Menu item response:', response.data);
      return response.data;
    } catch (error: any) {
      console.error(`Error fetching menu item ${id}:`, {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        message: error.message
      });
      throw new Error(error.response?.data?.detail || `Failed to fetch menu item: ${error.message}`);
    }
  },

  // Create a new menu item
  async createMenuItem(menuItemData: Omit<MenuItem, 'id'>): Promise<MenuItemResponse> {
    try {
      // Get category name from different possible input types
      const categoryName = typeof menuItemData.category === 'string' 
        ? menuItemData.category 
        : menuItemData.category?.name || '';
      
      if (!categoryName) {
        throw new Error('Category name is required');
      }
      
      // Convert to backend schema
      const payload = {
        name: menuItemData.name,
        description: menuItemData.description || undefined,
        price: Number(menuItemData.price),
        category_name: categoryName, // This must match the backend's expected field name
        is_available: menuItemData.isAvailable ?? true,
        image_url: menuItemData.imageUrl || undefined,
      };
      
      console.log('Sending payload to /items:', JSON.stringify(payload, null, 2));
      
      console.log('Sending payload to /items:', payload);
      const response = await apiInstance.post<MenuItemResponse>(`${MENU_BASE_PATH}/items`, payload);
      return response.data;
    } catch (error) {
      console.error('Error creating menu item:', error);
      throw error;
    }
  },

  // Update an existing menu item
  async updateMenuItem(
    id: string | number, 
    menuItemData: Partial<Omit<MenuItem, 'id'>> & { category?: string | { name: string } }
  ): Promise<MenuItemResponse> {
    try {
      // Convert camelCase to snake_case for the backend
      const payload: any = {};
      if (menuItemData.name !== undefined) payload.name = menuItemData.name;
      if (menuItemData.description !== undefined) payload.description = menuItemData.description;
      if (menuItemData.price !== undefined) payload.price = menuItemData.price;
      
      // Handle category - use category_name for updates
      if (menuItemData.category !== undefined) {
        payload.category_name = typeof menuItemData.category === 'string' 
          ? menuItemData.category 
          : menuItemData.category?.name || '';
      }
      
      if (menuItemData.isAvailable !== undefined) payload.is_available = menuItemData.isAvailable;
      if (menuItemData.imageUrl !== undefined) payload.image_url = menuItemData.imageUrl;
      
      if (menuItemData.variants !== undefined) {
        payload.variants = menuItemData.variants.map(variant => ({
          id: variant.id,
          name: variant.name,
          price: variant.price,
          is_available: variant.isAvailable
        }));
      }
      
      const response = await apiInstance.put<MenuItemResponse>(`${MENU_BASE_PATH}/items/${id}`, payload);
      return response.data;
    } catch (error) {
      console.error(`Error updating menu item ${id}:`, error);
      throw error;
    }
  },

  // Delete a menu item
  async deleteMenuItem(id: string | number): Promise<boolean> {
    try {
      await apiInstance.delete(`${MENU_BASE_PATH}/items/${id}`);
      return true;
    } catch (error) {
      console.error(`Error deleting menu item ${id}:`, error);
      throw error;
    }
  },

  // Toggle menu item availability
  async updateMenuItemAvailability(
    id: string | number, 
    isAvailable: boolean
  ): Promise<MenuItemResponse> {
    try {
      const response = await apiInstance.patch<MenuItemResponse>(`${MENU_BASE_PATH}/items/${id}/availability`, { is_available: isAvailable });
      return response.data;
    } catch (error) {
      console.error(`Error toggling availability for menu item ${id}:`, error);
      throw error;
    }
  },

  // Get all menu categories
  getCategories(): Promise<string[]> {
    console.log('Fetching categories from:', `${MENU_BASE_PATH}/categories`);
    return apiInstance.get<Category[]>(`${MENU_BASE_PATH}/categories`)
      .then(response => {
        // Ensure we return an array of category names
        if (!Array.isArray(response.data)) {
          console.warn('Unexpected categories response format:', response.data);
          return [];
        }
        return response.data.map(cat => cat.name || '').filter(Boolean);
      })
      .catch(error => {
        console.error('Error fetching categories:', error);
        // Return default categories if API fails
        return [
          'Coffee',
          'Tea',
          'Breakfast',
          'Lunch',
          'Snacks',
          'Desserts',
          'Drinks',
          'Specials'
        ];
      });
  }
};
