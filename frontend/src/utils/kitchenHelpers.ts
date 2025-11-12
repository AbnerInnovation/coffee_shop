import type { Order, OrderItem } from '@/services/orderService';

/**
 * Interface for grouped kitchen items
 */
export interface GroupedKitchenItem {
  menu_item_id: number;
  menu_item_name: string;
  variant_id?: number;
  variant_name?: string;
  category?: string;
  total_quantity: number;
  orders: Array<{
    order_id: number;
    order_number?: number;
    table_number: number | null;
    quantity: number;
  }>;
}

/**
 * Status badge classes mapping
 */
export const STATUS_BADGE_CLASSES = {
  pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200',
  preparing: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200',
  ready: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200',
  completed: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
  delivered: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
  cancelled: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200'
} as const;

/**
 * Get CSS classes for status badge
 */
export function getStatusBadgeClass(status: string): string {
  return STATUS_BADGE_CLASSES[status as keyof typeof STATUS_BADGE_CLASSES] || 'bg-gray-100 text-gray-800';
}

/**
 * Get CSS classes for item status badge
 */
export function getItemStatusBadgeClass(status: string): string {
  return getStatusBadgeClass(status);
}

/**
 * Filter items to show only pending or preparing items
 * Also filters out items whose category is not visible in kitchen
 */
export function getKitchenVisibleItems(order: Order): OrderItem[] {
  return order.items.filter(item => {
    const isActiveStatus = item.status === 'pending' || item.status === 'preparing';
    const isVisibleInKitchen = item.menu_item?.category_visible_in_kitchen !== false;
    return isActiveStatus && isVisibleInKitchen;
  });
}

/**
 * Check if order has pending items
 */
export function hasPendingItems(order: Order): boolean {
  return getKitchenVisibleItems(order).some(item => item.status === 'pending');
}

/**
 * Check if order has preparing items
 */
export function hasPreparingItems(order: Order): boolean {
  return getKitchenVisibleItems(order).some(item => item.status === 'preparing');
}

/**
 * Calculate time elapsed since item was started
 */
export function getTimeElapsed(startedAt: string, t: (key: string, params?: any) => string): string {
  if (!startedAt) return '';
  
  const start = new Date(startedAt).getTime();
  const now = new Date().getTime();
  const diffInMinutes = Math.floor((now - start) / (1000 * 60));
  
  if (diffInMinutes < 1) return t('app.views.kitchen.time.just_now');
  if (diffInMinutes < 60) return t('app.views.kitchen.time.minutes_ago', { m: diffInMinutes });
  
  const hours = Math.floor(diffInMinutes / 60);
  const minutes = diffInMinutes % 60;
  return t('app.views.kitchen.time.hours_minutes_ago', { h: hours, m: minutes });
}

/**
 * Group kitchen items by menu item and variant
 */
export function groupKitchenItems(orders: Order[]): GroupedKitchenItem[] {
  const groups = new Map<string, GroupedKitchenItem>();

  orders.forEach(order => {
    const kitchenItems = getKitchenVisibleItems(order);

    kitchenItems.forEach(item => {
      // Create unique key: menu_item_id + variant_id (if exists)
      const key = `${item.menu_item.id}_${item.variant?.id || 'no-variant'}`;

      if (!groups.has(key)) {
        groups.set(key, {
          menu_item_id: item.menu_item.id,
          menu_item_name: item.menu_item.name,
          variant_id: item.variant?.id,
          variant_name: item.variant?.name,
          category: item.menu_item.category,
          total_quantity: 0,
          orders: []
        });
      }

      const group = groups.get(key)!;
      group.total_quantity += item.quantity;
      group.orders.push({
        order_id: order.id,
        order_number: order.order_number,
        table_number: order.table_number,
        quantity: item.quantity
      });
    });
  });

  // Convert to array and sort by total quantity (descending)
  return Array.from(groups.values()).sort((a, b) => b.total_quantity - a.total_quantity);
}

/**
 * Initialize order items with default statuses
 */
export function initializeOrderItems(order: Order): Order {
  return {
    ...order,
    items: order.items.map(item => ({
      ...item,
      status: item.status || 'pending',
      started_at: (item as any).started_at || order.created_at
    }))
  };
}

/**
 * Check if all items in order are preparing or beyond
 */
export function areAllItemsPreparing(order: Order): boolean {
  return order.items.every(item =>
    item.status === 'preparing' ||
    item.status === 'ready' ||
    item.status === 'delivered'
  );
}

/**
 * Check if all items in order are ready or delivered
 */
export function areAllItemsReady(order: Order): boolean {
  return order.items.every(item =>
    item.status === 'ready' ||
    item.status === 'delivered' ||
    item.status === 'cancelled'
  );
}
