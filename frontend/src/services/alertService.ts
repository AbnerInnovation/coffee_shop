import api from './api'

export type AlertType = 
  | 'expiring_soon' 
  | 'grace_period' 
  | 'suspended' 
  | 'payment_approved' 
  | 'payment_rejected'

export interface SubscriptionAlert {
  id: number
  restaurant_id: number
  subscription_id: number
  alert_type: AlertType
  title: string
  message: string
  is_read: boolean
  read_at: string | null
  created_at: string
}

export const alertService = {
  /**
   * Get subscription alerts
   */
  async getAlerts(unreadOnly = false): Promise<SubscriptionAlert[]> {
    // Axios interceptor already returns response.data, so response is already the data
    return await api.get('/subscriptions/alerts', {
      params: { unread_only: unreadOnly }
    }) as SubscriptionAlert[]
  },

  /**
   * Mark alerts as read
   */
  async markAsRead(alertIds: number[]): Promise<void> {
    await api.post('/subscriptions/alerts/mark-read', {
      alert_ids: alertIds
    })
  },

  /**
   * Get unread count
   */
  async getUnreadCount(): Promise<number> {
    const alerts = await this.getAlerts(true)
    return alerts.length
  }
}
