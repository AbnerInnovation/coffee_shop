import api from './api';
import API_CONFIG from '@/config/api';
import { authService } from './authService';

const CASH_REGISTER_ENDPOINT = API_CONFIG.ENDPOINTS.CASH_REGISTER;

// TypeScript interfaces for cash register data
export interface CashRegisterSession {
  id: number;
  restaurant_id: number;
  cashier_id: number;
  opened_by_user_id: number;
  closed_by_user_id?: number;
  status: 'OPEN' | 'CLOSED';
  initial_balance: number;
  final_balance?: number;
  expected_balance?: number;
  difference?: number;
  notes?: string;
  opened_at: string;
  closed_at?: string;
  created_at: string;
  updated_at: string;
}

export const cashRegisterService = {
  // Past sessions endpoints
  async getPastSessions(filters?: {
    page?: number;
    limit?: number;
    start_date?: string;
    end_date?: string;
    status?: string;
  }): Promise<CashRegisterSession[]> {
    const params = new URLSearchParams();
    if (filters?.page) params.append('page', filters.page.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    if (filters?.start_date) params.append('start_date', filters.start_date);
    if (filters?.end_date) params.append('end_date', filters.end_date);
    if (filters?.status) params.append('status', filters.status);

    const queryString = params.toString();
    const url = `${CASH_REGISTER_ENDPOINT}/sessions${queryString ? `?${queryString}` : ''}`;

    // Backend returns List[CashRegisterSession], interceptor flattens to array
    // The api.get() interceptor returns response.data directly, so we get the array
    return await api.get(url) as unknown as CashRegisterSession[];
  },

  // Session endpoints
  async getCurrentSession() {
    const response = await api.get(`${CASH_REGISTER_ENDPOINT}/sessions/current`);
    const session = response || null;
    return session;
  },

  async getSessionById(sessionId: number) {
    const response = await api.get(`${CASH_REGISTER_ENDPOINT}/sessions/${sessionId}`);
    return response;
  },

  async openSession(initialBalance: number) {
    const currentUser = authService.getStoredUser();
    if (!currentUser) {
      throw new Error('User not authenticated');
    }

    const response = await api.post(`${CASH_REGISTER_ENDPOINT}/sessions`, {
      initial_balance: initialBalance,
      status: 'OPEN',  // Use uppercase to match the database enum
      opened_by_user_id: currentUser.id,
      cashier_id: currentUser.id  // Make sure to include cashier_id
    });
    return response;
  },

  async closeSession(sessionId: number, finalBalance: number, notes?: string) {
    const currentUser = authService.getStoredUser();
    if (!currentUser) {
      throw new Error('User not authenticated');
    }

    const response = await api.patch(`${CASH_REGISTER_ENDPOINT}/sessions/${sessionId}/close`, {
      final_balance: finalBalance,
      notes: notes || `Session closed by ${currentUser.full_name || currentUser.email}`
    });
    return response;
  },

  async cutSession(sessionId: number, paymentBreakdown: { cash: number; card: number; digital: number; other: number }) {
    const response = await api.post(`${CASH_REGISTER_ENDPOINT}/sessions/${sessionId}/cut`, {
      session_id: sessionId,
      cash_payments: paymentBreakdown.cash,
      card_payments: paymentBreakdown.card,
      digital_payments: paymentBreakdown.digital,
      other_payments: paymentBreakdown.other
    });
    return response;
  },

  // Transaction endpoints
  async getTransactions(sessionId: number) {
    const response = await api.get(`${CASH_REGISTER_ENDPOINT}/transactions`, {
      params: { session_id: sessionId }
    });
    return response;
  },

  async createTransaction(transactionData: any) {
    const response = await api.post(`${CASH_REGISTER_ENDPOINT}/transactions`, transactionData);
    return response;
  },

  // Report endpoints
  async getSessionReport(sessionId: number) {
    const response = await api.get(`${CASH_REGISTER_ENDPOINT}/reports/session/${sessionId}`);
    return response;
  },

  async getLastCut(sessionId: number) {
    const response = await api.get(`${CASH_REGISTER_ENDPOINT}/sessions/${sessionId}/last-cut`);
    return response;
  },

  async getDailyReport(date: string) {
    const response = await api.get(`${CASH_REGISTER_ENDPOINT}/reports/daily`, {
      params: { date }
    });
    return response;
  },

  // Order payment integration
  async markOrderAsPaid(orderId: number, paymentMethod: 'cash' | 'card' | 'digital' | 'other') {
    const response = await api.patch(`${API_CONFIG.ENDPOINTS.ORDERS}/${orderId}/pay`, null, {
      params: { payment_method: paymentMethod }
    });
    return response;
  },

  // Expense endpoints
  async addExpense(sessionId: number, expenseData: {
    amount: number;
    description: string;
    category?: string;
  }) {
    const response = await api.post(`${CASH_REGISTER_ENDPOINT}/sessions/${sessionId}/expenses`, {
      amount: expenseData.amount,
      description: expenseData.description,
      category: expenseData.category
    });
    return response;
  },

  // Transaction management
  async deleteTransaction(transactionId: number) {
    const response = await api.delete(`${CASH_REGISTER_ENDPOINT}/transactions/${transactionId}`);
    return response;
  },

  // Advanced Reports
  async getDailySummaries(startDate?: string, endDate?: string) {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const queryString = params.toString();
    const url = `${CASH_REGISTER_ENDPOINT}/reports/daily-summaries${queryString ? `?${queryString}` : ''}`;
    
    const response = await api.get(url);
    return response;
  },

  async getWeeklySummary(startDate?: string, endDate?: string) {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const queryString = params.toString();
    const url = `${CASH_REGISTER_ENDPOINT}/reports/weekly-summary${queryString ? `?${queryString}` : ''}`;
    
    const response = await api.get(url);
    return response;
  },

  // Denomination counting (Mexican Pesos)
  async closeSessionWithDenominations(
    sessionId: number,
    finalBalance: number,
    notes?: string,
    denominations?: {
      bills_1000?: number;
      bills_500?: number;
      bills_200?: number;
      bills_100?: number;
      bills_50?: number;
      bills_20?: number;
      coins_20?: number;
      coins_10?: number;
      coins_5?: number;
      coins_2?: number;
      coins_1?: number;
      coins_50_cent?: number;
    }
  ) {
    const currentUser = authService.getStoredUser();
    if (!currentUser) {
      throw new Error('User not authenticated');
    }

    const response = await api.patch(`${CASH_REGISTER_ENDPOINT}/sessions/${sessionId}/close-with-denominations`, {
      final_balance: finalBalance,
      notes: notes || `Session closed by ${currentUser.full_name || currentUser.email}`,
      denominations: denominations || null
    });
    return response;
  }
};

export default cashRegisterService;
