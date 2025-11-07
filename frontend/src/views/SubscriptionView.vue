<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
        {{ t('app.subscription.title') }}
      </h1>
      <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
        {{ t('app.subscription.subtitle') }}
      </p>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700 mb-6">
      <nav class="-mb-px flex space-x-8">
        <button
          @click="activeTab = 'overview'"
          :class="[
            activeTab === 'overview'
              ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
          ]"
        >
          {{ t('app.subscription.tabs.overview') }}
        </button>
        <button
          @click="activeTab = 'alerts'"
          :class="[
            activeTab === 'alerts'
              ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
          ]"
        >
          {{ t('app.subscription.tabs.alerts') }}
          <span v-if="unreadAlertCount > 0" class="ml-2 py-0.5 px-2 rounded-full text-xs bg-red-100 text-red-600 dark:bg-red-900 dark:text-red-300">
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
    <div v-else class="space-y-6">
      <!-- Overview Tab -->
      <div v-if="activeTab === 'overview'" class="space-y-6">
      
      <!-- Expiring Soon Alert (1-3 days) -->
      <div v-if="subscription?.has_subscription && daysUntilExpiration !== null && daysUntilExpiration > 0 && daysUntilExpiration <= 3" 
           class="bg-amber-50 dark:bg-amber-900/20 border-l-4 border-amber-500 p-4 rounded-lg">
        <div class="flex items-start">
          <svg class="h-6 w-6 text-amber-500 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div class="flex-1">
            <h3 class="text-sm font-semibold text-amber-800 dark:text-amber-200">
              ⚠️ Tu suscripción vence en {{ daysUntilExpiration }} {{ daysUntilExpiration === 1 ? 'día' : 'días' }}
            </h3>
            <p class="mt-1 text-sm text-amber-700 dark:text-amber-300">
              Renueva ahora para evitar interrupciones en tu servicio
            </p>
            <button
              @click="showRenewalModal = true"
              class="mt-3 px-4 py-2 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition-colors text-sm font-medium"
            >
              Renovar Ahora
            </button>
          </div>
        </div>
      </div>
      
      <!-- Expired Subscription Alert -->
      <div v-if="subscription?.has_subscription && subscription.subscription?.status === 'expired'" 
           class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4 rounded-lg">
        <div class="flex items-start">
          <svg class="h-6 w-6 text-red-500 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div class="flex-1">
            <h3 class="text-sm font-semibold text-red-800 dark:text-red-200">
              {{ t('app.subscription.account_suspended.subscription_expired') }}
            </h3>
            <p class="mt-1 text-sm text-red-700 dark:text-red-300">
              {{ t('app.subscription.account_suspended.period_ended') }}
            </p>
            <button
              @click="showRenewalModal = true"
              class="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
            >
              {{ t('app.subscription.account_suspended.renew_plan') }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- Current Plan Card -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        <div class="px-6 py-5 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ t('app.subscription.current_plan') }}
          </h2>
        </div>
        
        <div v-if="subscription?.has_subscription" class="p-6">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3">
                <h3 class="text-2xl font-bold text-gray-900 dark:text-white">
                  {{ subscription.subscription?.plan.name }}
                </h3>
                <span
                  :class="getStatusClass(subscription.subscription?.status || 'active')"
                  class="px-3 py-1 text-xs font-semibold rounded-full"
                >
                  {{ t(`app.subscription.status.${subscription.subscription?.status}`) }}
                </span>
              </div>
              
              <div class="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('app.subscription.price') }}</p>
                  <p class="text-lg font-semibold text-gray-900 dark:text-white">
                    ${{ formatMoney(subscription.subscription?.total_price || 0) }}/{{ t(`app.subscription.${subscription.subscription?.billing_cycle}`) }}
                  </p>
                </div>
                <div v-if="subscription?.subscription?.days_until_renewal !== null && subscription?.subscription?.days_until_renewal !== undefined">
                  <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('app.subscription.renewal_date') }}</p>
                  <p class="text-lg font-semibold text-gray-900 dark:text-white">
                    {{ subscription.subscription?.days_until_renewal }} {{ t('app.common.days') }}
                  </p>
                </div>
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('app.subscription.auto_renew') }}</p>
                  <p class="text-lg font-semibold text-gray-900 dark:text-white">
                    {{ subscription.subscription?.auto_renew ? t('app.common.yes') : t('app.common.no') }}
                  </p>
                </div>
              </div>
            </div>
            
            <button
              @click="showUpgradeModal = true"
              class="ml-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              {{ t('app.subscription.upgrade') }}
            </button>
          </div>
        </div>
        
        <div v-else class="p-6 text-center">
          <p class="text-gray-500 dark:text-gray-400 mb-4">
            {{ t('app.subscription.no_subscription') }}
          </p>
          <button
            @click="showUpgradeModal = true"
            class="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            {{ t('app.subscription.choose_plan') }}
          </button>
        </div>
      </div>

      <!-- Usage Statistics -->
      <div v-if="usage" class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        <div class="px-6 py-5 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ t('app.subscription.usage_stats') }}
          </h2>
        </div>
        
        <!-- No Subscription Message -->
        <div v-if="!usage.has_subscription" class="p-8 text-center">
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
        
        <div v-else class="p-6 space-y-6">
          <!-- Users -->
          <div>
            <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              {{ t('app.subscription.users') }}
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <UsageBar
                :label="t('app.subscription.admin_users')"
                :current="usage?.usage?.users?.admin ?? 0"
                :max="usage?.limits?.max_admin_users ?? 0"
                :percentage="usage?.percentages?.admin_users ?? 0"
              />
              <UsageBar
                :label="t('app.subscription.waiter_users')"
                :current="usage?.usage?.users?.waiter ?? 0"
                :max="usage?.limits?.max_waiter_users ?? 0"
                :percentage="usage?.percentages?.waiter_users ?? 0"
              />
              <UsageBar
                :label="t('app.subscription.cashier_users')"
                :current="usage?.usage?.users?.cashier ?? 0"
                :max="usage?.limits?.max_cashier_users ?? 0"
                :percentage="usage?.percentages?.cashier_users ?? 0"
              />
            </div>
          </div>

          <!-- Resources -->
          <div>
            <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              {{ t('app.subscription.resources') }}
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <UsageBar
                :label="t('app.subscription.tables')"
                :current="usage?.usage?.tables ?? 0"
                :max="usage?.limits?.max_tables ?? 0"
                :percentage="usage?.percentages?.tables ?? 0"
              />
              <UsageBar
                :label="t('app.subscription.menu_items')"
                :current="usage?.usage?.menu_items ?? 0"
                :max="usage?.limits?.max_menu_items ?? 0"
                :percentage="usage?.percentages?.menu_items ?? 0"
              />
              <UsageBar
                :label="t('app.subscription.categories')"
                :current="usage?.usage?.categories ?? 0"
                :max="usage?.limits?.max_categories ?? 0"
                :percentage="usage?.percentages?.categories ?? 0"
              />
            </div>
          </div>

          <!-- Features -->
          <div>
            <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              {{ t('app.subscription.features') }}
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              <FeatureBadge
                :label="t('app.subscription.kitchen_module')"
                :enabled="usage?.limits?.has_kitchen_module ?? false"
              />
              <FeatureBadge
                :label="t('app.subscription.ingredients_module')"
                :enabled="usage?.limits?.has_ingredients_module ?? false"
              />
              <FeatureBadge
                :label="t('app.subscription.inventory_module')"
                :enabled="usage?.limits?.has_inventory_module ?? false"
              />
              <FeatureBadge
                :label="t('app.subscription.advanced_reports')"
                :enabled="usage?.limits?.has_advanced_reports ?? false"
              />
              <FeatureBadge
                :label="t('app.subscription.multi_branch')"
                :enabled="usage?.limits?.has_multi_branch ?? false"
              />
            </div>
          </div>
        </div>
      </div>
      </div>

      <!-- Add-ons Tab -->
      <div v-if="activeTab === 'addons'" class="space-y-6">
        <div v-if="!subscription?.has_subscription" class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6 text-center">
          <p class="text-yellow-800 dark:text-yellow-200">
            {{ t('app.subscription.addons_require_plan') }}
          </p>
          <button
            @click="activeTab = 'overview'"
            class="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            {{ t('app.subscription.choose_plan') }}
          </button>
        </div>

        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div
            v-for="addon in addons"
            :key="addon.id"
            class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700"
          >
            <div class="p-6">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {{ addon.name }}
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
                {{ addon.description }}
              </p>
              
              <div class="flex items-baseline mb-4">
                <span class="text-2xl font-bold text-gray-900 dark:text-white">
                  ${{ formatMoney(addon.monthly_price) }}
                </span>
                <span class="ml-1 text-sm text-gray-500 dark:text-gray-400">
                  /{{ t('app.subscription.monthly') }}
                </span>
              </div>

              <div v-if="addon.addon_type !== 'service'" class="text-sm text-gray-600 dark:text-gray-400 mb-4">
                <span v-if="addon.provides_users > 0">
                  +{{ addon.provides_users }} {{ t('app.subscription.users').toLowerCase() }}
                </span>
                <span v-else-if="addon.provides_tables > 0">
                  +{{ addon.provides_tables }} {{ t('app.subscription.tables').toLowerCase() }}
                </span>
                <span v-else-if="addon.provides_menu_items > 0">
                  +{{ addon.provides_menu_items }} {{ t('app.subscription.menu_items').toLowerCase() }}
                </span>
              </div>

              <button
                class="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                @click="handleAddAddon(addon)"
              >
                {{ t('app.subscription.add_addon') }}
              </button>
            </div>
          </div>
        </div>

        <div v-if="addons && addons.length === 0 && subscription?.has_subscription" class="text-center py-12">
          <p class="text-gray-500 dark:text-gray-400">
            {{ t('app.subscription.no_addons_available') }}
          </p>
        </div>
      </div>

      <!-- Alerts Tab -->
      <div v-if="activeTab === 'alerts'">
        <div v-if="subscription?.has_subscription">
          <SubscriptionAlerts 
            :unread-only="false"
            :auto-refresh="true"
            @update:count="handleAlertCountUpdate"
          />
        </div>
        <div v-else class="text-center py-12">
          <p class="text-gray-500 dark:text-gray-400">
            {{ t('app.subscription.no_subscription') }}
          </p>
        </div>
      </div>
    </div>

    <!-- Upgrade Modal -->
    <UpgradePlanModal
      :is-open="showUpgradeModal"
      @close="showUpgradeModal = false"
      @upgraded="handleUpgraded"
    />

    <!-- Renewal Payment Modal -->
    <RenewalPaymentModal
      :is-open="showRenewalModal"
      :available-plans="availablePlans"
      @close="showRenewalModal = false"
      @success="handleRenewalSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { ArrowPathIcon } from '@heroicons/vue/24/outline';
