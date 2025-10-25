import { computed, type Ref } from 'vue';
import type { OrderWithLocalFields, OrderStatus } from '@/utils/orderHelpers';

export type PaymentFilter = 'all' | 'paid' | 'unpaid';
export type OrderTypeFilter = 'all' | 'dine_in' | 'takeaway' | 'delivery';

/**
 * Composable for filtering orders based on status, payment, and order type
 */
export function useOrderFilters(
  orders: Ref<OrderWithLocalFields[]>,
  selectedStatus: Ref<OrderStatus>,
  selectedPaymentFilter: Ref<PaymentFilter>,
  selectedOrderType: Ref<OrderTypeFilter>
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
    
    return filtered;
  });

  const getOrderCount = (status: OrderStatus): number => {
    if (!orders.value || !orders.value.length) return 0;
    if (status === 'all') return orders.value.length;
    return orders.value.filter(order => order.status === status).length;
  };

  return {
    filteredOrders,
    getOrderCount
  };
}
