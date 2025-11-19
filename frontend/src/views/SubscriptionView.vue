<template>
  <div class="max-w-7xl mx-auto px-3 sm:px-4 lg:px-6 py-3 sm:py-6">
    <!-- Header -->
    <div class="mb-4 sm:mb-6">
      <h1 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
        {{ t('app.subscription.title') }}
      </h1>
      <p class="mt-1 text-xs sm:text-sm text-gray-600 dark:text-gray-400">
        {{ t('app.subscription.subtitle') }}
      </p>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700 mb-4 sm:mb-6">
      <nav class="-mb-px flex space-x-4 sm:space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.value"
          @click="activeTab = tab.value"
          :class="[
            activeTab === tab.value
              ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
            'whitespace-nowrap py-3 px-1 border-b-2 font-medium text-xs sm:text-sm'
          ]"
        >
          {{ tab.label }}
          <span
            v-if="tab.value === 'alerts' && unreadAlertCount > 0"
            class="ml-2 py-0.5 px-2 rounded-full text-xs bg-red-100 text-red-600 dark:bg-red-900 dark:text-red-300"
          >
            {{ unreadAlertCount }}
          </span>
        </button>
      </nav>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <ArrowPathIcon class="h-12 w-12 animate-spin text-indigo-600" />
    </div>

    <!-- Content -->
    <div v-else class="space-y-4 sm:space-y-6">
      <!-- Overview Tab -->
      <div v-if="activeTab === 'overview'" class="space-y-4 sm:space-y-6">
        <!-- Expiring Soon Alert -->
        <AlertBanner
          v-if="subscription?.has_subscription && daysUntilExpiration !== null && daysUntilExpiration > 0 && daysUntilExpiration <= 3"
          variant="warning"
          :title="`⚠️ Tu suscripción vence en ${daysUntilExpiration} ${daysUntilExpiration === 1 ? 'día' : 'días'}`"
          message="Renueva ahora para evitar interrupciones en tu servicio"
          button-text="Renovar Ahora"
          @action="showRenewalModal = true"
        />

        <!-- Expired Subscription Alert -->
        <AlertBanner
          v-if="subscription?.has_subscription && subscription.subscription?.status === 'expired'"
          variant="error"
          :title="t('app.subscription.account_suspended.subscription_expired')"
          :message="t('app.subscription.account_suspended.period_ended')"
          :button-text="t('app.subscription.account_suspended.renew_plan')"
          @action="showRenewalModal = true"
        />

        <!-- Current Plan Card -->
        <PlanCard
          :title="t('app.subscription.current_plan')"
          :has-subscription="subscription?.has_subscription || false"
          :plan-name="subscription?.subscription?.plan.name"
          :status-class="getStatusClass(subscription?.subscription?.status || 'active')"
          :status-label="t(`app.subscription.status.${subscription?.subscription?.status}`)"
          :price-label="t('app.subscription.price')"
          :formatted-price="`$${formatMoney(subscription?.subscription?.total_price || 0)}/${t(`app.subscription.${subscription?.subscription?.billing_cycle}`)}`"
          :renewal-label="t('app.subscription.renewal_date')"
          :days-until-renewal="subscription?.subscription?.days_until_renewal"
          :days-label="t('app.common.days')"
          :no-subscription-message="t('app.subscription.no_subscription')"
          :choose-plan-label="t('app.subscription.choose_plan')"
          @choose-plan="showUpgradeModal = true"
        />

        <!-- Usage Statistics -->
        <div v-if="usage" class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
          <div class="px-3 py-2 sm:px-4 sm:py-3 border-b border-gray-200 dark:border-gray-700">
            <h2 class="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">
              {{ t('app.subscription.usage_stats') }}
            </h2>
          </div>

          <!-- No Subscription Message -->
          <div v-if="!usage.has_subscription" class="p-6 text-center">
            <div class="mx-auto w-16 h-16 bg-yellow-100 dark:bg-yellow-900/20 rounded-full flex items-center justify-center mb-4">
              <svg class="w-8 h-8 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {{ t('app.subscription.no_active_plan') }}
            </h3>
            <p class="text-gray-600 dark:text-gray-400 mb-6">
              {{ t('app.subscription.no_subscription_message') }}
            </p>
            <button
              @click="showUpgradeModal = true"
              class="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              {{ t('app.subscription.choose_plan') }}
            </button>
          </div>

          <div v-else class="p-3 sm:p-4 space-y-3 sm:space-y-4">
            <!-- Users -->
            <div>
              <h3 class="text-sm sm:text-base font-bold text-gray-900 dark:text-gray-100 mb-2">
                {{ t('app.subscription.users') }}
              </h3>
              <div class="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-3">
                <UsageBar
                  v-for="userType in userTypes"
                  :key="userType.key"
                  :label="t(userType.label)"
                  :current="usage?.usage?.users?.[userType.key] ?? 0"
                  :max="usage?.limits?.[userType.maxKey] ?? 0"
                  :percentage="usage?.percentages?.[userType.percentageKey] ?? 0"
                />
              </div>
            </div>

            <!-- Resources -->
            <div>
              <h3 class="text-sm sm:text-base font-bold text-gray-900 dark:text-gray-100 mb-2">
                {{ t('app.subscription.resources') }}
              </h3>
              <div class="grid grid-cols-2 md:grid-cols-3 gap-2 sm:gap-3">
                <UsageBar
                  v-for="resource in resources"
                  :key="resource.key"
                  :label="t(resource.label)"
                  :current="usage?.usage?.[resource.key] ?? 0"
                  :max="usage?.limits?.[resource.maxKey] ?? 0"
                  :percentage="usage?.percentages?.[resource.key] ?? 0"
                />
              </div>
            </div>

            <!-- Features -->
            <div>
              <h3 class="text-sm sm:text-base font-bold text-gray-900 dark:text-gray-100 mb-2">
                {{ t('app.subscription.features') }}
              </h3>
              <div class="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-3 gap-2 sm:gap-3">
                <FeatureBadge
                  v-for="feature in features"
                  :key="feature.key"
                  :label="t(feature.label)"
                  :enabled="usage?.features?.[feature.key] ?? false"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Alerts Tab -->
      <div v-if="activeTab === 'alerts'">
        <div v-if="subscription?.has_subscription">
          <SubscriptionAlerts :unread-only="false" :auto-refresh="true" @update:count="handleAlertCountUpdate" />
        </div>
        <div v-else class="text-center py-12">
          <p class="text-gray-500 dark:text-gray-400">
            {{ t('app.subscription.no_subscription') }}
          </p>
        </div>
      </div>

      <!-- Settings Tab -->
      <div v-if="activeTab === 'settings'">
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
          <div class="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
            <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
              {{ t('app.subscription.settings.title') }}
            </h2>
            <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {{ t('app.subscription.settings.subtitle') }}
            </p>
          </div>

          <div class="p-4 sm:p-6 space-y-4 sm:space-y-6">
            <!-- Kitchen Print Settings -->
            <div class="bg-gray-50 dark:bg-gray-900/50 rounded-lg sm:rounded-xl p-4 sm:p-5 border border-gray-200 dark:border-gray-700">
              <div class="flex items-center justify-between gap-3">
                <div class="flex items-center gap-2 sm:gap-3 flex-1 min-w-0">
                  <div class="p-1.5 sm:p-2 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg flex-shrink-0">
                    <svg class="w-5 h-5 sm:w-6 sm:h-6 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                    </svg>
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="text-sm sm:text-base font-semibold text-gray-900 dark:text-white">
                      {{ t('app.subscription.settings.kitchen_print.title') }}
                    </h3>
                    <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                      {{ t('app.subscription.settings.kitchen_print.description') }}
                    </p>
                  </div>
                </div>
                <button
                  @click="toggleKitchenPrint"
                  :disabled="savingSettings"
                  :class="[
                    'relative inline-flex h-6 w-11 sm:h-7 sm:w-12 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2 dark:focus:ring-offset-gray-800',
                    kitchenPrintEnabled
                      ? 'bg-indigo-600'
                      : 'bg-gray-300 dark:bg-gray-600',
                    savingSettings ? 'opacity-50 cursor-not-allowed' : ''
                  ]"
                >
                  <span
                    :class="[
                      'pointer-events-none inline-block h-5 w-5 sm:h-6 sm:w-6 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out',
                      kitchenPrintEnabled ? 'translate-x-5' : 'translate-x-0'
                    ]"
                  />
                </button>
              </div>
            </div>

            <!-- Paper Width Settings -->
            <transition
              enter-active-class="transition ease-out duration-200"
              enter-from-class="opacity-0 -translate-y-2"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition ease-in duration-150"
              leave-from-class="opacity-100 translate-y-0"
              leave-to-class="opacity-0 -translate-y-2"
            >
              <div v-if="kitchenPrintEnabled" class="bg-gray-50 dark:bg-gray-900/50 rounded-lg sm:rounded-xl p-4 sm:p-5 border border-gray-200 dark:border-gray-700">
                <div class="flex items-center gap-2 sm:gap-3 mb-3 sm:mb-4">
                  <div class="p-1.5 sm:p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex-shrink-0">
                    <svg class="w-5 h-5 sm:w-6 sm:h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="text-sm sm:text-base font-semibold text-gray-900 dark:text-white">
                      {{ t('app.subscription.settings.paper_width.title') }}
                    </h3>
                    <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                      {{ t('app.subscription.settings.paper_width.description') }}
                    </p>
                  </div>
                </div>
                <div class="grid grid-cols-2 gap-2 sm:gap-3">
                  <button
                    @click="setPaperWidth(58)"
                    :disabled="savingSettings"
                    :class="[
                      'group relative px-3 py-3 sm:px-4 sm:py-4 rounded-lg sm:rounded-xl border-2 transition-all duration-200 transform active:scale-95 sm:hover:scale-105',
                      paperWidth === 58
                        ? 'border-indigo-500 bg-gradient-to-br from-indigo-50 to-indigo-100 dark:from-indigo-900/30 dark:to-indigo-800/20 shadow-md'
                        : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 active:border-indigo-400 sm:hover:border-indigo-400 dark:hover:border-indigo-500',
                      savingSettings ? 'opacity-50 cursor-not-allowed transform-none' : 'cursor-pointer'
                    ]"
                  >
                    <div class="text-center">
                      <div :class="[
                        'text-xl sm:text-2xl font-bold',
                        paperWidth === 58 ? 'text-indigo-700 dark:text-indigo-300' : 'text-gray-900 dark:text-white'
                      ]">
                        58mm
                      </div>
                      <div :class="[
                        'text-[9px] sm:text-[10px] font-medium uppercase tracking-wide mt-0.5',
                        paperWidth === 58 ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-500 dark:text-gray-400'
                      ]">
                        {{ t('app.subscription.settings.paper_width.compact') }}
                      </div>
                    </div>
                    <div v-if="paperWidth === 58" class="absolute top-1 right-1 sm:top-1.5 sm:right-1.5">
                      <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-indigo-600 dark:text-indigo-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                      </svg>
                    </div>
                  </button>
                  <button
                    @click="setPaperWidth(80)"
                    :disabled="savingSettings"
                    :class="[
                      'group relative px-3 py-3 sm:px-4 sm:py-4 rounded-lg sm:rounded-xl border-2 transition-all duration-200 transform active:scale-95 sm:hover:scale-105',
                      paperWidth === 80
                        ? 'border-indigo-500 bg-gradient-to-br from-indigo-50 to-indigo-100 dark:from-indigo-900/30 dark:to-indigo-800/20 shadow-md'
                        : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 active:border-indigo-400 sm:hover:border-indigo-400 dark:hover:border-indigo-500',
                      savingSettings ? 'opacity-50 cursor-not-allowed transform-none' : 'cursor-pointer'
                    ]"
                  >
                    <div class="text-center">
                      <div :class="[
                        'text-xl sm:text-2xl font-bold',
                        paperWidth === 80 ? 'text-indigo-700 dark:text-indigo-300' : 'text-gray-900 dark:text-white'
                      ]">
                        80mm
                      </div>
                      <div :class="[
                        'text-[9px] sm:text-[10px] font-medium uppercase tracking-wide mt-0.5',
                        paperWidth === 80 ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-500 dark:text-gray-400'
                      ]">
                        {{ t('app.subscription.settings.paper_width.standard') }}
                      </div>
                    </div>
                    <div v-if="paperWidth === 80" class="absolute top-1 right-1 sm:top-1.5 sm:right-1.5">
                      <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-indigo-600 dark:text-indigo-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                      </svg>
                    </div>
                  </button>
                </div>
              </div>
            </transition>

          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <UpgradePlanModal :is-open="showUpgradeModal" @close="showUpgradeModal = false" @upgraded="handleUpgraded" />
    <RenewalPaymentModal
      :is-open="showRenewalModal"
      :available-plans="availablePlans"
      @close="showRenewalModal = false"
      @success="handleRenewalSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { ArrowPathIcon } from '@heroicons/vue/24/outline'
