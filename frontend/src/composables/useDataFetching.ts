import { ref, type Ref } from 'vue';
import menuService from '@/services/menuService';
import tableService, { type Table } from '@/services/tableService';
import { transformMenuItemFromAPI, transformTableFromAPI } from '@/utils/orderFormHelpers';
import type { ExtendedMenuItem } from '@/types/order';

/**
 * Composable para gestionar el fetching de datos (menu items y tables)
 * Centraliza la lógica de carga de datos con manejo de estados y errores
 */
export function useDataFetching() {
  // Loading states
  const loading = ref({
    menu: false,
    tables: false
  });

  // Error states
  const error = ref({
    menu: '',
    tables: ''
  });

  // Data
  const menuItems = ref<ExtendedMenuItem[]>([]);
  const availableTables = ref<Array<{
    id: number;
    number: number; // Changed from string to number to match Table interface
    capacity: number;
    status: string;
  }>>([]);

  /**
   * Fetch menu items from API and transform them
   */
  async function fetchMenuItems(
    onSuccess?: () => void,
    onError?: (errorMessage: string) => void
  ): Promise<void> {
    try {
      loading.value.menu = true;
      error.value.menu = '';
      
      const response = await menuService.getMenuItems();
      menuItems.value = response.map((item: any) => transformMenuItemFromAPI(item));
      
      // Call success callback if provided
      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      console.error('Error fetching menu items:', err);
      const errorMessage = 'Failed to load menu items';
      error.value.menu = errorMessage;
      
      // Call error callback if provided
      if (onError) {
        onError(errorMessage);
      }
    } finally {
      loading.value.menu = false;
    }
  }

  /**
   * Fetch available tables from API and transform them
   */
  async function fetchAvailableTables(
    tableId?: number | null,
    onTableSelected?: (tableId: number) => void,
    onError?: (errorMessage: string) => void
  ): Promise<void> {
    try {
      loading.value.tables = true;
      error.value.tables = '';
      
      const tables = await tableService.getTables();
      availableTables.value = tables.map(table => transformTableFromAPI(table));
      
      // If tableId is provided, call the callback to select it
      if (tableId && onTableSelected) {
        onTableSelected(tableId);
      }
    } catch (err) {
      console.error('Error fetching tables:', err);
      const errorMessage = 'Failed to load tables';
      error.value.tables = errorMessage;
      
      // Call error callback if provided
      if (onError) {
        onError(errorMessage);
      }
    } finally {
      loading.value.tables = false;
    }
  }

  /**
   * Fetch both menu items and tables in parallel
   */
  async function fetchAll(
    tableId?: number | null,
    onMenuSuccess?: () => void,
    onTableSelected?: (tableId: number) => void,
    onError?: (errorMessage: string) => void
  ): Promise<void> {
    await Promise.all([
      fetchMenuItems(onMenuSuccess, onError),
      fetchAvailableTables(tableId, onTableSelected, onError)
    ]);
  }

  /**
   * Reset all data and states
   */
  function reset(): void {
    menuItems.value = [];
    availableTables.value = [];
    loading.value.menu = false;
    loading.value.tables = false;
    error.value.menu = '';
    error.value.tables = '';
  }

  return {
    // State
    loading,
    error,
    menuItems,
    availableTables,
    
    // Methods
    fetchMenuItems,
    fetchAvailableTables,
    fetchAll,
    reset
  };
}
