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
import { ArrowPathIcon } from '@heroicons/vue/24/outline'
import { useSubscriptionData } from '@/composables/useSubscriptionData'
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
  { value: 'alerts', label: t('app.subscription.tabs.alerts') }
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

// Lifecycle
onMounted(() => {
  loadData()

  if (route.query.openModal === 'true') {
    showUpgradeModal.value = true
    router.replace({ query: { ...route.query, openModal: undefined } })
  }
})
</script>
