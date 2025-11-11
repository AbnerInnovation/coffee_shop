import { useI18n } from 'vue-i18n';

// Types
export type BackendOrderStatus = 'pending' | 'preparing' | 'ready' | 'completed' | 'cancelled';
export type OrderStatus = BackendOrderStatus | 'all'

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

export interface OrderWithLocalFields {
  id: number;
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

// Status badge classes
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

// Format time
export function formatTime(date: string | Date): string {
  return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Get order items summary
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

// Get order type label
export function getOrderTypeLabel(orderType: string): string {
  const { t } = useI18n();
  const typeMap: Record<string, string> = {
    'dine_in': t('app.views.orders.filters.dine_in') as string,
    'takeaway': t('app.views.orders.filters.takeaway') as string,
    'delivery': t('app.views.orders.filters.delivery') as string
  };
  return typeMap[orderType] || orderType;
}

// Get order count by status
export function getOrderCount(orders: OrderWithLocalFields[], status: OrderStatus): number {
  if (!orders || !orders.length) return 0;
  
  return orders.filter(order => order.status === status).length;
}

// Check if order can be cancelled
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

// Transform API order to local format
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
