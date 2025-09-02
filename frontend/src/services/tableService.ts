import api from './api';
import API_CONFIG from '@/config/api';

export interface Table {
  id: number;
  number: number;
  capacity: number;
  location: string;
  is_occupied: boolean;
  created_at: string;
  updated_at: string;
}

// Use the configured API instance from api.ts
const apiInstance = api;

// Get tables base path from config
const TABLES_BASE_PATH = API_CONFIG.ENDPOINTS.TABLES || '/tables';

// Table Operations
export const getTables = async (params?: {
  skip?: number;
  limit?: number;
  occupied?: boolean;
  capacity?: number;
}): Promise<Table[]> => {
  const response = await apiInstance.get<Table[]>(TABLES_BASE_PATH, { params });
  return Array.isArray(response) ? response : [];
};

export const getTable = async (id: number): Promise<Table> => {
  const response = await apiInstance.get<Table>(`${TABLES_BASE_PATH}/${id}`);
  return response;
};

export const createTable = async (tableData: Omit<Table, 'id' | 'created_at' | 'updated_at'>): Promise<Table> => {
  const response = await apiInstance.post<Table>(TABLES_BASE_PATH, tableData);
  return response;
};

export const updateTable = async (id: number, tableData: Partial<Omit<Table, 'id' | 'created_at' | 'updated_at'>>): Promise<Table> => {
  const response = await apiInstance.put<Table>(`${TABLES_BASE_PATH}/${id}`, tableData);
  return response;
};

export const deleteTable = async (id: number): Promise<boolean> => {
  await apiInstance.delete(`${TABLES_BASE_PATH}/${id}`);
  return true;
};

export const updateTableOccupancy = async (id: number, isOccupied: boolean): Promise<Table> => {
  const response = await apiInstance.patch<Table>(
    `${TABLES_BASE_PATH}/${id}/occupancy`,
    { is_occupied: isOccupied }
  );
  return response;
};

// Export all functions as default
export default {
  getTables,
  getTable,
  createTable,
  updateTable,
  deleteTable,
  updateTableOccupancy,
};
