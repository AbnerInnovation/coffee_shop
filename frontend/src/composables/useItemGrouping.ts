/**
 * Composable for Order Item Grouping
 * 
 * Provides reactive grouping functionality for order items.
 * Items are stored individually but displayed grouped when identical.
 */

import { computed, type Ref } from 'vue';
import type { OrderItem } from '@/services/orderService';
import {
  groupOrderItems,
  type GroupedOrderItem,
  formatSpecialInstructions,
  calculateGroupTotal
} from '@/utils/orderItemGrouping';

export function useItemGrouping(items: Ref<OrderItem[]>) {
  /**
   * Grouped items for display
   * Automatically updates when items change
   */
  const groupedItems = computed(() => {
    return groupOrderItems(items.value);
  });

  /**
   * Total number of individual items (ungrouped count)
   */
  const totalItemCount = computed(() => {
    return items.value.length;
  });

  /**
   * Total number of groups (grouped count)
   */
  const groupCount = computed(() => {
    return groupedItems.value.length;
  });

  /**
   * Total price of all items
   */
  const totalPrice = computed(() => {
    return groupedItems.value.reduce((sum, group) => {
      return sum + calculateGroupTotal(group);
    }, 0);
  });

  /**
   * Get formatted special instructions for a group
   */
  const getFormattedInstructions = (group: GroupedOrderItem): string[] => {
    return formatSpecialInstructions(group.special_instructions);
  };

  /**
   * Check if any items have customizations
   */
  const hasAnyCustomizations = computed(() => {
    return groupedItems.value.some(group => group.hasCustomizations);
  });

  return {
    // Computed properties
    groupedItems,
    totalItemCount,
    groupCount,
    totalPrice,
    hasAnyCustomizations,
    
    // Methods
    getFormattedInstructions
  };
}
