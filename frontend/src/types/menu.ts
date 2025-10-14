export interface MenuItemVariant {
  id?: string | number;
  name: string;
  price: number;
  discount_price?: number;
  is_available?: boolean;
}

// Define a type that represents either a string (category name) or a full Category object
type CategoryInput = string | MenuCategory;

// Define a simplified category type for the form
export type CategoryForm = {
  id?: string | number;
  name: string;
  description?: string;
};

export interface MenuItem {
  id?: string | number;
  name: string;
  description?: string;
  category: string | CategoryForm; // Can be string (name) or full category object
  price: number;
  discount_price?: number;
  image_url?: string;
  is_available?: boolean;
  variants?: MenuItemVariant[];
  created_at?: string;
  updated_at?: string;
}

export interface MenuItemFormData {
  name: string;
  description: string;
  category: string;
  price: number | string;
  discount_price?: number | string;
  is_available: boolean;
  image_url?: string;
  variants: MenuItemVariant[];
}

export interface MenuCategory {
  id: string | number;
  name: string;
  description?: string;
  items?: MenuItem[];
}
