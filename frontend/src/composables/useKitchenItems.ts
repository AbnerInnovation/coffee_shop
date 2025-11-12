import type { Order, OrderItem } from '@/services/orderService';
import orderService from '@/services/orderService';
import { 
  getKitchenVisibleItems, 
  areAllItemsPreparing, 
  areAllItemsReady 
} from '@/utils/kitchenHelpers';

/**
 * Composable for kitchen item actions
 * Implements Single Responsibility Principle - only handles item status updates
 */
export function useKitchenItems(refreshOrders: () => Promise<void>) {
  /**
   * Mark individual item as preparing
   */
  const markItemPreparing = async (order: Order, item: OrderItem) => {
    try {
      // Update the item status
      await orderService.updateOrderItemStatus(order.id, item.id, 'preparing');

      // Fetch the updated order to get current state of all items
      const updatedOrder = await orderService.getOrder(order.id);

      // Check if all items are now preparing or beyond
      if (areAllItemsPreparing(updatedOrder) && updatedOrder.status === 'pending') {
        await orderService.updateOrder(order.id, { status: 'preparing' });
      }

      await refreshOrders();
    } catch (error) {
      console.error('Error updating item status:', error);
    }
  };

  /**
   * Mark individual item as ready
   */
  const markItemReady = async (order: Order, item: OrderItem) => {
    try {
      // Update the item status
      await orderService.updateOrderItemStatus(order.id, item.id, 'ready');

      // Fetch the updated order to get current state of all items
      const updatedOrder = await orderService.getOrder(order.id);

      // Check if all items in the order are now ready or delivered
      if (areAllItemsReady(updatedOrder) && updatedOrder.status !== 'ready') {
        await orderService.updateOrder(order.id, { status: 'ready' });
      }

      await refreshOrders();
    } catch (error) {
      console.error('Error updating item status:', error);
    }
  };

  /**
   * Start preparing all pending items in an order
   */
  const startPreparingAllItems = async (order: Order) => {
    try {
      const pendingItems = getKitchenVisibleItems(order).filter(
        item => item.status === 'pending'
      );

      // Update all pending items to preparing
      for (const item of pendingItems) {
        await orderService.updateOrderItemStatus(order.id, item.id, 'preparing');
      }

      // Fetch the updated order to get current state of all items
      const updatedOrder = await orderService.getOrder(order.id);

      // Check if all items are now preparing or beyond
      if (areAllItemsPreparing(updatedOrder) && updatedOrder.status === 'pending') {
        await orderService.updateOrder(order.id, { status: 'preparing' });
      }

      await refreshOrders();
    } catch (error) {
      console.error('Error starting preparation:', error);
    }
  };

  /**
   * Mark all preparing items as ready
   */
  const markAllItemsReady = async (order: Order) => {
    try {
      const preparingItems = getKitchenVisibleItems(order).filter(
        item => item.status === 'preparing'
      );

      // Update all preparing items to ready
      for (const item of preparingItems) {
        await orderService.updateOrderItemStatus(order.id, item.id, 'ready');
      }

      // Fetch the updated order to get current state of all items
      const updatedOrder = await orderService.getOrder(order.id);

      // Check if all items in the order are ready or delivered
      if (areAllItemsReady(updatedOrder) && updatedOrder.status !== 'ready') {
        await orderService.updateOrder(order.id, { status: 'ready' });
      }

      await refreshOrders();
    } catch (error) {
      console.error('Error marking items ready:', error);
    }
  };

  return {
    // Methods
    markItemPreparing,
    markItemReady,
    startPreparingAllItems,
    markAllItemsReady
  };
}
