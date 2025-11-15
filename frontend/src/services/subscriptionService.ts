import api from './api';

export interface SubscriptionPlan {
  id: number;
  name: string;
  tier: string;
  display_name: string;
  description: string;
  monthly_price: number;
  annual_price: number;
  max_admin_users: number;
  max_waiter_users: number;
  max_cashier_users: number;
  max_kitchen_users: number;
  max_owner_users: number;
  max_tables: number;
  max_menu_items: number;
  max_categories: number;
  has_kitchen_module: boolean;
  has_ingredients_module: boolean;
  has_inventory_module: boolean;
  has_advanced_reports: boolean;
  has_multi_branch: boolean;
  has_priority_support: boolean;
  report_retention_days: number;
  support_hours_monthly: number;
  is_trial: boolean;
  trial_duration_days: number;
  is_popular: boolean;
  is_active: boolean;
  sort_order: number;
  features: any;
  created_at: string;
  updated_at: string;
}

export interface SubscriptionAddon {
  id: number;
  name: string;
  code: string;
  display_name: string;
  description: string;
  addon_type: string;
  category: string;
  monthly_price: number;
  is_recurring: boolean;
  is_quantifiable: boolean;
  min_quantity: number;
  max_quantity: number;
  provides_users: number;
  provides_tables: number;
  provides_menu_items: number;
  enables_inventory: boolean;
  enables_advanced_reports: boolean;
  enables_kitchen: boolean;
  available_for_plans: any;
  is_active: boolean;
  is_featured: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface MySubscription {
  has_subscription: boolean;
  subscription?: {
    id: number;
    plan: {
      id: number;
      name: string;
      tier: string;
      is_trial: boolean;
    };
    status: string;
    billing_cycle: string;
    total_price: number;
    start_date: string;
    current_period_end?: string;
    trial_end_date?: string;
    auto_renew: boolean;
    days_until_renewal?: number;
  };
  message?: string;
}

export interface SubscriptionUsage {
  has_subscription: boolean;
  message?: string;
  limits?: Record<string, any>;
  usage?: {
    users: {
      admin: number;
      waiter: number;
      cashier: number;
      kitchen: number;
      owner: number;
    };
    tables: number;
    menu_items: number;
    categories: number;
  };
  percentages?: {
    admin_users: number;
    waiter_users: number;
    cashier_users: number;
    kitchen_users: number;
    owner_users: number;
    tables: number;
    menu_items: number;
    categories: number;
  };
  features?: {
    has_kitchen_module: boolean;
    has_ingredients_module: boolean;
    has_inventory_module: boolean;
    has_advanced_reports: boolean;
    has_multi_branch: boolean;
  };
}

export interface SubscriptionStatus {
  is_active: boolean;
  status: string;
  message: string;
  can_operate: boolean;
  days_remaining: number;
  plan_name?: string;
}

class SubscriptionService {
  /**
   * Get current restaurant's subscription
   */
  async getMySubscription(): Promise<MySubscription> {
    return await api.get('/subscriptions/my-subscription');
  }

  /**
   * Get subscription usage and limits
   */
  async getUsage(): Promise<SubscriptionUsage> {
    return await api.get('/subscriptions/usage');
  }

  /**
   * Get all available subscription plans
   */
  async getPlans(): Promise<SubscriptionPlan[]> {
    return await api.get('/subscriptions/plans');
  }

  /**
   * Get all available add-ons
   */
  async getAddons(): Promise<SubscriptionAddon[]> {
    const response = await api.get('/subscriptions/addons');
    return response as any; // Interceptor already flattens response
  }

  /**
   * Upgrade the current subscription plan
   */
  async upgradePlan(planId: number, billingCycle: 'monthly' | 'annual'): Promise<any> {
    return await api.post('/subscriptions/upgrade', null, {
      params: {
        plan_id: planId,
        billing_cycle: billingCycle
      }
    });
  }

  /**
   * Get a specific plan by ID
   */
  async getPlanById(planId: number): Promise<SubscriptionPlan> {
    return await api.get(`/subscriptions/plans/${planId}`);
  }

  /**
   * Check subscription status (active/expired/suspended)
   */
  async checkStatus(): Promise<SubscriptionStatus> {
    return await api.get('/subscriptions/status');
  }
}

export const subscriptionService = new SubscriptionService();
