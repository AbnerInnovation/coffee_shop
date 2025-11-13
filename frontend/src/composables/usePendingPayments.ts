import { ref } from 'vue';
import api from '@/services/api';

export interface Payment {
  id: number;
  restaurant_id: number;
  subscription_id: number;
  plan_id: number;
  amount: number;
  billing_cycle: string;
  payment_method: string;
  reference_number: string;
  payment_date: string | null;
  proof_image_url: string | null;
  notes: string | null;
  status: string;
  created_at: string;
  restaurant_name?: string;
  plan_name?: string;
}

/**
 * Composable for managing pending payments
 */
export function usePendingPayments() {
  const payments = ref<Payment[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const processing = ref(false);

  /**
   * Load pending payments
   */
  const loadPayments = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await api.get('/sysadmin/payments/pending') as unknown as Payment[];
      payments.value = response;
    } catch (err: any) {
      console.error('Error loading payments:', err);
      error.value = err.response?.data?.detail || 'Error loading payments';
    } finally {
      loading.value = false;
    }
  };

  /**
   * Approve a payment
   */
  const approvePayment = async (paymentId: number) => {
    processing.value = true;
    error.value = null;
    
    try {
      await api.post(`/sysadmin/payments/${paymentId}/approve`);
      await loadPayments();
      return true;
    } catch (err: any) {
      console.error('Error approving payment:', err);
      error.value = err.response?.data?.detail || 'Error approving payment';
      return false;
    } finally {
      processing.value = false;
    }
  };

  /**
   * Reject a payment
   */
  const rejectPayment = async (paymentId: number, reason: string) => {
    processing.value = true;
    error.value = null;
    
    try {
      await api.post(`/sysadmin/payments/${paymentId}/reject`, {
        reason: reason.trim()
      });
      await loadPayments();
      return true;
    } catch (err: any) {
      console.error('Error rejecting payment:', err);
      error.value = err.response?.data?.detail || 'Error rejecting payment';
      return false;
    } finally {
      processing.value = false;
    }
  };

  return {
    // State
    payments,
    loading,
    error,
    processing,
    
    // Actions
    loadPayments,
    approvePayment,
    rejectPayment
  };
}
