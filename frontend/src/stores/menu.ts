import { defineStore } from 'pinia';
import type { Ref } from 'vue';
import { ref } from 'vue';
import { menuService } from '@/services/menuService';
import type { MenuItem } from '@/components/menu/MenuList.vue';

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
      isAvailable: item.is_available ?? item.isAvailable ?? true,
      imageUrl: item.image_url ?? item.imageUrl ?? '',
      variants: Array.isArray(item.variants) 
        ? item.variants.map((v: any) => ({
            id: v.id,
            name: v.name || '',
            price: typeof v.price === 'number' ? v.price : parseFloat(v.price) || 0,
            isAvailable: v.is_available ?? v.isAvailable ?? true
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
      const response = await menuService.createMenuItem({
        ...menuItemData,
        is_available: menuItemData.isAvailable,
        image_url: menuItemData.imageUrl,
        variants: menuItemData.variants?.map(variant => ({
          ...variant,
          is_available: variant.isAvailable
        }))
      });
      const newItem = normalizeMenuItem(response);
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
      const response = await menuService.updateMenuItem(id, {
        ...menuItemData,
        is_available: menuItemData.isAvailable,
        image_url: menuItemData.imageUrl,
        variants: menuItemData.variants?.map(variant => ({
          ...variant,
          is_available: variant.isAvailable
        }))
      });
      const index = menuItems.value.findIndex(item => item.id === id);
      if (index !== -1) {
        const updatedItem = { ...menuItems.value[index], ...normalizeMenuItem(response) };
        menuItems.value[index] = updatedItem;
        return updatedItem;
      }
      return response;
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
      const response = await menuService.updateMenuItemAvailability(id, !item.isAvailable);
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
      const categoryNames = await menuService.getCategories();
      console.log('Raw categories from API:', categoryNames);
      
      // Ensure we have an array of strings
      if (Array.isArray(categoryNames)) {
        // Filter out any invalid values and ensure uniqueness
        const validCategories = [...new Set(categoryNames)].filter(Boolean);
        console.log('Processed categories:', validCategories);
        categories.value = validCategories;
      } else {
        console.warn('Unexpected categories format:', categoryNames);
        categories.value = [];
      }
      
      // If we still don't have categories, use defaults
      if (categories.value.length === 0) {
        console.warn('No categories found, using defaults');
        categories.value = [
          'Coffee',
          'Tea',
          'Breakfast',
          'Lunch',
          'Snacks',
          'Desserts',
          'Drinks',
          'Specials'
        ];
      }
      
      return categories.value;
    } catch (err: any) {
      const message = err.response?.data?.message || err.message || 'Failed to fetch categories';
      error.value = message;
      console.error('Error fetching categories:', message);
      // Return the current categories if available, or an empty array
      return [...categories.value];
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
