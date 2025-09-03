import api from './api';

export type OrderStatus = 'pending' | 'preparing' | 'ready' | 'completed' | 'cancelled';

export interface OrderItem {
  menu_item_id: number;
  quantity: number;
  special_instructions?: string | null;
  unit_price?: number;  // Add this to match the data we're sending
}

export interface CreateOrderData {
  table_id?: number | null;  // Optional for takeaway/delivery orders
  customer_name?: string | null;  // For takeaway/delivery orders
  items: OrderItem[];
  notes?: string | null;
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
  unit_price?: number;
  menu_item?: MenuItem;
}

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
  customer_name?: string | null;
  table_number?: number | null;
  table_id?: number | null;
  table?: TableDetails;
  notes?: string | null;
  items?: OrderItemDetails[];
}

const orderService = {
  async createOrder(orderData: CreateOrderData): Promise<Order> {
    try {
      const response = await api.post('/orders', orderData);

      return response;
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
    const response = await api.get(`/orders/${orderId}`);
    return response.data;
  },

  async updateOrder(orderId: number, data: { status?: OrderStatus; [key: string]: any }): Promise<Order> {
    const response = await api.put(`/orders/${orderId}`, data);
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
