import api from './api';
import API_CONFIG from '@/config/api';
import { authService } from './authService';

const CASH_REGISTER_ENDPOINT = API_CONFIG.ENDPOINTS.CASH_REGISTER;

export const cashRegisterService = {
  // Session endpoints
  async getCurrentSession() {
    console.log('Fetching current session from:', `${CASH_REGISTER_ENDPOINT}/sessions/current`)
    const response = await api.get(`${CASH_REGISTER_ENDPOINT}/sessions/current`);
    console.log('Current session API response:', response)
    const session = response || null;
    console.log('Processed session data:', session)
    return session;
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
  }
};

export default cashRegisterService;
