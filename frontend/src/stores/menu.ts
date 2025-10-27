import { defineStore } from 'pinia';
import type { Ref } from 'vue';
import { ref } from 'vue';
import menuService from '@/services/menuService';
import type { MenuItem, MenuCategory } from '@/types/menu';

export const useMenuStore = defineStore('menu', () => {
  const menuItems: Ref<MenuItem[]> = ref<MenuItem[]>([]);
  // Detailed categories with IDs
  const categoriesDetailed: Ref<MenuCategory[]> = ref<MenuCategory[]>([]);
  // Backwards compatible list of category names used by existing forms/components
  const categories: Ref<string[]> = ref<string[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Helper to normalize menu item data
  function normalizeMenuItem(item: any): MenuItem {
    // Preserve category as object if it has id, otherwise use string
    let category: string | { id: string | number; name: string; description?: string };
    
    if (typeof item.category === 'string') {
      category = item.category;
    } else if (item.category && typeof item.category === 'object' && 'id' in item.category) {
      // Preserve the full category object with id
      category = {
        id: item.category.id,
        name: item.category.name || '',
        description: item.category.description
      };
    } else {
      category = item.category?.name || '';
    }
      
    return {
      id: item.id,
      name: item.name,
      description: item.description || '',
      price: typeof item.price === 'number' ? item.price : parseFloat(item.price) || 0,
      discount_price: item.discount_price ? (typeof item.discount_price === 'number' ? item.discount_price : parseFloat(item.discount_price)) : undefined,
      category: category,
      is_available: item.is_available ?? true,
      image_url: item.image_url ?? '',
      ingredients: item.ingredients || null,
      variants: Array.isArray(item.variants) 
        ? item.variants.map((v: any) => ({
            id: v.id,
            name: v.name || '',
            price: typeof v.price === 'number' ? v.price : parseFloat(v.price) || 0,
            discount_price: v.discount_price ? (typeof v.discount_price === 'number' ? v.discount_price : parseFloat(v.discount_price)) : undefined,
            is_available: v.is_available ?? true
          }))
        : []
    };
  }

  async function fetchMenuItems(categoryId?: number, available?: boolean) {
    loading.value = true;
    error.value = null;
    try {
      const response = await menuService.getMenuItems(categoryId, available);
      menuItems.value = Array.isArray(response) ? response.map(normalizeMenuItem) : [];
      return menuItems.value;
    } catch (err: any) {
      const message = err.response?.data?.message || err.message || 'Failed to fetch menu items';
      error.value = message;
      throw new Error(message);
    } finally {
      loading.value = false;
    }
  }

  async function getMenuItem(id: string | number) {
    loading.value = true;
    error.value = null;
    try {
      const response = await menuService.getMenuItem(id);
      console.log('🔍 Raw response from API:', response);
      console.log('🔍 Response.ingredients:', response.ingredients);
      const normalized = normalizeMenuItem(response);
      console.log('🔍 After normalizeMenuItem:', normalized);
      console.log('🔍 Normalized.ingredients:', normalized.ingredients);
      return normalized;
    } catch (err: any) {
      const message = err.response?.data?.message || err.message || `Failed to fetch menu item ${id}`;
      error.value = message;
      throw new Error(message);
    } finally {
      loading.value = false;
    }
  }

  async function createMenuItem(menuItemData: Omit<MenuItem, 'id'>) {
    loading.value = true;
    error.value = null;
    try {
      // Prepare the data with proper variant format
      const menuItemPayload = {
        ...menuItemData,
        // Ensure variants are properly formatted
        variants: menuItemData.variants?.map(variant => ({
          name: variant.name,
          price: Number(variant.price),
          discount_price: variant.discount_price ? Number(variant.discount_price) : undefined,
          is_available: variant.is_available ?? true
        })) || []
      };
      
      const response = await menuService.createMenuItem(menuItemPayload);
      const newItem = normalizeMenuItem(response);
      
      // Add the new item to the store
      menuItems.value.push(newItem);
      return newItem;
    } catch (err: any) {
      const message = err.response?.data?.message || err.message || 'Failed to create menu item';
      error.value = message;
      // Re-throw the original error to preserve status code and details
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function updateMenuItem(id: string | number, menuItemData: Partial<MenuItem>) {
    loading.value = true;
    error.value = null;
    try {
      // Prepare the data with proper variant format
      const menuItemPayload: any = { ...menuItemData };
      
      // Only include variants if they are provided in the update
      if (menuItemData.variants) {
        menuItemPayload.variants = menuItemData.variants.map(variant => ({
          ...(variant.id && { id: variant.id }), // Only include id if it exists
          name: variant.name,
          price: Number(variant.price),
          discount_price: variant.discount_price ? Number(variant.discount_price) : undefined,
          is_available: variant.is_available ?? true
        }));
      }
      
      const response = await menuService.updateMenuItem(id, menuItemPayload);
      const normalizedItem = normalizeMenuItem(response);
      
      // Update the item in the store
      const index = menuItems.value.findIndex(item => item.id === id);
      if (index !== -1) {
        menuItems.value[index] = normalizedItem;
        return normalizedItem;
      }
      
      // If item wasn't in the store, add it
      menuItems.value.push(normalizedItem);
      return normalizedItem;
    } catch (err: any) {
      const message = err.response?.data?.message || err.message || `Failed to update menu item ${id}`;
      error.value = message;
      // Re-throw the original error to preserve status code and details
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function deleteMenuItem(id: string | number) {
    loading.value = true;
    error.value = null;
    try {
      await menuService.deleteMenuItem(id);
      const index = menuItems.value.findIndex(item => item.id === id);
      if (index !== -1) {
        menuItems.value.splice(index, 1);
      }
      return true;
    } catch (err: any) {
      error.value = err.message || 'Failed to delete menu item';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function toggleMenuItemAvailability(id: string | number) {
    const item = menuItems.value.find(item => item.id === id);
    if (!item) return;
    
    loading.value = true;
    error.value = null;
    try {
      const response = await menuService.updateMenuItemAvailability(id, !item.is_available);
      const updatedItem = normalizeMenuItem(response);
      const index = menuItems.value.findIndex(item => item.id === id);
      if (index !== -1) {
        menuItems.value[index] = updatedItem;
      }
      return updatedItem;
    } catch (err: any) {
      error.value = err.message || 'Failed to update menu item availability';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Get all menu categories
  async function getCategories(forceRefresh = false) {
    // Return cached categories if we have them and don't force refresh
    if (!forceRefresh && categories.value.length > 0) {
      return categories.value;
    }
    
    loading.value = true;
    error.value = null;
    try {
      let categoryData: MenuCategory[] = [];
      try {
        categoryData = await (menuService as any).getCategories();
      } catch (err) {
        console.error('Error fetching categories from API:', err);
        categoryData = []; // Fallback to empty array on error
      }

      if (Array.isArray(categoryData) && categoryData.length > 0) {
        categoriesDetailed.value = categoryData;
        categories.value = categoryData.map(c => c.name);
      } else {
        const defaults: MenuCategory[] = [];
        categoriesDetailed.value = defaults;
        categories.value = defaults.map(c => c.name);
      }

      return categories.value;
    } catch (err: any) {
      const message = err.response?.data?.message || err.message || 'Failed to fetch categories';
      error.value = message;
      console.error('Error in getCategories:', err);
      
      // Return default categories on error
      return [

      ];
    } finally {
      loading.value = false;
    }
  }

  return {
    menuItems,
    categoriesDetailed,
    categories,
    loading,
    error,
    fetchMenuItems,
    getMenuItem,
    createMenuItem,
    updateMenuItem,
    deleteMenuItem,
    toggleMenuItemAvailability,
    getCategories,
    // Category CRUD
    // Now using real backend endpoints
    async createCategory(name: string, description?: string, visibleInKitchen: boolean = true) {
      loading.value = true;
      error.value = null;
      try {
        const created = await menuService.createCategory({ name, description, visible_in_kitchen: visibleInKitchen });
        // Add to local state
        categoriesDetailed.value.push(created);
        categories.value = categoriesDetailed.value.map(c => c.name);
        return created;
      } catch (err: any) {
        error.value = err.response?.data?.detail || err.message || 'Failed to create category';
        throw new Error(error.value || 'Failed to create category');
      } finally {
        loading.value = false;
      }
    },
    async updateCategory(id: string | number, data: { name?: string; description?: string; visible_in_kitchen?: boolean }) {
      loading.value = true;
      error.value = null;
      try {
        const updated = await menuService.updateCategory(id, data);
        // Update in local state
        const idx = categoriesDetailed.value.findIndex(c => c.id === id);
        if (idx !== -1) {
          categoriesDetailed.value[idx] = updated;
        }
        categories.value = categoriesDetailed.value.map(c => c.name);
        return updated;
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to update category';
        error.value = errorMessage;
        throw new Error(errorMessage);
      } finally {
        loading.value = false;
      }
    },
    async deleteCategory(id: string | number) {
      loading.value = true;
      error.value = null;
      try {
        await menuService.deleteCategory(id);
        // Remove from local state
        categoriesDetailed.value = categoriesDetailed.value.filter(c => c.id !== id);
        categories.value = categoriesDetailed.value.map(c => c.name);
        return true;
      } catch (err: any) {
        const errorMessage = err.response?.data?.detail || err.message || 'Failed to delete category';
        error.value = errorMessage;
        throw new Error(errorMessage);
      } finally {
        loading.value = false;
      }
    },
  };
});
