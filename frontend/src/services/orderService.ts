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
  items: CreateOrderItemData[];
  notes?: string | null;
  user_id?: string | null;
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
  table_number: number;
  table_id: number;
  customer_name: string | null;
  user_id: string | null;
  notes: string | null;
  is_paid?: boolean;
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
      const { data } = await api.post<Order>('/orders', orderData);
      return data;
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
    const response = await api.get<Order>(`/orders/${orderId}`);
    
    return response;
  },

  async updateOrder(orderId: number, data: { status?: OrderStatus; [key: string]: any }): Promise<Order> {
    const { data: responseData } = await api.put<Order>(`/orders/${orderId}`, data);
    return responseData;
  },

  async getTableOrders(tableId: number): Promise<Order[]> {
    const { data } = await api.get<Order[]>(`/tables/${tableId}/orders`);
    return data;
  },

  async getActiveOrders(status?: OrderStatus, tableId?: number): Promise<Order[]> {
    try {
      const params: { limit: number; status?: OrderStatus; table_id?: number } = { limit: 200 };
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

  async markOrderPaid(orderId: number): Promise<Order> {
    const { data } = await api.put<Order>(`/orders/${orderId}`, { is_paid: true });
    return data;
  },

  async addOrderItem(orderId: number, item: { menu_item_id: number; variant_id?: number | null; quantity: number; special_instructions?: string | null; unit_price?: number }): Promise<any> {
    const { data } = await api.post(`/orders/${orderId}/items`, item);
    return data;
  },

  async updateOrderItem(orderId: number, itemId: number, item: { quantity?: number; unit_price?: number; special_instructions?: string | null; variant_id?: number | null }): Promise<any> {
    const { data } = await api.put(`/orders/${orderId}/items/${itemId}`, item);
    return data;
  },

  async deleteOrderItem(orderId: number, itemId: number): Promise<void> {
    await api.delete(`/orders/${orderId}/items/${itemId}`);
  },

  async getMenuItems(): Promise<MenuItem[]> {
    try {
      const { data } = await api.get<MenuItem[]>('/menu/items');
      return data;
    } catch (error) {
      console.error('Error fetching menu items:', error);
      throw error;
    }
  },

  async updateOrderItemStatus(orderId: number, itemId: number, status: string): Promise<OrderItem> {
    try {
      const { data } = await api.patch<OrderItem>(`/orders/${orderId}/items/${itemId}`, { status });
      return data;
    } catch (error) {
      console.error('Error updating order item status:', error);
      throw error;
    }
  },
};

export default orderService;
