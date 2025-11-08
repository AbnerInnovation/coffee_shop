import { ref, type Ref } from 'vue';
import orderService, { type CreateOrderData, type OrderItem } from '@/services/orderService';
import specialNotesService from '@/services/specialNotesService';
import { mapOrderTypeToBackend } from '@/utils/orderFormHelpers';
import type { OrderPerson } from './useMultipleDiners';

/**
 * Composable para gestionar la creación y actualización de órdenes
 * Separa la lógica compleja de creación/edición del componente principal
 */
export function useOrderCreation() {
  /**
   * Valida que la orden tenga items
   */
  function validateHasItems(
    isMultipleDinersMode: boolean,
    persons: OrderPerson[],
    validItems: any[]
  ): boolean {
    if (isMultipleDinersMode) {
      const totalItems = persons.reduce((sum, person) => sum + person.items.length, 0);
      return totalItems > 0;
    }
    return validItems.length > 0;
  }

  /**
   * Construye los updates para una orden existente
   */
  function buildOrderUpdates(
    form: any,
    existingOrder: any
  ): Record<string, any> {
    const updates: any = {};
    
    // Table ID
    const newTableId = form.type === 'Dine-in' ? (form.tableId as number | null) : null;
    if (newTableId !== existingOrder.table_id) {
      updates.table_id = newTableId;
    }
    
    // Notes
    if (form.notes !== (existingOrder.notes || '')) {
      updates.notes = form.notes || null;
    }
    
    // Customer name
    const newCustomerName = form.type !== 'Dine-in' ? (form.customerName || null) : null;
    if (newCustomerName !== (existingOrder.customer_name || null)) {
      updates.customer_name = newCustomerName;
    }
    
    // Order type
    const newOrderType = mapOrderTypeToBackend(form.type);
    const currentOrderType = (existingOrder as any).order_type || 'dine_in';
    if (newOrderType !== currentOrderType) {
      updates.order_type = newOrderType;
    }
    
    return updates;
  }

  /**
   * Actualiza los items de una orden existente (upsert + delete)
   */
  async function updateOrderItems(
    orderId: number,
    validItems: any[],
    existingItems: OrderItem[]
  ): Promise<void> {
    // Build lookup map
    const existingMap = new Map<string, OrderItem>();
    for (const it of existingItems) {
      const key = `${it.menu_item_id}|${it.variant_id ?? ''}`;
      existingMap.set(key, it);
    }

    // Track seen items
    const seenKeys = new Set<string>();

    // Upserts: update existing or add new
    for (const item of validItems) {
      const key = `${item.menu_item_id}|${item.variant_id ?? ''}`;
      const existing = existingMap.get(key);
      
      if (existing) {
        // Update existing item
        const patch: any = {};
        if (existing.quantity !== item.quantity) patch.quantity = item.quantity;
        
        const desiredUnitPrice = item.unit_price ?? existing.unit_price ?? 0;
        if ((existing.unit_price ?? 0) !== desiredUnitPrice) {
          patch.unit_price = desiredUnitPrice;
        }
        
        const si = item.special_instructions ?? null;
        if ((existing.special_instructions ?? null) !== si) {
          patch.special_instructions = si;
        }
        
        const desiredVariantId = item.variant_id ?? null;
        if ((existing.variant_id ?? null) !== desiredVariantId) {
          patch.variant_id = desiredVariantId;
        }
        
        if (Object.keys(patch).length > 0) {
          await orderService.updateOrderItem(orderId, existing.id, patch);
        }
        seenKeys.add(key);
      } else {
        // Add new item
        await orderService.addOrderItem(orderId, {
          menu_item_id: item.menu_item_id,
          variant_id: item.variant_id ?? null,
          quantity: item.quantity,
          special_instructions: item.special_instructions ?? null,
          unit_price: item.unit_price ?? 0,
        });
      }
    }

    // Deletions: remove items no longer present
    for (const [key, ex] of existingMap.entries()) {
      if (!validItems.some(it => `${it.menu_item_id}|${(it.variant_id ?? '')}` === key)) {
        await orderService.deleteOrderItem(orderId, ex.id);
      }
    }
  }

  /**
   * Construye el payload para crear una nueva orden
   */
  function buildOrderPayload(
    form: any,
    isMultipleDinersMode: boolean,
    persons: OrderPerson[],
    validItems: any[]
  ): CreateOrderData {
    const basePayload = {
      table_id: form.type === 'Dine-in' ? (form.tableId as number | null) : null,
      customer_name: form.type !== 'Dine-in' ? (form.customerName || null) : null,
      notes: form.notes || null,
    };

    if (isMultipleDinersMode) {
      // Multiple diners format
      return {
        ...basePayload,
        persons: persons.map(person => ({
          name: person.name || null,
          position: person.position,
          items: person.items.map(it => ({
            menu_item_id: Number(it.menu_item_id),
            variant_id: it.variant_id ? Number(it.variant_id) : null,
            quantity: it.quantity,
            special_instructions: it.special_instructions ?? null,
            unit_price: it.unit_price ?? 0,
            extras: it.extras || [],
          }))
        }))
      };
    } else {
      // Legacy format
      return {
        ...basePayload,
        items: validItems.map(it => ({
          menu_item_id: Number(it.menu_item_id),
          variant_id: it.variant_id ? Number(it.variant_id) : null,
          quantity: it.quantity,
          special_instructions: it.special_instructions ?? null,
          unit_price: it.unit_price ?? 0,
          extras: it.extras || [],
        })),
      };
    }
  }

  /**
   * Maneja el pago de una orden si está marcada como pagada
   */
  async function handleOrderPayment(
    orderId: number,
    markAsPaid: boolean,
    paymentMethod: 'cash' | 'card' | 'digital' | 'other',
    t: (key: string) => string,
    showSuccess: (msg: string) => void,
    showError: (msg: string) => void
  ): Promise<boolean> {
    if (!markAsPaid) {
      showSuccess(t('app.views.orders.messages.order_created_success'));
      return true;
    }

    try {
      await orderService.markOrderPaid(orderId, paymentMethod);
      showSuccess(t('app.views.orders.messages.order_created_and_paid_success') || 'Order created and marked as paid successfully');
      return true;
    } catch (paymentError: any) {
      console.error('Failed to mark order as paid:', paymentError);
      
      const errorDetail = paymentError.response?.data?.detail || '';
      if (errorDetail.includes('No open cash register session found') || errorDetail.includes('cash register session')) {
        showError(t('app.views.cashRegister.cashRegisterSessionRequiredMessage') || 'Please open a cash register session first');
      } else {
        showError(t('app.views.cashRegister.paymentFailedGeneric') || 'Failed to complete payment');
      }
      return false;
    }
  }

  /**
   * Actualiza una orden existente
   */
  async function updateExistingOrder(
    orderId: number,
    form: any,
    existingOrder: any,
    validItems: any[]
  ): Promise<any> {
    // Update order-level fields
    const updates = buildOrderUpdates(form, existingOrder);
    if (Object.keys(updates).length > 0) {
      await orderService.updateOrder(orderId, updates);
    }

    // Update items
    await updateOrderItems(orderId, validItems, existingOrder.items);

    // Get updated order
    return await orderService.getOrder(orderId);
  }

  /**
   * Crea una nueva orden
   */
  async function createNewOrder(
    form: any,
    isMultipleDinersMode: boolean,
    persons: OrderPerson[],
    validItems: any[],
    markAsPaid: boolean,
    paymentMethod: 'cash' | 'card' | 'digital' | 'other',
    t: (key: string) => string,
    showSuccess: (msg: string) => void,
    showError: (msg: string) => void
  ): Promise<{ order: any; paymentSuccess: boolean }> {
    // Build payload
    const orderPayload = buildOrderPayload(form, isMultipleDinersMode, persons, validItems);

    // Create order
    const created = await orderService.createOrder(orderPayload);

    // Handle payment
    const paymentSuccess = await handleOrderPayment(
      created.id,
      markAsPaid,
      paymentMethod,
      t,
      showSuccess,
      showError
    );

    return { order: created, paymentSuccess };
  }

  return {
    validateHasItems,
    buildOrderUpdates,
    updateOrderItems,
    buildOrderPayload,
    handleOrderPayment,
    updateExistingOrder,
    createNewOrder
  };
}
