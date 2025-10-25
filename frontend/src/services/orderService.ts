import api from './api';

export type OrderStatus = 'pending' | 'preparing' | 'ready' | 'completed' | 'cancelled';

export interface OrderItem {
  id: number;
  menu_item_id: number;
  variant_id: number | null;
  quantity: number;
  special_instructions: string | null;
  status: string;
  order_id: number;
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
    image_url: string;
    is_available: boolean;
  };
}

export interface CreateOrderItemData {
  menu_item_id: number;
  variant_id: number | null;
  quantity: number;
  special_instructions: string | null;
  unit_price: number;
}

export interface CreateOrderData {
  table_id?: number | null;  // Optional for takeaway/delivery orders
  customer_name?: string | null;  // For takeaway/delivery orders
  notes?: string | null;
  items: CreateOrderItemData[];
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

  async getActiveOrders(status?: OrderStatus, tableId?: number, sortBy: string = 'orders'): Promise<Order[]> {
    try {
      const params: { limit: number; status?: OrderStatus; table_id?: number; sort_by?: string } = { limit: 200, sort_by: sortBy };
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

  async markOrderPaid(orderId: number, paymentMethod: 'cash' | 'card' | 'digital' | 'other' = 'cash'): Promise<Order> {
    // El interceptor de axios ya devuelve response.data automáticamente
    return await api.patch(`/orders/${orderId}/pay`, null, {
      params: { payment_method: paymentMethod }
    }) as Order;
  },

  async addOrderItem(orderId: number, item: { menu_item_id: number; variant_id?: number | null; quantity: number; special_instructions?: string | null; unit_price?: number }): Promise<any> {
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
