import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import type { PaymentMethodsConfig } from './useRestaurantSettings'

export type PaymentMethod = 'cash' | 'card' | 'digital' | 'other'

export interface PaymentMethodOption {
  value: PaymentMethod
  label: string
  enabled: boolean
}

/**
 * Composable to get available payment methods based on restaurant configuration
 */
export function usePaymentMethods() {
  const authStore = useAuthStore()

  /**
   * Get payment methods configuration from restaurant settings
   */
  const paymentMethodsConfig = computed<PaymentMethodsConfig>(() => {
    return authStore.restaurant?.payment_methods_config || {
      cash: true,
      card: false,
      digital: true,
      other: false
    }
  })

  /**
   * Get all payment method options with their enabled status
   */
  const allPaymentMethods = computed<PaymentMethodOption[]>(() => {
    const config = paymentMethodsConfig.value
    return [
      { value: 'cash', label: 'Efectivo', enabled: config.cash },
      { value: 'card', label: 'Tarjeta', enabled: config.card },
      { value: 'digital', label: 'Digital', enabled: config.digital },
      { value: 'other', label: 'Otro', enabled: config.other }
    ]
  })

  /**
   * Get only enabled payment methods
   */
  const availablePaymentMethods = computed<PaymentMethodOption[]>(() => {
    return allPaymentMethods.value.filter(method => method.enabled)
  })

  /**
   * Check if a specific payment method is enabled
   */
  const isPaymentMethodEnabled = (method: PaymentMethod): boolean => {
    return paymentMethodsConfig.value[method] ?? false
  }

  /**
   * Get payment method label by value
   */
  const getPaymentMethodLabel = (method: PaymentMethod): string => {
    const methodOption = allPaymentMethods.value.find(m => m.value === method)
    return methodOption?.label || method
  }

  return {
    paymentMethodsConfig,
    allPaymentMethods,
    availablePaymentMethods,
    isPaymentMethodEnabled,
    getPaymentMethodLabel
  }
}
