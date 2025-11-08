// Order related types and interfaces

export interface MenuItemVariant {
  id: number;
  name: string;
  price: number;
  discount_price?: number;
  price_adjustment: number;
  is_available: boolean;
  is_default: boolean;
  menu_item_id: number;
  created_at?: string;
  updated_at?: string;
}

export interface ExtendedMenuItem {
  id: number;
  name: string;
  description?: string;
  has_variants: boolean;
  variants?: MenuItemVariant[];
  price: number;
  discount_price?: number;
  category?: { name: string } | string;
  ingredients?: any;
  is_available?: boolean;
}

export interface OrderItemWithDetails {
  id?: number;
  menu_item_id: number;
  variant_id?: number | null;
  name: string;
  variant_name?: string;
  category?: string;
  quantity: number;
  unit_price: number;
  price?: number;
  notes?: string;
  special_instructions?: string;
  status?: string;
  extras?: Array<{ 
    name: string; 
    price: number; 
    quantity: number;
  }>;
}

// OrderPerson is now exported from useMultipleDiners composable
// Import it from there to avoid duplication:
// import type { OrderPerson } from '@/composables/useMultipleDiners';

export interface OrderFormData {
  type: 'Dine-in' | 'Takeaway' | 'Delivery';
  tableId: number | string | null;
  customerName: string;
  notes: string;
  items: Array<{
    menu_item_id: number;
    variant_id?: number | null;
    quantity: number;
    notes?: string;
    special_instructions?: string;
    unit_price?: number;
    extras?: Array<{
      name: string;
      price: number;
      quantity: number;
    }>;
  }>;
}
