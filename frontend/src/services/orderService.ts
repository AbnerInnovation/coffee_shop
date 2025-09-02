import api from './api';

export type OrderStatus = 'pending' | 'preparing' | 'ready' | 'completed' | 'cancelled';

export interface OrderItem {
  menu_item_id: number;
  quantity: number;
  special_instructions?: string;
}

export interface CreateOrderData {
  table_id: number;
  items: OrderItem[];
  notes?: string;
}

export interface MenuItem {
  id: number;
  name: string;
  price: number;
  description?: string;
  category?: string;
  image_url?: string;
  is_available: boolean;
}

export interface OrderItemDetails extends OrderItem {
  id: number;
  name: string;
  price: number;
  menu_item?: MenuItem;
}

export interface Order {
  id: number;
  status: OrderStatus;
  created_at: string;
  updated_at: string;
  total_amount: number;
  customer_name?: string;
  table_number?: number;
  table_id: number;
  notes?: string;
  items?: OrderItemDetails[];
}

const orderService = {
  async createOrder(orderData: CreateOrderData): Promise<Order> {
    const response = await api.post('/orders', orderData);
    return response.data;
  },

  async getOrder(orderId: number): Promise<Order> {
    const response = await api.get(`/orders/${orderId}`);
    return response.data;
  },

  async updateOrderStatus(orderId: number, status: OrderStatus): Promise<Order> {
    const response = await api.patch(`/orders/${orderId}/status`, { status });
    return response.data;
  },

  async getTableOrders(tableId: number): Promise<Order[]> {
    const response = await api.get(`/tables/${tableId}/orders`);
    return response.data;
  },

  async getActiveOrders(status?: OrderStatus): Promise<Order[]> {
    try {
      const params: { limit: number; status?: OrderStatus } = { limit: 200 };
      if (status) {
        params.status = status;
      }
      const response = await api.get('/orders/', { params });
      
      // The response might be the array directly or wrapped in a data property
      const responseData = Array.isArray(response) ? response : 
                         (Array.isArray(response?.data) ? response.data : response);
      
      if (!Array.isArray(responseData)) {
        console.error('Expected array but got:', response);
        return [];
      }
      
      return responseData;
    } catch (error) {
      console.error('Error fetching orders:', error);
      throw error;
    }
  },
};

export default orderService;
