import api from './api';
import API_CONFIG from '@/config/api';
import type { AxiosResponse } from 'axios';
import type { MenuItem, MenuItemVariant, MenuCategory } from '@/types/menu';

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
  variants?: MenuItemVariant[];
  created_at?: string;
  updated_at?: string;
}

// Use the configured API instance from api.ts
const apiInstance = api;

// Get menu base path from config
const MENU_BASE_PATH = API_CONFIG.ENDPOINTS.MENU || '/api/menu';
const CATEGORIES_BASE_PATH = '/categories';

// Add request interceptor to include auth token
apiInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle errors
apiInstance.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('Unauthorized access - please log in');
    }
    return Promise.reject(error);
  }
);

// Helper to normalize menu item data
const normalizeMenuItem = (item: any): MenuItemResponse => {
  // Ensure variants is always an array and has consistent property names
  const variants = Array.isArray(item.variants) ? item.variants.map((v: any) => ({
    id: v.id,
    name: v.name,
    price: Number(v.price),
    is_available: v.is_available ?? v.isAvailable ?? true,
    isAvailable: v.isAvailable ?? v.is_available ?? true
  })) : [];

  return {
    id: item.id,
    name: item.name,
    description: item.description,
    price: Number(item.price),
    category: item.category,
    is_available: item.is_available ?? item.isAvailable ?? true,
    isAvailable: item.isAvailable ?? item.is_available ?? true,
    image_url: item.image_url ?? item.imageUrl,
    variants,
    created_at: item.created_at,
    updated_at: item.updated_at
  };
};

// Menu Item Operations

export const getMenuItems = async (category?: string, available?: boolean): Promise<MenuItemResponse[]> => {
  const params = new URLSearchParams();
  if (category) params.append('category', category);
  if (available !== undefined) params.append('available', String(available));
  
  const response = await apiInstance.get<MenuItemResponse[]>(
    MENU_BASE_PATH,
    { params }
  );
  
  // The response is already the data we need after the interceptor
  const items = Array.isArray(response) ? response : [];
  return items.map(normalizeMenuItem);
};

export const getMenuItem = async (id: string | number): Promise<MenuItemResponse> => {
  const response = await apiInstance.get<MenuItemResponse>(
    `${MENU_BASE_PATH}/${id}`
  );
  return normalizeMenuItem(response);
};

export const createMenuItem = async (menuItemData: Omit<MenuItem, 'id'>): Promise<MenuItemResponse> => {
  // Prepare the data with proper variant format
  const payload = {
    ...menuItemData,
    // Ensure variants array is included if it exists
    variants: menuItemData.variants?.map(variant => ({
      name: variant.name,
      price: Number(variant.price),
      is_available: variant.is_available ?? true
    })) || []
  };

  const response = await apiInstance.post<MenuItemResponse>(
    MENU_BASE_PATH,
    payload
  );
  return normalizeMenuItem(response);
};

export const updateMenuItem = async (
  id: string | number,
  menuItemData: Partial<Omit<MenuItem, 'id'>> & { category?: string | { name: string } }
): Promise<MenuItemResponse> => {
  // Prepare the data with proper variant format
  const payload = {
    ...menuItemData,
    // Only include variants if they are provided in the update
    ...(menuItemData.variants && {
      variants: menuItemData.variants.map(variant => ({
        ...(variant.id && { id: variant.id }), // Only include id if it exists
        name: variant.name,
        price: Number(variant.price),
        is_available: variant.is_available ?? true
      }))
    })
  };

  const response = await apiInstance.put<MenuItemResponse>(
    `${MENU_BASE_PATH}/${id}`,
    payload
  );
  return normalizeMenuItem(response);
};

export const deleteMenuItem = async (id: string | number): Promise<boolean> => {
  await apiInstance.delete(`${MENU_BASE_PATH}/${id}`);
  return true;
};

export const updateMenuItemAvailability = async (
  id: string | number,
  isAvailable: boolean
): Promise<MenuItemResponse> => {
  const response = await apiInstance.patch<MenuItemResponse>(
    `${MENU_BASE_PATH}/${id}/availability`,
    { is_available: isAvailable }
  );
  return normalizeMenuItem(response);
};

export const getCategories = async (): Promise<MenuCategory[]> => {
  const response = await apiInstance.get<MenuCategory[]>(`${CATEGORIES_BASE_PATH}/`);
  console.log('categories response:', response);
  const arr = Array.isArray(response) ? response : [];
  // The response is already normalized category objects from the backend
  return arr.map((c: any) => ({
    id: c.id,
    name: c.name,
    description: c.description || ''
  } as MenuCategory));
};

// Category CRUD Operations

export const createCategory = async (data: { name: string; description?: string }): Promise<MenuCategory> => {
  const payload = { name: data.name, description: data.description ?? '' };
  const response = await apiInstance.post<MenuCategory>(`${CATEGORIES_BASE_PATH}/`, payload);
  return response as unknown as MenuCategory;
};

export const updateCategory = async (
  id: string | number,
  data: Partial<{ name: string; description?: string }>
): Promise<MenuCategory> => {
  const response = await apiInstance.put<MenuCategory>(`${CATEGORIES_BASE_PATH}/${id}`, data);
  return response as unknown as MenuCategory;
};

export const deleteCategory = async (id: string | number): Promise<boolean> => {
  await apiInstance.delete(`${CATEGORIES_BASE_PATH}/${id}`);
  return true;
};

// Variant Operations

export const addMenuItemVariant = async (
  menuItemId: string | number,
  variant: Omit<MenuItemVariant, 'id'> & { is_available?: boolean }
): Promise<MenuItemVariant> => {
  // Ensure we're using snake_case for the API
  const variantData = {
    ...variant,
    is_available: variant.is_available ?? true
  };
  
  const response = await apiInstance.post<MenuItemVariant>(
    `${MENU_BASE_PATH}/${menuItemId}/variants`,
    variantData
  );
  
  // The response is already the variant data we need after the interceptor
  return response as unknown as MenuItemVariant;
};

export const updateMenuItemVariant = async (
  menuItemId: string | number,
  variantId: string | number,
  variantData: Partial<Omit<MenuItemVariant, 'id'>> & { isAvailable?: boolean }
): Promise<MenuItemVariant> => {
  const data = { ...variantData };
  if ('isAvailable' in data) {
    data.is_available = data.isAvailable;
    delete data.isAvailable;
  }
  
  const response = await apiInstance.put<ApiResponse<MenuItemVariant>>(
    `${MENU_BASE_PATH}/${menuItemId}/variants/${variantId}`,
    data
  );
  return response.data.data;
};

export const deleteMenuItemVariant = async (
  menuItemId: string | number,
  variantId: string | number
): Promise<boolean> => {
  await apiInstance.delete(`${MENU_BASE_PATH}/${menuItemId}/variants/${variantId}`);
  return true;
};

export const toggleVariantAvailability = async (
  menuItemId: string | number,
  variantId: string | number,
  isAvailable: boolean
): Promise<MenuItemVariant> => {
  return updateMenuItemVariant(menuItemId, variantId, { isAvailable });
};

// Export all functions as default
export default {
  // Menu Item operations
  getMenuItems,
  getMenuItem,
  createMenuItem,
  updateMenuItem,
  deleteMenuItem,
  updateMenuItemAvailability,
  getCategories,
  createCategory,
  updateCategory,
  deleteCategory,
  
  // Variant operations
  addMenuItemVariant,
  updateMenuItemVariant,
  deleteMenuItemVariant,
  toggleVariantAvailability
};
