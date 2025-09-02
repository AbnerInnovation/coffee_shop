import api from './api';

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

export interface Order extends CreateOrderData {
  id: number;
  status: 'pending' | 'preparing' | 'ready' | 'served' | 'paid' | 'cancelled';
  created_at: string;
  updated_at: string;
  total_amount: number;
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

  async updateOrderStatus(orderId: number, status: Order['status']): Promise<Order> {
    const response = await api.patch(`/orders/${orderId}/status`, { status });
    return response.data;
  },

  async getTableOrders(tableId: number): Promise<Order[]> {
    const response = await api.get(`/tables/${tableId}/orders`);
    return response.data;
  },

  async getActiveOrders(): Promise<Order[]> {
    const response = await api.get('/orders/active');
    return response.data;
  },
};

export default orderService;
