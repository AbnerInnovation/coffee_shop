import { computed, type Ref } from 'vue';
import type { Order } from '@/services/orderService';
import { getKitchenVisibleItems, groupKitchenItems, type GroupedKitchenItem } from '@/utils/kitchenHelpers';

export type KitchenStatusFilter = 'all' | 'pending' | 'preparing' | 'grouped';
export type OrderTypeFilter = 'all' | 'dine_in' | 'takeaway' | 'delivery';

/**
 * Composable for kitchen filtering logic
 * Implements Single Responsibility Principle - only handles filtering
 */
export function useKitchenFilters(
  orders: Ref<Order[]>,
  selectedStatus: Ref<KitchenStatusFilter>,
  selectedOrderType: Ref<OrderTypeFilter>,
  t: (key: string, params?: any) => string
) {
  /**
   * Filter orders by order type
   */
  const ordersByType = computed(() => {
    if (selectedOrderType.value === 'all') {
      return orders.value;
    }
    return orders.value.filter(order => order.order_type === selectedOrderType.value);
  });

  /**
   * Filter orders that have visible items in kitchen
   */
  const ordersWithVisibleItems = computed(() => {
    return ordersByType.value.filter(order => {
      const visibleItems = getKitchenVisibleItems(order);
      return visibleItems.length > 0;
    });
  });

  /**
   * Grouped items view
   */
  const groupedItems = computed<GroupedKitchenItem[]>(() => {
    return groupKitchenItems(ordersByType.value);
  });

  /**
   * Filtered orders based on selected status and order type
   */
  const filteredOrders = computed(() => {
    let result = ordersWithVisibleItems.value;

    // Filter by status (skip for 'all' and 'grouped')
    if (selectedStatus.value !== 'all' && selectedStatus.value !== 'grouped') {
      result = result.filter(order => order.status === selectedStatus.value);
    }

    return result;
  });

  /**
   * Status tabs with counts
   */
  const statusTabs = computed(() => {
    const totalGroupedItems = groupedItems.value.length;

    return [
      {
        value: 'pending' as const,
        label: t('app.views.kitchen.tabs.pending'),
        count: ordersWithVisibleItems.value.filter(o => o.status === 'pending').length
      },
      {
        value: 'preparing' as const,
        label: t('app.views.kitchen.tabs.preparing'),
        count: ordersWithVisibleItems.value.filter(o => o.status === 'preparing').length
      },
      {
        value: 'grouped' as const,
        label: t('app.views.kitchen.tabs.grouped'),
        count: totalGroupedItems
      }
    ];
  });

  /**
   * Order type tabs with counts
   */
  const orderTypeTabs = computed(() => {
    // Count all orders with visible items (before order type filter)
    const allOrdersWithItems = orders.value.filter(order => {
      const visibleItems = getKitchenVisibleItems(order);
      return visibleItems.length > 0;
    });

    return [
      {
        value: 'all' as const,
        label: t('app.views.kitchen.order_type_filter.all'),
        count: allOrdersWithItems.length
      },
      {
        value: 'dine_in' as const,
        label: t('app.views.kitchen.order_type_filter.dine_in'),
        count: allOrdersWithItems.filter(o => o.order_type === 'dine_in').length
      },
      {
        value: 'takeaway' as const,
        label: t('app.views.kitchen.order_type_filter.takeaway'),
        count: allOrdersWithItems.filter(o => o.order_type === 'takeaway').length
      },
      {
        value: 'delivery' as const,
        label: t('app.views.kitchen.order_type_filter.delivery'),
        count: allOrdersWithItems.filter(o => o.order_type === 'delivery').length
      }
    ];
  });

  return {
    // Computed properties
    filteredOrders,
    groupedItems,
    statusTabs,
    orderTypeTabs,
    ordersWithVisibleItems
  };
}
