/**
 * Order Item Grouping Utilities
 * 
 * Implements industry-standard item grouping for restaurant POS systems.
 * Items are stored individually in the database (quantity=1) but grouped
 * visually in the UI when they are identical.
 */

import type { OrderItem } from '@/services/orderService';

/**
 * Fingerprint interface for item comparison
 */
interface ItemFingerprint {
  menuItemId: number;
  variantId: number | null;
  specialInstructions: string;
}

/**
 * Grouped item for display purposes
 */
export interface GroupedOrderItem {
  // Original item data
  id?: number;
  menu_item_id: number;
  variant_id?: number | null;
  name: string;
  variant_name?: string;
  price: number;
  category?: string;
  
  // Grouping data
  quantity: number;  // Count of identical items
  item_ids: number[];  // IDs of individual items in this group
  
  // Customization data
  special_instructions?: string | null;
  
  // Display data
  fingerprint: string;  // Unique identifier for this group
  hasCustomizations: boolean;  // Quick check if item has modifications
  status?: string;
}

/**
 * Generates a unique fingerprint for an order item
 * Items with the same fingerprint are considered identical and can be grouped
 */
export function generateItemFingerprint(item: Partial<OrderItem>): string {
  const fingerprint: ItemFingerprint = {
    menuItemId: item.menu_item_id || 0,
    variantId: item.variant_id || null,
    specialInstructions: (item.special_instructions || '').trim()
  };
  
  return JSON.stringify(fingerprint);
}

/**
 * Checks if two items can be grouped together
 */
export function canGroupItems(item1: Partial<OrderItem>, item2: Partial<OrderItem>): boolean {
  return generateItemFingerprint(item1) === generateItemFingerprint(item2);
}

/**
 * Checks if an item has any customizations
 */
export function hasCustomizations(item: Partial<OrderItem>): boolean {
  return !!(item.special_instructions && item.special_instructions.trim().length > 0);
}

/**
 * Groups order items for display
 * Returns an array of grouped items where identical items are combined
 */
export function groupOrderItems(items: OrderItem[]): GroupedOrderItem[] {
  const groups = new Map<string, GroupedOrderItem>();
  
  items.forEach(item => {
    const fingerprint = generateItemFingerprint(item);
    
    if (groups.has(fingerprint)) {
      // Add to existing group
      const group = groups.get(fingerprint)!;
      group.quantity++;
      if (item.id) {
        group.item_ids.push(item.id);
      }
    } else {
      // Create new group
      groups.set(fingerprint, {
        id: item.id,
        menu_item_id: item.menu_item_id,
        variant_id: item.variant_id,
        name: item.menu_item?.name || '',
        variant_name: item.variant?.name,
        price: item.unit_price || 0,
        category: item.menu_item?.category,
        quantity: 1,
        item_ids: item.id ? [item.id] : [],
        special_instructions: item.special_instructions,
        status: item.status,
        fingerprint,
        hasCustomizations: hasCustomizations(item)
      });
    }
  });
  
  return Array.from(groups.values());
}

/**
 * Formats special instructions for display as an array of lines
 */
export function formatSpecialInstructions(specialInstructions: string | null | undefined): string[] {
  if (!specialInstructions || !specialInstructions.trim()) {
    return [];
  }
  
  // Split by pipe separator (used in SpecialNotesBuilder)
  return specialInstructions.split('|').map(s => s.trim()).filter(s => s.length > 0);
}

/**
 * Calculates total price for a grouped item
 */
export function calculateGroupTotal(group: GroupedOrderItem): number {
  return group.price * group.quantity;
}
