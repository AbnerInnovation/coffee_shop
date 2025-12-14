/**
 * Operation Mode Types
 * 
 * Defines TypeScript types for the operation mode system.
 * These types match the backend enums and configuration.
 */

export enum OperationMode {
  FULL_RESTAURANT = 'full_restaurant',
  POS_ONLY = 'pos_only',
  CAFE_MODE = 'cafe_mode',
  FOOD_TRUCK = 'food_truck',
  QUICK_SERVICE = 'quick_service'
}

export enum OrderType {
  DINE_IN = 'dine_in',
  TAKEAWAY = 'takeaway',
  DELIVERY = 'delivery',
  POS_SALE = 'pos_sale',
  QUICK_SERVICE = 'quick_service'
}

export interface OperationModeConfig {
  // UI Features
  show_tables: boolean
  show_kitchen: boolean
  show_waiters: boolean
  show_delivery: boolean
  
  // Business Logic
  requires_table_for_order: boolean
  allows_pos_sales: boolean
  allows_table_service: boolean
  allows_kitchen_orders: boolean
  
  // Default Settings
  default_order_type: OrderType
  
  // User Types Allowed
  allowed_staff_types: string[]
  
  // Validation Rules
  min_tables: number
  min_menu_items: number
  
  // Ticket Configuration
  use_daily_tickets: boolean
  ticket_prefix: string
}

export interface ModeConfigResponse {
  operation_mode: string
  plan_name: string | null
  config: OperationModeConfig
}

export interface SubscriptionUsageResponse {
  has_subscription: boolean
  operation_mode?: string
  mode_config?: OperationModeConfig
  limits: {
    max_admin_users: number
    max_waiter_users: number
    max_cashier_users: number
    max_kitchen_users: number
    max_owner_users: number
    max_tables: number
    max_menu_items: number
    max_categories: number
  }
  usage: {
    users: {
      admin: number
      waiter: number
      cashier: number
      kitchen: number
    }
    tables: number
    menu_items: number
    categories: number
  }
  percentages: {
    admin_users: number
    waiter_users: number
    cashier_users: number
    kitchen_users: number
    tables: number
    menu_items: number
    categories: number
  }
  features: {
    has_kitchen_module: boolean
    has_ingredients_module: boolean
    has_inventory_module: boolean
    has_advanced_reports: boolean
    has_multi_branch: boolean
  }
}
