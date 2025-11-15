import api from './api';

export type OrderStatus = 'pending' | 'preparing' | 'ready' | 'completed' | 'cancelled' | 'all';

export interface OrderItemExtra {
  id: number;
  order_item_id: number;
  name: string;
  price: number;
  quantity: number;
  created_at: string;
  updated_at: string;
}

export interface OrderItem {
  id: number;
  menu_item_id: number;
  variant_id: number | null;
  quantity: number;
  special_instructions: string | null;
  status: string;
  order_id: number;
  person_id?: number | null;
  created_at: string;
  updated_at: string;
  variant: {
    id: number;
    name: string;
    price: number;
    description: string | null;
  } | null;
  unit_price: number;
  menu_item: {
    id: number;
    name: string;
    description: string;
    price: number;
    category: string;
    category_visible_in_kitchen: boolean;
    image_url: string;
    is_available: boolean;
  };
  extras: OrderItemExtra[];
}

export interface CreateOrderItemData {
  menu_item_id: number;
  variant_id: number | null;
  quantity: number;
  special_instructions: string | null;
  unit_price: number;
  person_id?: number | null;
  extras?: Array<{
    name: string;
    price: number;
    quantity: number;
  }>;
}

export interface OrderPerson {
  id?: number;
  order_id?: number;
  name?: string | null;
  position: number;
  items: OrderItem[];
  created_at?: string;
  updated_at?: string;
}

export interface CreateOrderPersonData {
  name?: string | null;
  position: number;
  items: CreateOrderItemData[];
}

export interface CreateOrderData {
  table_id?: number | null;  // Optional for takeaway/delivery orders
  customer_name?: string | null;  // For takeaway/delivery orders
  order_type?: string;  // Order type: dine_in, takeaway, or delivery
  notes?: string | null;
  items?: CreateOrderItemData[];  // Legacy support
  persons?: CreateOrderPersonData[];  // New multi-diner approach
}

export interface Variant {
  id: number;
  name: string;
  price: number;
  price_adjustment: number;
  is_default: boolean;
  description: string | null;
}

// MenuItem is now defined below with the correct variants type

// Remove OrderItemDetails interface as it's no longer needed

export interface TableDetails {
  id: number;
  number: number;
  capacity: number;
  is_occupied: boolean;
}

export interface Order {
  id: number;
  order_number: number;
  status: OrderStatus;
  created_at: string;
  updated_at: string;
  total_amount: number;
  table_number: number | null;
  table_id: number | null;
  customer_name: string | null;
  user_id: string | null;
  notes: string | null;
  is_paid?: boolean;
  order_type?: string;
  items: OrderItem[];
  persons?: OrderPerson[];  // New multi-diner support
}

// Menu item variant for the frontend
export interface MenuItemVariant {
  id: number;
  name: string;
  price: number;
  description: string | null;
}

// Menu item type for the frontend
export interface MenuItem {
  id: number;
  name: string;
  description?: string;
  price: number;
  category?: string;
  image_url?: string;
  is_available: boolean;
  variants?: MenuItemVariant[];
  has_variants: boolean;
}

