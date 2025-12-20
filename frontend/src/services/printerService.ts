/**
 * Service for Printer API operations
 */
import api from './api';

export enum PrinterType {
  KITCHEN = 'kitchen',
  BAR = 'bar',
  CASHIER = 'cashier'
}

export enum ConnectionType {
  NETWORK = 'network',
  USB = 'usb',
  BLUETOOTH = 'bluetooth'
}

export interface Printer {
  id: number;
  restaurant_id: number;
  name: string;
  printer_type: PrinterType;
  connection_type: ConnectionType;
  ip_address?: string;
  port?: number;
  device_path?: string;
  paper_width: number;
  is_active: boolean;
  is_default: boolean;
  auto_print: boolean;
  print_copies: number;
  category_ids: number[];
  created_at: string;
  updated_at: string;
}

export interface PrinterCreate {
  name: string;
  printer_type: PrinterType;
  connection_type?: ConnectionType;
  ip_address?: string;
  port?: number;
  device_path?: string;
  paper_width?: number;
  is_active?: boolean;
  is_default?: boolean;
  auto_print?: boolean;
  print_copies?: number;
  category_ids?: number[];
}

export interface PrinterUpdate {
  name?: string;
  printer_type?: PrinterType;
  connection_type?: ConnectionType;
  ip_address?: string;
  port?: number;
  device_path?: string;
  paper_width?: number;
  is_active?: boolean;
  is_default?: boolean;
  auto_print?: boolean;
  print_copies?: number;
  category_ids?: number[];
}

export interface PrinterListResponse {
  printers: Printer[];
  total: number;
}

/**
 * Get all printers for the current restaurant
 */
export const getPrinters = async (
  printerType?: PrinterType,
  isActive?: boolean
): Promise<PrinterListResponse> => {
  const params = new URLSearchParams();
  if (printerType) params.append('printer_type', printerType);
  if (isActive !== undefined) params.append('is_active', String(isActive));
  
  const query = params.toString() ? `?${params.toString()}` : '';
  return await api.get(`/printers${query}`);
};

/**
 * Get a specific printer by ID
 */
export const getPrinter = async (printerId: number): Promise<Printer> => {
  return await api.get(`/printers/${printerId}`);
};

/**
 * Get printers assigned to a specific category
 */
export const getPrintersByCategory = async (categoryId: number): Promise<Printer[]> => {
  return await api.get(`/printers/category/${categoryId}`);
};

/**
 * Get the default printer for a specific type
 */
export const getDefaultPrinter = async (printerType: PrinterType): Promise<Printer> => {
  return await api.get(`/printers/type/${printerType}/default`);
};

/**
 * Create a new printer
 */
export const createPrinter = async (printerData: PrinterCreate): Promise<Printer> => {
  return await api.post('/printers', printerData);
};

/**
 * Update a printer
 */
export const updatePrinter = async (
  printerId: number,
  printerData: PrinterUpdate
): Promise<Printer> => {
  return await api.put(`/printers/${printerId}`, printerData);
};

/**
 * Delete a printer
 */
export const deletePrinter = async (printerId: number): Promise<void> => {
  return await api.delete(`/printers/${printerId}`);
};

/**
 * Assign categories to a printer
 */
export const assignCategoriesToPrinter = async (
  printerId: number,
  categoryIds: number[]
): Promise<Printer> => {
  return await api.post(`/printers/${printerId}/categories`, {
    category_ids: categoryIds
  });
};

/**
 * Get printers grouped by type
 */
export const getPrintersByType = async (): Promise<Record<PrinterType, Printer[]>> => {
  const response = await getPrinters();
  const grouped: Record<PrinterType, Printer[]> = {
    [PrinterType.KITCHEN]: [],
    [PrinterType.BAR]: [],
    [PrinterType.CASHIER]: []
  };
  
  response.printers.forEach(printer => {
    grouped[printer.printer_type].push(printer);
  });
  
  return grouped;
};

/**
 * Get active printers only
 */
export const getActivePrinters = async (): Promise<Printer[]> => {
  const response = await getPrinters(undefined, true);
  return response.printers;
};
