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
    return response.data;
  },

  async closeSession(sessionId: number, finalBalance: number) {
    const currentUser = authService.getStoredUser();
    if (!currentUser) {
      throw new Error('User not authenticated');
    }

    const response = await api.put(`${CASH_REGISTER_ENDPOINT}/sessions/${sessionId}/close`, {
      final_balance: finalBalance,
      actual_balance: finalBalance,  // Assuming actual_balance is the same as final_balance
      status: 'CLOSED',  // Use uppercase to match the database enum
      closed_by_user_id: currentUser.id,
      cashier_id: currentUser.id  // Include cashier_id
    });
    return response.data;
  },

  async cutSession(sessionId: number) {
    const response = await api.post(`${CASH_REGISTER_ENDPOINT}/sessions/${sessionId}/cut`);
    return response.data;
  },

  // Transaction endpoints
  async getTransactions(sessionId: number) {
    const response = await api.get(`${CASH_REGISTER_ENDPOINT}/transactions`, {
      params: { session_id: sessionId }
    });
    return response.data;
  },

  async createTransaction(transactionData: any) {
    const response = await api.post(`${CASH_REGISTER_ENDPOINT}/transactions`, transactionData);
    return response.data;
  },

  // Report endpoints
  async getSessionReport(sessionId: number) {
    const response = await api.get(`${CASH_REGISTER_ENDPOINT}/reports/session/${sessionId}`);
    return response.data;
  },

  async getDailyReport(date: string) {
    const response = await api.get(`${CASH_REGISTER_ENDPOINT}/reports/daily`, {
      params: { date }
    });
    return response.data;
  }
};

export default cashRegisterService;
