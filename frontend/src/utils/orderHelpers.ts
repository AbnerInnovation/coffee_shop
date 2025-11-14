/**
 * Order helpers and utilities
 * 
 * Provides functions for order management, status handling,
 * data transformation, and validation.
 */

import { useI18n } from 'vue-i18n';

// ==================== Types ====================

/**
 * Backend order status values
 * Represents the actual status stored in the database
 */
export type BackendOrderStatus = 'pending' | 'preparing' | 'ready' | 'completed' | 'cancelled';

/**
 * Frontend order status values
 * Includes 'all' for filtering purposes in the UI
 */
export type OrderStatus = BackendOrderStatus | 'all'

/**
 * Local representation of an order item
 * Includes transformed data for UI display
 */
export interface OrderItemLocal {
  id: number;
  menu_item_id: number;
  name: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  notes?: string;
  variant_id?: number | null;
  variant_name?: string;
  status?: string;
  variant?: { id: number; name: string } | null;
  menu_item?: { id: number; name: string; category?: string; price?: number };
  extras?: Array<{
    id: number;
    name: string;
    price: number;
    quantity: number;
  }>;
}

/**
 * Order with localized fields for UI display
 * Combines backend data with translated/formatted fields
 */
export interface OrderWithLocalFields {
  id: number;
  order_number?: string;
  status: BackendOrderStatus;
  customerName: string;
  table: string;
  total: number;
  createdAt: Date;
  updated_at: string;
  total_amount?: number;
  table_id?: number | null;
  notes?: string | null;
  items: OrderItemLocal[];
  created_at?: string;
  customer_name?: string | null;
  table_number?: number | null;
  is_paid?: boolean;
}

// ==================== Status Functions ====================

/**
 * Gets Tailwind CSS classes for order status badge
 * Returns color-coded classes based on order status
 * 
 * @param status - The order status
 * @returns Tailwind CSS classes string
 * 
 * @example
 * ```typescript
 * const classes = getStatusBadgeClass('pending');
 * // Returns: 'inline-flex items-center ... bg-yellow-100 text-yellow-800'
 * ```
 */
export function getStatusBadgeClass(status: BackendOrderStatus): string {
  const baseClasses = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium';

  switch (status) {
    case 'pending':
      return `${baseClasses} bg-yellow-100 text-yellow-800`;
    case 'preparing':
      return `${baseClasses} bg-blue-100 text-blue-800`;
    case 'ready':
      return `${baseClasses} bg-green-100 text-green-800`;
    case 'completed':
      return `${baseClasses} bg-gray-100 text-gray-800`;
    case 'cancelled':
      return `${baseClasses} bg-red-100 text-red-800`;
    default:
      return `${baseClasses} bg-gray-100 text-gray-800`;
  }
}

// ==================== Formatting Functions ====================

/**
 * Formats a date/time to display only hours and minutes
 * 
 * @param date - Date string or Date object
 * @returns Formatted time string (HH:MM)
 * 
 * @example
 * ```typescript
 * formatTime('2025-11-14T09:30:00');
 * // Returns: '09:30'
 * ```
 */
