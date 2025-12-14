/**
 * useOperationMode Composable
 * 
 * Provides reactive access to the restaurant's operation mode configuration.
 * This composable fetches and caches the mode configuration from the backend.
 */

import { ref, computed, readonly } from 'vue'
import axios from 'axios'
import type { 
  OperationMode, 
  OperationModeConfig, 
  ModeConfigResponse 
} from '@/types/operationMode'

const operationMode = ref<OperationMode | null>(null)
const modeConfig = ref<OperationModeConfig | null>(null)
const planName = ref<string | null>(null)
const isLoading = ref(false)
const isLoaded = ref(false)
const error = ref<string | null>(null)

export function useOperationMode() {
  const loadModeConfig = async () => {
    if (isLoaded.value) {
      return
    }

    isLoading.value = true
    error.value = null

    try {
      const response = await axios.get<ModeConfigResponse>('/api/v1/subscriptions/mode-config')
      
      operationMode.value = response.data.operation_mode as OperationMode
      modeConfig.value = response.data.config
      planName.value = response.data.plan_name
      isLoaded.value = true
      
      console.log('✅ Operation mode loaded:', {
        mode: operationMode.value,
        plan: planName.value,
        showTables: response.data.config.show_tables,
        showKitchen: response.data.config.show_kitchen
      })
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Error loading operation mode'
      console.error('❌ Error loading operation mode:', err)
      // On error, default to full_restaurant mode
      operationMode.value = 'full_restaurant' as OperationMode
      isLoaded.value = true
    } finally {
      isLoading.value = false
    }
  }

  const isFeatureEnabled = (feature: keyof OperationModeConfig): boolean => {
    // If not loaded yet, return true to avoid hiding features during load
    // This prevents flickering but means features show briefly before hiding
    if (!isLoaded.value || !modeConfig.value) {
      return true
    }
    return Boolean(modeConfig.value[feature])
  }

  const showTables = computed(() => isFeatureEnabled('show_tables'))
  const showKitchen = computed(() => isFeatureEnabled('show_kitchen'))
  const showWaiters = computed(() => isFeatureEnabled('show_waiters'))
  const showDelivery = computed(() => isFeatureEnabled('show_delivery'))
  
  const requiresTableForOrder = computed(() => 
    modeConfig.value?.requires_table_for_order ?? true
  )
  
  const allowsPosSales = computed(() => 
    modeConfig.value?.allows_pos_sales ?? false
  )
  
  const useDailyTickets = computed(() => 
    modeConfig.value?.use_daily_tickets ?? false
  )

  const isPosOnlyMode = computed(() => 
    operationMode.value === 'pos_only'
  )

  const isFullRestaurantMode = computed(() => 
    operationMode.value === 'full_restaurant'
  )

  const defaultOrderType = computed(() => 
    modeConfig.value?.default_order_type ?? 'dine_in'
  )

  const allowedStaffTypes = computed(() => 
    modeConfig.value?.allowed_staff_types ?? []
  )

  const clearCache = () => {
    operationMode.value = null
    modeConfig.value = null
    planName.value = null
    isLoaded.value = false
    error.value = null
  }

  const setModeConfigFromUsage = (mode: string, config: OperationModeConfig) => {
    operationMode.value = mode as OperationMode
    modeConfig.value = config
    isLoaded.value = true
    
    console.log('✅ Operation mode loaded from usage:', {
      mode: operationMode.value,
      showTables: config.show_tables,
      showKitchen: config.show_kitchen
    })
  }

  return {
    operationMode: readonly(operationMode),
    modeConfig: readonly(modeConfig),
    planName: readonly(planName),
    isLoading: readonly(isLoading),
    isLoaded: readonly(isLoaded),
    error: readonly(error),
    
    loadModeConfig,
    setModeConfigFromUsage,
    isFeatureEnabled,
    clearCache,
    
    showTables,
    showKitchen,
    showWaiters,
    showDelivery,
    requiresTableForOrder,
    allowsPosSales,
    useDailyTickets,
    isPosOnlyMode,
    isFullRestaurantMode,
    defaultOrderType,
    allowedStaffTypes
  }
}
