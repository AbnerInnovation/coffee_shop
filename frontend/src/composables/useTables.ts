import { ref } from 'vue';
import tableService from '@/services/tableService';
import type { Table } from '@/services/tableService';

/**
 * Composable for managing tables state and operations
 * Handles CRUD operations, loading states, and error handling
 */
export function useTables() {
  const tables = ref<Table[]>([]);
  const loading = ref(false);
  const error = ref('');
  const selectedTableId = ref<number | null>(null);

  /**
   * Fetch all tables from the API
   */
  const fetchTables = async () => {
    try {
      loading.value = true;
      error.value = '';
      tables.value = await tableService.getTables();
    } catch (err) {
      console.error('Error fetching tables:', err);
      error.value = 'Failed to load tables. Please try again.';
    } finally {
      loading.value = false;
    }
  };

  /**
   * Create a new table
   */
  const createTable = async (tableData: Partial<Table>) => {
    try {
      error.value = '';
      const normalizedData = {
        number: Number(tableData.number),
        capacity: Number(tableData.capacity),
        location: tableData.location || 'Inside',
        is_occupied: tableData.is_occupied ?? false
      };
      await tableService.createTable(normalizedData);
      await fetchTables();
      return { success: true };
    } catch (err: any) {
      console.error('Error creating table:', err);
      
      // Handle subscription limit errors (403)
      if (err?.response?.status === 403) {
        const errorDetail = err.response?.data?.detail || 
                           err.response?.data?.error?.message || 
                           'Límite de suscripción alcanzado. Por favor mejora tu plan.';
        
        return {
          success: false,
          isLimitError: true,
          message: errorDetail,
          currentUsage: tables.value.length,
          maxLimit: extractMaxLimit(errorDetail)
        };
      }
      
      error.value = err?.response?.data?.detail || 
                   err?.response?.data?.error?.message ||
                   'Failed to create table. Please try again.';
      return { success: false, isLimitError: false };
    }
  };

  /**
   * Update an existing table
   */
  const updateTable = async (tableId: number, tableData: Partial<Table>) => {
    try {
      error.value = '';
      const normalizedData = {
        number: Number(tableData.number),
        capacity: Number(tableData.capacity),
        location: tableData.location || 'Inside',
        is_occupied: tableData.is_occupied ?? false
      };
      await tableService.updateTable(tableId, normalizedData);
      await fetchTables();
      return { success: true };
    } catch (err: any) {
      console.error('Error updating table:', err);
      error.value = err?.response?.data?.detail || 
                   err?.response?.data?.error?.message ||
                   'Failed to update table. Please try again.';
      return { success: false };
    }
  };

  /**
   * Delete a table
   */
  const deleteTable = async (tableId: number) => {
    try {
      error.value = '';
      await tableService.deleteTable(tableId);
      await fetchTables();
      return { success: true };
    } catch (err: any) {
      console.error('Error deleting table:', err);
      error.value = err?.response?.data?.detail || 
                   err?.response?.data?.error?.message ||
                   'Failed to delete table. Please try again.';
      return { success: false };
    }
  };

  /**
   * Toggle table occupancy status
   */
  const toggleOccupancy = async (tableId: number, currentStatus: boolean) => {
    try {
      error.value = '';
      await tableService.updateTableOccupancy(tableId, !currentStatus);
      await fetchTables();
      return { success: true };
    } catch (err: any) {
      console.error('Error updating table status:', err);
      error.value = 'Failed to update table status. Please try again.';
      return { success: false };
    }
  };

  /**
   * Select a table
   */
  const selectTable = (tableId: number | null) => {
    selectedTableId.value = tableId;
  };

  /**
   * Get table by ID
   */
  const getTableById = (tableId: number): Table | undefined => {
    return tables.value.find(t => t.id === tableId);
  };

  /**
   * Extract max limit from error message
   */
  const extractMaxLimit = (errorMessage: string): number | null => {
    const match = errorMessage.match(/Maximum (\d+)/);
    return match ? parseInt(match[1]) : null;
  };

  /**
   * Clear error message
   */
  const clearError = () => {
    error.value = '';
  };

  return {
    // State
    tables,
    loading,
    error,
    selectedTableId,
    
    // Actions
    fetchTables,
    createTable,
    updateTable,
    deleteTable,
    toggleOccupancy,
    selectTable,
    getTableById,
    clearError
  };
}