export function formatTime(date: string | Date): string {
  return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/**
 * Generates a human-readable summary of order items
 * Includes quantities, names, variants, and extras
 * 
 * @param items - Array of order items
 * @returns Comma-separated summary string
 * 
 * @example
 * ```typescript
 * const items = [
 *   { quantity: 2, name: 'Café', variant_name: 'Grande', extras: [{ name: 'Leche' }] },
 *   { quantity: 1, name: 'Croissant', variant_name: null, extras: [] }
 * ];
 * getOrderItemsSummary(items);
 * // Returns: '2x Café - Grande con Leche, 1x Croissant'
 * ```
 */
export function getOrderItemsSummary(items: OrderItemLocal[]): string {
  if (!items || !Array.isArray(items)) return '';
  return items.map(item => {
    let parts: string[] = [];
    
    // Base: quantity and name
    let baseText = `${item.quantity}x ${item.name}`;
    
    // Add variant if present (using dash for cleaner look)
    if (item.variant_name) {
      baseText += ` - ${item.variant_name}`;
    }
    
    parts.push(baseText);
    
    // Add extras if present (using "con" for natural Spanish)
    if (item.extras && item.extras.length > 0) {
      const extrasText = item.extras
        .map(extra => extra.name)
        .join(', ');
      parts.push(`con ${extrasText}`);
    }
    
    return parts.join(' ');
  }).join(', ');
}

/**
 * Gets translated label for order type
 * 
 * @param orderType - Order type code ('dine_in', 'takeaway', 'delivery')
 * @returns Translated order type label
 * 
 * @example
 * ```typescript
 * getOrderTypeLabel('dine_in');
 * // Returns: 'Para comer aquí' (in Spanish)
 * ```
 */
export function getOrderTypeLabel(orderType: string): string {
  const { t } = useI18n();
  const typeMap: Record<string, string> = {
    'dine_in': t('app.views.orders.filters.dine_in') as string,
    'takeaway': t('app.views.orders.filters.takeaway') as string,
    'delivery': t('app.views.orders.filters.delivery') as string
  };
  return typeMap[orderType] || orderType;
}

// ==================== Utility Functions ====================

/**
 * Counts orders with a specific status
 * 
 * @param orders - Array of orders
 * @param status - Status to count
 * @returns Number of orders with the given status
 * 
 * @example
 * ```typescript
 * const pendingCount = getOrderCount(orders, 'pending');
 * // Returns: 5
 * ```
 */
export function getOrderCount(orders: OrderWithLocalFields[], status: OrderStatus): number {
  if (!orders || !orders.length) return 0;
  
  return orders.filter(order => order.status === status).length;
}

/**
 * Validates if an order can be cancelled
 * 
 * Rules:
 * - Cannot cancel paid orders
 * - Can only cancel pending orders
 * - All items must be in pending status
 * 
 * @param order - The order to validate
 * @returns True if order can be cancelled, false otherwise
 * 
 * @example
 * ```typescript
 * const order = { status: 'pending', is_paid: false, items: [...] };
 * if (canCancelOrder(order)) {
 *   // Show cancel button
 * }
 * ```
 */
export function canCancelOrder(order: OrderWithLocalFields): boolean {
  // Cannot cancel paid orders
  if (order.is_paid) return false;
  // Cannot cancel non-pending orders
  if (order.status !== 'pending') return false;
  // If no items, can cancel
  if (!order.items || order.items.length === 0) return true;
  // All items must be pending
  return order.items.every(item => !item.status || item.status === 'pending');
}

// ==================== Data Transformation ====================

/**
 * Transforms order from API format to local UI format
 * 
 * Performs the following transformations:
 * - Maps backend field names to frontend conventions
 * - Translates status and table information
 * - Calculates item totals including extras
 * - Formats dates and times
 * - Adds localized fields for display
 * 
 * @param order - Raw order object from API
 * @param t - i18n translation function
 * @returns Transformed order with local fields, or null if order is invalid
 * 
 * @example
 * ```typescript
 * const apiOrder = await orderService.getOrder(123);
 * const localOrder = transformOrderToLocal(apiOrder, t);
 * // localOrder.table = 'Mesa 5' (translated)
 * // localOrder.customerName = 'Walk-in' (default)
 * ```
 */
export function transformOrderToLocal(order: any, t: any): OrderWithLocalFields | null {
  if (!order) return null;

  const mappedItems = Array.isArray(order.items) ? order.items.map((item): OrderItemLocal => {
    const variant = item.variant;
    const menuItemName = item.menu_item?.name || 'Unknown Item';
    const variantName = variant?.name;

    const unitPrice = item.unit_price || 0;
    const quantity = item.quantity || 0;
    let total = unitPrice * quantity;
    
    // Add extras to total if present
    if (item.extras && Array.isArray(item.extras)) {
      item.extras.forEach((extra: any) => {
        total += (extra.price || 0) * (extra.quantity || 0);
      });
    }

    return {
      id: item.id,
      menu_item_id: item.menu_item_id,
      name: menuItemName,
      variant_id: item.variant_id,
      variant_name: variantName,
      quantity: quantity,
      unit_price: unitPrice,
      total_price: total,
      notes: item.special_instructions || undefined,
      status: item.status,
      variant: variant ? { id: variant.id, name: variant.name } : null,
      menu_item: item.menu_item ? {
        id: item.menu_item.id,
        name: item.menu_item.name,
        category: item.menu_item.category,
        price: item.menu_item.price
      } : undefined,
      extras: item.extras && Array.isArray(item.extras) ? item.extras.map((extra: any) => ({
        id: extra.id,
        name: extra.name,
        price: extra.price || 0,
        quantity: extra.quantity || 1
      })) : []
    };
  }) : [];

  return {
    ...order,
    customerName: order.customer_name || 'Walk-in',
    table: order.table_number 
      ? t('app.views.cashRegister.table_number', { number: order.table_number }) 
      : t('app.views.cashRegister.takeaway'),
    total: order.total_amount || 0,
    createdAt: new Date(order.created_at || new Date()),
    items: mappedItems,
    status: order.status as BackendOrderStatus,
    table_number: order.table_number,
    customer_name: order.customer_name,
    notes: order.notes,
    updated_at: order.updated_at,
    is_paid: (order as any).is_paid ?? false
  };
}