const orderService = {
  async createOrder(orderData: CreateOrderData): Promise<Order> {
    try {
      // El interceptor de axios ya devuelve response.data automáticamente
      return await api.post('/orders', orderData) as Order;
    } catch (error: any) {
      if (error.response) {
        throw new Error(error.response.data?.detail || 'Failed to create order');
      } else if (error.request) {
        throw new Error('No response received from the server');
      } else {
        throw error;
      }
    }
  },

  async getOrder(orderId: number): Promise<Order> {
    // El interceptor de axios ya devuelve response.data automáticamente
    return await api.get(`/orders/${orderId}`) as Order;
  },

  async updateOrder(orderId: number, data: { status?: OrderStatus; [key: string]: any }): Promise<Order> {
    // El interceptor de axios ya devuelve response.data automáticamente
    return await api.put(`/orders/${orderId}`, data) as Order;
  },

  async getTableOrders(tableId: number): Promise<Order[]> {
    // El interceptor de axios ya devuelve response.data automáticamente
    return await api.get(`/tables/${tableId}/orders`) as Order[];
  },

  async getActiveOrders(status?: OrderStatus, tableId?: number, sortBy: string = 'orders', hours: number = 24): Promise<Order[]> {
    try {
      const params: { limit: number; status?: OrderStatus; table_id?: number; sort_by?: string; hours?: number } = { 
        limit: 500, 
        sort_by: sortBy,
        hours: hours 
      };
      if (status) {
        params.status = status;
      }
      if (tableId) {
        params.table_id = tableId;
      }
      const response = await api.get<Order[]>('/orders', { params });
      return Array.isArray(response) ? response : [];
    } catch (error: any) {
      console.error('Error fetching active orders:', error);
      if (error?.response) {
        console.error('Error response data:', error.response.data);
        console.error('Error status:', error.response.status);
      }
      throw error;
    }
  },

  async getOrdersByTable(tableId: number): Promise<Order[]> {
    const response = await api.get<Order[]>('/orders', { params: { table_id: tableId, limit: 50 } });
    return Array.isArray(response) ? response : [];
  },

  async markOrderPaid(orderId: number, paymentMethod: 'cash' | 'card' | 'digital' | 'other' = 'cash', currentStatus?: string): Promise<Order> {
    // Si la orden está en status "ready", también cambiar a "completed"
    const params: any = { payment_method: paymentMethod };
    
    if (currentStatus === 'ready') {
      params.status = 'completed';
    }
    
    // El interceptor de axios ya devuelve response.data automáticamente
    return await api.patch(`/orders/${orderId}/pay`, null, {
      params
    }) as Order;
  },

  async addOrderItem(orderId: number, item: { menu_item_id: number; variant_id?: number | null; quantity: number; special_instructions?: string | null; unit_price?: number; person_id?: number | null }): Promise<any> {
    // El interceptor de axios ya devuelve response.data automáticamente
    return await api.post(`/orders/${orderId}/items`, item);
  },

  async addMultipleItemsToOrder(orderId: number, items: CreateOrderItemData[]): Promise<Order> {
    try {
      // El interceptor de axios ya devuelve response.data automáticamente
      return await api.post(`/orders/${orderId}/items/bulk`, items) as Order;
    } catch (error: any) {
      if (error.response) {
        throw new Error(error.response.data?.detail || 'Failed to add items to order');
      } else if (error.request) {
        throw new Error('No response received from the server');
      } else {
        throw error;
      }
    }
  },

  async updateOrderItem(orderId: number, itemId: number, item: { quantity?: number; unit_price?: number; special_instructions?: string | null; variant_id?: number | null }): Promise<any> {
    // El interceptor de axios ya devuelve response.data automáticamente
    return await api.put(`/orders/${orderId}/items/${itemId}`, item);
  },

  async deleteOrderItem(orderId: number, itemId: number): Promise<void> {
    await api.delete(`/orders/${orderId}/items/${itemId}`);
  },

  async getMenuItems(): Promise<MenuItem[]> {
    try {
      // El interceptor de axios ya devuelve response.data automáticamente
      return await api.get('/menu/items') as MenuItem[];
    } catch (error) {
      console.error('Error fetching menu items:', error);
      throw error;
    }
  },

  // Order Item Extras
  async addExtraToOrderItem(orderId: number, itemId: number, extra: { name: string; price: number; quantity: number }): Promise<OrderItemExtra> {
    try {
      return await api.post(`/orders/${orderId}/items/${itemId}/extras`, extra) as OrderItemExtra;
    } catch (error: any) {
      if (error.response) {
        throw new Error(error.response.data?.detail || 'Failed to add extra to order item');
      }
      throw error;
    }
  },

  async getOrderItemExtras(orderId: number, itemId: number): Promise<OrderItemExtra[]> {
    try {
      return await api.get(`/orders/${orderId}/items/${itemId}/extras`) as OrderItemExtra[];
    } catch (error: any) {
      if (error.response) {
        throw new Error(error.response.data?.detail || 'Failed to get extras');
      }
      throw error;
    }
  },

  async updateOrderItemExtra(orderId: number, itemId: number, extraId: number, extra: { name?: string; price?: number; quantity?: number }): Promise<OrderItemExtra> {
    try {
      return await api.put(`/orders/${orderId}/items/${itemId}/extras/${extraId}`, extra) as OrderItemExtra;
    } catch (error: any) {
      if (error.response) {
        throw new Error(error.response.data?.detail || 'Failed to update extra');
      }
      throw error;
    }
  },

  async deleteOrderItemExtra(orderId: number, itemId: number, extraId: number): Promise<void> {
    try {
      await api.delete(`/orders/${orderId}/items/${itemId}/extras/${extraId}`);
    } catch (error: any) {
      if (error.response) {
        throw new Error(error.response.data?.detail || 'Failed to delete extra');
      }
      throw error;
    }
  },

  async updateOrderItemStatus(orderId: number, itemId: number, status: string): Promise<OrderItem> {
    try {
      // El interceptor de axios ya devuelve response.data automáticamente
      // Status va como query parameter, no en el body
      return await api.patch(`/orders/${orderId}/items/${itemId}/status?status=${status}`) as OrderItem;
    } catch (error) {
      console.error('Error updating order item status:', error);
      throw error;
    }
  },
};

export default orderService;
