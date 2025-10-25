import api from './api';

export interface AdminStats {
  total_restaurants: number;
  restaurants_with_subscription: number;
  restaurants_without_subscription: number;
  total_subscriptions: number;
  active_subscriptions: number;
  trial_subscriptions: number;
  cancelled_subscriptions: number;
  expired_subscriptions: number;
  total_monthly_revenue: number;
  total_annual_revenue: number;
  plans_distribution: Record<string, number>;
}

export interface RestaurantWithSubscription {
  id: number;
  name: string;
  subdomain: string;
  email?: string;
  phone?: string;
  is_active: boolean;
  created_at: string;
  subscription_id?: number;
  plan_name?: string;
  plan_tier?: string;
  subscription_status?: string;
  monthly_price?: number;
  trial_end_date?: string;
  current_period_end?: string;
  days_until_renewal?: number;
  is_trial?: boolean;
}

export interface GetRestaurantsParams {
  skip?: number;
  limit?: number;
  search?: string;
  has_subscription?: boolean;
}

export interface CreateSubscriptionData {
  plan_id: number;
  billing_cycle?: 'monthly' | 'annual';
}

export interface UpgradeSubscriptionData {
  new_plan_id: number;
}

export interface CreateRestaurantData {
  name: string;
  subdomain: string;
  email: string;
  phone?: string;
  address?: string;
  description?: string;
}

export interface CreateAdminData {
  full_name: string;
  email: string;
  password: string;
}

class AdminService {
  /**
   * Get system-wide statistics
   */
  async getStats(): Promise<AdminStats> {
    return await api.get('/admin/stats');
  }

  /**
   * Get all restaurants with subscription info
   */
  async getRestaurants(params?: GetRestaurantsParams): Promise<RestaurantWithSubscription[]> {
    return await api.get('/admin/restaurants', { params });
  }

  /**
   * Create a new restaurant (with automatic trial subscription)
   */
  async createRestaurant(data: CreateRestaurantData): Promise<any> {
    return await api.post('/restaurants', data);
  }

  /**
   * Get detailed subscription info for a restaurant
   */
  async getRestaurantSubscription(restaurantId: number): Promise<any> {
    return await api.get(`/admin/restaurants/${restaurantId}/subscription`);
  }

  /**
   * Create a subscription for a restaurant
   */
  async createSubscription(restaurantId: number, data: CreateSubscriptionData): Promise<any> {
    return await api.post(`/admin/restaurants/${restaurantId}/subscription`, data);
  }

  /**
   * Upgrade/change a restaurant's subscription plan
   */
  async upgradeSubscription(restaurantId: number, data: UpgradeSubscriptionData): Promise<any> {
    return await api.put(`/admin/restaurants/${restaurantId}/subscription/upgrade`, data);
  }

  /**
   * Cancel a restaurant's subscription
   */
  async cancelSubscription(restaurantId: number, immediate: boolean = false): Promise<any> {
    return await api.delete(`/admin/restaurants/${restaurantId}/subscription`, {
      params: { immediate }
    });
  }

  /**
   * Get admin users for a restaurant
   */
  async getRestaurantAdmins(restaurantId: number): Promise<any> {
    return await api.get(`/restaurants/${restaurantId}/admins`);
  }

  /**
   * Create an admin user for a restaurant
   */
  async createRestaurantAdmin(restaurantId: number, data: CreateAdminData): Promise<any> {
    return await api.post(`/restaurants/${restaurantId}/admin`, data);
  }
}

export const adminService = new AdminService();