import { useSubscriptionData } from '@/composables/useSubscriptionData'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import UsageBar from '@/components/subscription/UsageBar.vue'
import FeatureBadge from '@/components/subscription/FeatureBadge.vue'
import AlertBanner from '@/components/subscription/AlertBanner.vue'
import PlanCard from '@/components/subscription/PlanCard.vue'
import UpgradePlanModal from '@/components/subscription/UpgradePlanModal.vue'
import RenewalPaymentModal from '@/components/RenewalPaymentModal.vue'
import SubscriptionAlerts from '@/components/SubscriptionAlerts.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

// Data management
const {
  loading,
  subscription,
  usage,
  availablePlans,
  daysUntilExpiration,
  loadData,
  formatMoney,
  getStatusClass
} = useSubscriptionData()

// State
const showUpgradeModal = ref(false)
const showRenewalModal = ref(false)
const unreadAlertCount = ref(0)
const kitchenPrintEnabled = ref(true)
const paperWidth = ref(80)
const savingSettings = ref(false)

// Active tab from URL query
const activeTab = computed({
  get: () => (route.query.tab as string) || 'overview',
  set: (value) => {
    router.push({ query: { ...route.query, tab: value } })
  }
})

// Tabs configuration
const tabs = computed(() => [
  { value: 'overview', label: t('app.subscription.tabs.overview') },
  { value: 'alerts', label: t('app.subscription.tabs.alerts') },
  { value: 'settings', label: t('app.subscription.tabs.settings') }
])

