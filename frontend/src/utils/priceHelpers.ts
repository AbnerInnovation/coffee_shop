import type { ExtendedMenuItem, MenuItemVariant } from '@/types/order';

/**
 * Get effective price considering discount
 */
export function getEffectivePrice(price: number, discountPrice?: number): number {
  if (discountPrice && discountPrice > 0) {
    return discountPrice;
  }
  return price;
}

/**
 * Calculate variant price
 * Prefer absolute variant.price; fallback to base + adjustment
 */
export function getVariantPrice(item: ExtendedMenuItem, variant: MenuItemVariant | null): number {
  const basePrice = typeof item.price === 'string' ? parseFloat(item.price) : (item.price || 0);

  // If variant has an absolute price (not price_adjustment)
  if (variant && typeof (variant as any).price === 'number' && !Number.isNaN((variant as any).price)) {
    const variantPrice = (variant as any).price as number;
    // Use variant's discount_price if available
    return getEffectivePrice(variantPrice, variant.discount_price);
  }

  // For base item or variant with price_adjustment
  // First, get the effective base price (with discount if available)
  const effectiveBasePrice = getEffectivePrice(basePrice, item.discount_price);

  // If variant has price_adjustment, add it
  if (variant && typeof variant.price_adjustment === 'number') {
    return effectiveBasePrice + variant.price_adjustment;
  }

  return effectiveBasePrice;
}

/**
 * Get menu item name by ID
 */
export function getMenuItemName(menuItems: any[], menuItemId: number): string {
  const item = menuItems.find(m => m.id === menuItemId);
  return item?.name || 'Unknown';
}
