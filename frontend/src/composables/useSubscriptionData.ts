import { ref, computed, type Ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { subscriptionService, type MySubscription, type SubscriptionUsage, type SubscriptionAddon } from '@/services/subscriptionService'

/**
 * Composable para gestión de datos de suscripción
 */
export function useSubscriptionData() {
  const { t } = useI18n()

  // State
  const loading = ref(true)
  const subscription = ref<MySubscription | null>(null)
  const usage = ref<SubscriptionUsage | null>(null)
  const addons = ref<SubscriptionAddon[]>([])
  const availablePlans = ref<any[]>([])

  /**
   * Calcula días hasta la expiración
   */
  const daysUntilExpiration = computed(() => {
    if (!subscription.value?.subscription?.current_period_end) return null

    const endDate = new Date(subscription.value.subscription.current_period_end)
    const now = new Date()
    const diffTime = endDate.getTime() - now.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

    return diffDays
  })

  /**
   * Carga todos los datos de suscripción
   */
  async function loadData() {
    loading.value = true
    try {
      [subscription.value, usage.value, addons.value, availablePlans.value] = await Promise.all([
        subscriptionService.getMySubscription(),
        subscriptionService.getUsage(),
        subscriptionService.getAddons().catch(() => []),
        subscriptionService.getPlans().catch(() => [])
      ])
    } catch (error) {
      console.error('Error loading subscription data:', error)
    } finally {
      loading.value = false
    }
  }

  /**
   * Formatea montos monetarios
   */
  function formatMoney(amount: number): string {
    return amount.toLocaleString('es-MX', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })
  }

  /**
   * Obtiene clase CSS según el estado de la suscripción
   */
  function getStatusClass(status: string): string {
    const classes: Record<string, string> = {
      trial: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      active: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      past_due: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      cancelled: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      expired: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
    }
    return classes[status] || classes.active
  }

  return {
    loading,
    subscription,
    usage,
    addons,
    availablePlans,
    daysUntilExpiration,
    loadData,
    formatMoney,
    getStatusClass
  }
}