import { subscriptionService, type MySubscription, type SubscriptionUsage, type SubscriptionAddon } from '@/services/subscriptionService';
import UsageBar from '@/components/subscription/UsageBar.vue';
import FeatureBadge from '@/components/subscription/FeatureBadge.vue';
import UpgradePlanModal from '@/components/subscription/UpgradePlanModal.vue';
import RenewalPaymentModal from '@/components/RenewalPaymentModal.vue';
import SubscriptionAlerts from '@/components/SubscriptionAlerts.vue';

const { t } = useI18n();
const route = useRoute();
const router = useRouter();

// State
const loading = ref(true);
const subscription = ref<MySubscription | null>(null);
const usage = ref<SubscriptionUsage | null>(null);
const addons = ref<SubscriptionAddon[]>([]);
const showUpgradeModal = ref(false);
const showRenewalModal = ref(false);
const availablePlans = ref<any[]>([]);
const unreadAlertCount = ref(0);

// Active tab from URL query
const activeTab = computed({
  get: () => (route.query.tab as string) || 'overview',
  set: (value) => {
    router.push({ query: { ...route.query, tab: value } });
  }
});

// Calculate days until expiration
const daysUntilExpiration = computed(() => {
  if (!subscription.value?.subscription?.current_period_end) return null;
  
  const endDate = new Date(subscription.value.subscription.current_period_end);
  const now = new Date();
  const diffTime = endDate.getTime() - now.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  
  return diffDays;
});

