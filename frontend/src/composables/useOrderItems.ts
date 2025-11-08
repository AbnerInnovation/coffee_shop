import { computed, type Ref } from 'vue';
import type { OrderItemWithDetails, ExtendedMenuItem, MenuItemVariant } from '@/types/order';

export function useOrderItems(formItems: Ref<any[]>) {
  // Increase item quantity
  const increaseQuantity = (item: OrderItemWithDetails) => {
    const existingItem = formItems.value.find(i =>
      i.menu_item_id === item.menu_item_id &&
      ((i.variant_id && item.variant_id) ? i.variant_id === item.variant_id : !i.variant_id && !item.variant_id)
    );

    if (existingItem) {
      existingItem.quantity += 1;
    }
  };

  // Decrease item quantity
  const decreaseQuantity = (item: OrderItemWithDetails) => {
    const existingItemIndex = formItems.value.findIndex(i =>
      i.menu_item_id === item.menu_item_id &&
      ((i.variant_id && item.variant_id) ? i.variant_id === item.variant_id : !i.variant_id && !item.variant_id)
    );

    if (existingItemIndex !== -1) {
      const existingItem = formItems.value[existingItemIndex];
      if (existingItem.quantity > 1) {
        existingItem.quantity -= 1;
      } else {
        formItems.value.splice(existingItemIndex, 1);
      }
    }
  };

  // Get item quantity
  const getItemQuantity = (menuItemId: number | string, variantId?: number | string | null): number => {
    const item = formItems.value.find(item => {
      const matchesMenuItem = Number(item.menu_item_id) === Number(menuItemId);
      const matchesVariant = variantId !== undefined ?
        Number(item.variant_id) === Number(variantId) :
        !item.variant_id;
      return matchesMenuItem && matchesVariant;
    });
    return item ? item.quantity : 0;
  };

  // Calculate item total
  const calculateItemTotal = (item: OrderItemWithDetails): string => {
    const price = item.unit_price !== undefined && item.unit_price !== null ?
      (typeof item.unit_price === 'string' ? parseFloat(item.unit_price) : item.unit_price) :
      (item.price !== undefined && item.price !== null ?
        (typeof item.price === 'string' ? parseFloat(item.price) : item.price) :
        0);

    const extrasTotal = item.extras?.reduce((sum, extra) => {
      const extraPrice = typeof extra.price === 'string' ? parseFloat(extra.price) : extra.price;
      return sum + (extraPrice * extra.quantity);
    }, 0) || 0;

    const total = (price + extrasTotal) * item.quantity;
    return total.toFixed(2);
  };

  // Check if item is locked (in preparation or ready)
  const isItemLocked = (item: OrderItemWithDetails): boolean => {
    const status = (item as any).status;
    return status === 'preparing' || status === 'ready' || status === 'delivered';
  };

  return {
    increaseQuantity,
    decreaseQuantity,
    getItemQuantity,
    calculateItemTotal,
    isItemLocked
  };
}
