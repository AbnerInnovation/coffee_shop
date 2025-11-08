import type { ExtendedMenuItem, MenuItemVariant, OrderItemWithDetails } from '@/types/order';
import type { Extra } from '@/components/orders/ExtrasSelector.vue';

/**
 * Mapea el tipo de orden del backend al formato del frontend
 */
export function mapOrderTypeToFrontend(backendType: string): 'Dine-in' | 'Takeaway' | 'Delivery' {
  const orderTypeMap: Record<string, 'Dine-in' | 'Takeaway' | 'Delivery'> = {
    'dine_in': 'Dine-in',
    'takeaway': 'Takeaway',
    'delivery': 'Delivery'
  };
  return orderTypeMap[backendType] || 'Dine-in';
}

/**
 * Mapea el tipo de orden del frontend al formato del backend
 */
export function mapOrderTypeToBackend(frontendType: string): string {
  const reverseMap: Record<string, string> = {
    'Dine-in': 'dine_in',
    'Takeaway': 'takeaway',
    'Delivery': 'delivery'
  };
  return reverseMap[frontendType] || 'dine_in';
}

/**
 * Transforma una variante de la API al formato del frontend
 */
export function transformVariantFromAPI(variant: any, itemId: number | string): MenuItemVariant {
  return {
    id: variant.id || 0,
    name: variant.name || '',
    price: typeof variant.price === 'string' ? parseFloat(variant.price) : (variant.price || 0),
    discount_price: variant.discount_price 
      ? (typeof variant.discount_price === 'string' ? parseFloat(variant.discount_price) : variant.discount_price) 
      : undefined,
    price_adjustment: Number(variant.price_adjustment) || 0,
    is_available: Boolean(variant.is_available ?? true),
    is_default: Boolean(variant.is_default ?? false),
    menu_item_id: variant.menu_item_id || itemId || 0,
    created_at: variant.created_at,
    updated_at: variant.updated_at
  };
}

/**
 * Transforma un menu item de la API al formato del frontend
 */
export function transformMenuItemFromAPI(item: any): ExtendedMenuItem {
  const variants: MenuItemVariant[] = (item.variants || []).map((variant: any) => 
    transformVariantFromAPI(variant, item.id)
  );

  return {
    id: Number(item.id) || 0,
    name: item.name || '',
    description: item.description || '',
    price: typeof item.price === 'string' ? parseFloat(item.price) : (item.price || 0),
    discount_price: item.discount_price 
      ? (typeof item.discount_price === 'string' ? parseFloat(item.discount_price) : item.discount_price) 
      : undefined,
    category: item.category || { name: 'Uncategorized' },
    is_available: item.is_available !== false,
    has_variants: variants.length > 0,
    variants: variants.length > 0 ? variants : undefined,
    ingredients: item.ingredients || null
  };
}

/**
 * Transforma una tabla de la API al formato del frontend
 */
export function transformTableFromAPI(table: any) {
  return {
    id: table.id,
    number: table.number, // Keep as number to match Table interface
    capacity: table.capacity,
    status: table.is_occupied ? 'Occupied' : 'Available'
  };
}

/**
 * Transforma un item del formulario a OrderItemWithDetails
 * Incluye búsqueda del menu item y cálculo de precios
 */
export function transformToOrderItemWithDetails(
  item: {
    menu_item_id: number;
    variant_id?: number | null;
    quantity: number;
    notes?: string;
    special_instructions?: string;
    unit_price?: number;
    extras?: Extra[];
    status?: string;
  },
  menuItems: ExtendedMenuItem[]
): OrderItemWithDetails {
  const menuItem = menuItems.find(mi => Number(mi.id) === Number(item.menu_item_id));
  const variant = menuItem?.variants?.find(v => Number(v.id) === Number(item.variant_id));
  
  // Calculate price
  const basePrice = typeof menuItem?.price === 'string' 
    ? parseFloat(menuItem.price) 
    : (menuItem?.price || 0);
  const adjustment = variant?.price_adjustment || 0;
  const price = variant ? basePrice + adjustment : basePrice;

  // Get category name
  const categoryName = menuItem?.category && typeof menuItem.category === 'object' && menuItem.category.name
    ? menuItem.category.name
    : typeof menuItem?.category === 'string'
      ? menuItem.category
      : undefined;

  return {
    id: Number(item.menu_item_id) * 1000 + (item.variant_id ? Number(item.variant_id) : 0),
    menu_item_id: Number(item.menu_item_id),
    variant_id: item.variant_id ? Number(item.variant_id) : null,
    name: menuItem?.name || 'Unknown Item',
    variant_name: variant?.name,
    category: categoryName,
    price,
    quantity: item.quantity,
    notes: item.special_instructions || item.notes,
    special_instructions: item.special_instructions,
    unit_price: item.unit_price ?? price,
    extras: item.extras || [],
    status: item.status
  };
}

/**
 * Crea un item inicial con cantidad 0 para el formulario
 */
export function createInitialFormItem(menuItem: ExtendedMenuItem) {
  return {
    menu_item_id: Number(menuItem.id),
    variant_id: null,
    quantity: 0,
    notes: '',
    special_instructions: '',
    unit_price: menuItem.price,
    extras: []
  };
}

/**
 * Extrae el nombre de categoría de un menu item
 */
export function getCategoryName(menuItem: ExtendedMenuItem | undefined): string | undefined {
  if (!menuItem?.category) return undefined;
  
  if (typeof menuItem.category === 'object' && menuItem.category.name) {
    return menuItem.category.name;
  }
  
  if (typeof menuItem.category === 'string') {
    return menuItem.category;
  }
  
  return undefined;
}

/**
 * Valida si un formulario de orden está completo
 */
export function validateOrderForm(
  form: {
    type: string;
    tableId: number | string | null;
    customerName: string;
  },
  hasItems: boolean
): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!hasItems) {
    errors.push('Debe agregar al menos un item a la orden');
  }

  if (form.type === 'Dine-in' && !form.tableId) {
    errors.push('Debe seleccionar una mesa para órdenes Dine-in');
  }

  if (form.type !== 'Dine-in' && !form.customerName.trim()) {
    errors.push('Debe ingresar el nombre del cliente');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}