// Methods
const loadData = async () => {
  loading.value = true;
  try {
    [subscription.value, usage.value, addons.value, availablePlans.value] = await Promise.all([
      subscriptionService.getMySubscription(),
      subscriptionService.getUsage(),
      subscriptionService.getAddons().catch(() => []), // Addons are optional
      subscriptionService.getPlans().catch(() => []) // Load available plans
    ]);
  } catch (error) {
    console.error('Error loading subscription data:', error);
  } finally {
    loading.value = false;
  }
};

const handleRenewalSuccess = async () => {
  // Reload subscription data after successful renewal
  await loadData();
};

const handleAlertCountUpdate = (count: number) => {
  // Handle alert count update if needed
  console.log('Unread alerts:', count);
};

const formatMoney = (amount: number) => {
  return amount.toLocaleString('es-MX', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};

const getStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    trial: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    active: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    past_due: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    cancelled: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    expired: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
  };
  return classes[status] || classes.active;
};

const handleUpgraded = () => {
  // Reload data after upgrade
  loadData();
};

const handleAddAddon = (addon: SubscriptionAddon) => {
  // TODO: Implement addon purchase flow
  console.log('Add addon:', addon);
  alert(`Funcionalidad de compra de add-on "${addon.name}" próximamente disponible`);
};

// Lifecycle
onMounted(() => {
  loadData();
  
  // Check if we should open the upgrade modal automatically
  if (route.query.openModal === 'true') {
    showUpgradeModal.value = true;
    // Clean up the query parameter
    router.replace({ query: { ...route.query, openModal: undefined } });
  }
});
</script>
