import { defineStore } from 'pinia';
import type { Ref } from 'vue';
import { ref } from 'vue';
import menuService from '@/services/menuService';
import type { MenuItem } from '@/types/menu';

export const useMenuStore = defineStore('menu', () => {
  const menuItems: Ref<MenuItem[]> = ref<MenuItem[]>([]);
  const categories: Ref<string[]> = ref<string[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Helper to normalize menu item data
  function normalizeMenuItem(item: any): MenuItem {
    // Extract category name whether it's a string or an object
    const category = typeof item.category === 'string' 
      ? item.category 
      : item.category?.name || '';
      
    return {
      id: item.id,
      name: item.name,
      description: item.description || '',
      price: typeof item.price === 'number' ? item.price : parseFloat(item.price) || 0,
      category: category,
      is_available: item.is_available ?? true,
      image_url: item.image_url ?? '',
      variants: Array.isArray(item.variants) 
        ? item.variants.map((v: any) => ({
            id: v.id,
            name: v.name || '',
            price: typeof v.price === 'number' ? v.price : parseFloat(v.price) || 0,
            is_available: v.is_available ?? true
          }))
        : []
    };
  }

  async function fetchMenuItems(category?: string, available?: boolean) {
    loading.value = true;
    error.value = null;
    try {
      const response = await menuService.getMenuItems(category, available);
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
      return normalizeMenuItem(response);
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
      throw new Error(message);
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
      throw new Error(message);
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
      console.log('Returning cached categories:', categories.value);
      return categories.value;
    }
    
    loading.value = true;
    error.value = null;
    try {
      console.log('Fetching categories from API...');
      let categoryData;
      try {
        categoryData = await menuService.getCategories();
        console.log('Raw categories from API:', categoryData);
      } catch (err) {
        console.error('Error fetching categories from API:', err);
        categoryData = []; // Fallback to empty array on error
      }
      
      // Ensure we have valid data
      if (Array.isArray(categoryData) && categoryData.length > 0) {
        // If items are objects with name property, extract names
        if (typeof categoryData[0] === 'object' && categoryData[0] !== null) {
          categories.value = categoryData.map(cat => cat.name || String(cat));
        } else {
          // If it's an array of strings or numbers
          categories.value = categoryData.map(String);
        }
      } else {
        console.warn('No valid categories received from API, using defaults');
        categories.value = [
          'Coffee',
          'Tea',
          'Pastries',
          'Breakfast',
          'Lunch',
          'Drinks',
          'Specials'
        ];
      }
      
      return categories.value;
    } catch (err: any) {
      const message = err.response?.data?.message || err.message || 'Failed to fetch categories';
      error.value = message;
      console.error('Error in getCategories:', err);
      
      // Return default categories on error
      return [
        'Coffee',
        'Tea',
        'Breakfast',
        'Lunch',
        'Drinks',
        'Specials'
      ];
    } finally {
      loading.value = false;
    }
  }

  // Initialize categories when store is created
  getCategories().catch(console.error);

  return {
    menuItems,
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
  };
});
