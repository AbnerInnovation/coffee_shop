import api from './api'

export interface RenewalRequest {
  plan_id: number
  billing_cycle: 'monthly' | 'annual'
  notes?: string
}

export interface RenewalResponse {
  payment_id: number
  reference_number: string
  amount: number
  instructions: string
  bank_details: {
    bank: string
    account: string
    clabe: string
    beneficiary: string
  }
}

export interface PaymentSubmitData {
  reference_number: string
  payment_date: string
  proof_image_url?: string
  notes?: string
}

export interface PaymentResponse {
  id: number
  restaurant_id: number
  subscription_id: number
  plan_id: number
  amount: number
  billing_cycle: string
  payment_method: string
  reference_number: string
  payment_date: string | null
  proof_image_url: string | null
  notes: string | null
  status: 'pending' | 'approved' | 'rejected' | 'failed'
  reviewed_by: number | null
  reviewed_at: string | null
  rejection_reason: string | null
  created_at: string
  updated_at: string
  restaurant_name?: string
  plan_name?: string
  reviewer_name?: string
}

export const paymentService = {
  /**
   * Request subscription renewal
   */
  async requestRenewal(data: RenewalRequest): Promise<RenewalResponse> {
    // Axios interceptor already returns response.data
    return await api.post('/subscriptions/request-renewal', data) as RenewalResponse
  },

  /**
   * Submit payment proof
   */
  async submitPayment(paymentId: number, data: PaymentSubmitData): Promise<PaymentResponse> {
    // Axios interceptor already returns response.data
    return await api.post(`/subscriptions/submit-payment/${paymentId}`, data) as PaymentResponse
  },

  /**
   * Get payment status
   */
  async getPaymentStatus(paymentId: number): Promise<PaymentResponse> {
    // Axios interceptor already returns response.data
    return await api.get(`/subscriptions/payment-status/${paymentId}`) as PaymentResponse
  }
}
