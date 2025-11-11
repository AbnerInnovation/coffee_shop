import { computed, type Ref } from 'vue';
import type { OrderWithLocalFields, OrderStatus } from '@/utils/orderHelpers';
import { getOrderCount as getOrderCountHelper } from '@/utils/orderHelpers';

export type PaymentFilter = 'all' | 'paid' | 'unpaid';
export type OrderTypeFilter = 'all' | 'dine_in' | 'takeaway' | 'delivery';
export type TableFilter = number | 'all';

/**
 * Composable for filtering orders based on status, payment, order type, and table
 */
export function useOrderFilters(
  orders: Ref<OrderWithLocalFields[]>,
  selectedStatus: Ref<OrderStatus>,
  selectedPaymentFilter: Ref<PaymentFilter>,
  selectedOrderType: Ref<OrderTypeFilter>,
  selectedTableFilter: Ref<TableFilter>
) {
  const filteredOrders = computed<OrderWithLocalFields[]>(() => {
    let filtered = orders.value;
    
    // Filter by status
    if (selectedStatus.value !== 'all') {
      filtered = filtered.filter(order => order.status === selectedStatus.value);
    }
    
    // Filter by payment status
    if (selectedPaymentFilter.value === 'paid') {
      filtered = filtered.filter(order => order.is_paid === true);
    } else if (selectedPaymentFilter.value === 'unpaid') {
      filtered = filtered.filter(order => !order.is_paid);
    }
    
    // Filter by order type
    if (selectedOrderType.value !== 'all') {
      const typeMap: Record<string, string> = {
        'dine_in': 'dine_in',
        'takeaway': 'takeaway',
        'delivery': 'delivery'
      };
      const targetType = typeMap[selectedOrderType.value];
      filtered = filtered.filter(order => {
        const orderType = (order as any).order_type;
        return orderType === targetType;
      });
    }
    
    // Filter by table
    if (selectedTableFilter.value !== 'all') {
      filtered = filtered.filter(order => order.table_id === selectedTableFilter.value);
    }
    
    return filtered;
  });

  // Use centralized helper, with special handling for 'all' status
  const getOrderCount = (status: OrderStatus): number => {
    if (!orders.value || !orders.value.length) return 0;
    if (status === 'all') return orders.value.length;
    return getOrderCountHelper(orders.value, status);
  };

  return {
    filteredOrders,
    getOrderCount
  };
}