// User types configuration
const userTypes = [
  { key: 'admin', label: 'app.subscription.admin_users', maxKey: 'max_admin_users', percentageKey: 'admin_users' },
  { key: 'waiter', label: 'app.subscription.waiter_users', maxKey: 'max_waiter_users', percentageKey: 'waiter_users' },
  { key: 'cashier', label: 'app.subscription.cashier_users', maxKey: 'max_cashier_users', percentageKey: 'cashier_users' },
  { key: 'kitchen', label: 'app.subscription.kitchen_users', maxKey: 'max_kitchen_users', percentageKey: 'kitchen_users' }
]

// Resources configuration
const resources = [
  { key: 'tables', label: 'app.subscription.tables', maxKey: 'max_tables' },
  { key: 'menu_items', label: 'app.subscription.menu_items', maxKey: 'max_menu_items' },
  { key: 'categories', label: 'app.subscription.categories', maxKey: 'max_categories' }
]

// Features configuration
const features = [
  { key: 'has_kitchen_module', label: 'app.subscription.kitchen_module' },
  { key: 'has_ingredients_module', label: 'app.subscription.ingredients_module' },
  { key: 'has_inventory_module', label: 'app.subscription.inventory_module' },
  { key: 'has_advanced_reports', label: 'app.subscription.advanced_reports' },
  { key: 'has_multi_branch', label: 'app.subscription.multi_branch' }
]

// Methods
const handleRenewalSuccess = async () => {
  await loadData()
}

const handleAlertCountUpdate = (count: number) => {
  unreadAlertCount.value = count
}

const handleUpgraded = () => {
  loadData()
}

const toggleKitchenPrint = async () => {
  try {
    savingSettings.value = true
    
    const newValue = !kitchenPrintEnabled.value
    
    // Update backend
    await api.patch('/restaurants/current', {
      kitchen_print_enabled: newValue
    })
    
    // Update local state
    kitchenPrintEnabled.value = newValue
    
    // Update auth store
    if (authStore.restaurant) {
      authStore.restaurant.kitchen_print_enabled = newValue
    }
    
    // Show success toast
    toast.success(
      newValue 
        ? t('app.subscription.settings.kitchen_print.enabled')
        : t('app.subscription.settings.kitchen_print.disabled')
    )
  } catch (error) {
    console.error('Error updating kitchen print setting:', error)
    toast.error(t('app.subscription.settings.error'))
  } finally {
    savingSettings.value = false
  }
}

const setPaperWidth = async (width: number) => {
  try {
    savingSettings.value = true
    
    // Update backend
    await api.patch('/restaurants/current', {
      kitchen_print_paper_width: width
    })
    
    // Update local state
    paperWidth.value = width
    
    // Update auth store
    if (authStore.restaurant) {
      authStore.restaurant.kitchen_print_paper_width = width
    }
    
    // Show success toast
    toast.success(
      t('app.subscription.settings.paper_width.updated', { width: `${width}mm` })
    )
  } catch (error) {
    console.error('Error updating paper width setting:', error)
    toast.error(t('app.subscription.settings.error'))
  } finally {
    savingSettings.value = false
  }
}

const loadRestaurantSettings = async () => {
  await authStore.loadRestaurant()
  kitchenPrintEnabled.value = authStore.restaurant?.kitchen_print_enabled ?? true
  paperWidth.value = authStore.restaurant?.kitchen_print_paper_width ?? 80
}

// Lifecycle
onMounted(() => {
  loadData()
  loadRestaurantSettings()

  if (route.query.openModal === 'true') {
    showUpgradeModal.value = true
    router.replace({ query: { ...route.query, openModal: undefined } })
  }
})
</script>
