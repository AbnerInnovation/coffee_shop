<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        {{ t('app.sysadmin.dashboard.title') }}
      </h1>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        {{ t('app.sysadmin.dashboard.subtitle') }}
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <p class="text-red-800 dark:text-red-200">{{ error }}</p>
    </div>

    <!-- Dashboard Content -->
    <div v-else-if="stats">
      <!-- Quick Stats Grid -->
      <div class="grid grid-cols-2 gap-3 sm:gap-5 lg:grid-cols-4">
        <StatCard
          :icon="BuildingStorefrontIcon"
          :label="t('app.sysadmin.dashboard.total_restaurants')"
          :value="stats.restaurants.total || 0"
          :subtitle="`+${stats.restaurants.new_last_30_days || 0} ${t('app.sysadmin.dashboard.this_month')}`"
          subtitle-class="text-green-600"
        />

        <StatCard
          :icon="CheckCircleIcon"
          icon-class="text-green-400"
          :label="t('app.sysadmin.dashboard.active_restaurants')"
          :value="stats.restaurants.active || 0"
          :subtitle="`/ ${stats.restaurants.total || 0}`"
        />

        <StatCard
          :icon="CurrencyDollarIcon"
          icon-class="text-green-400"
          :label="t('app.sysadmin.dashboard.mrr')"
          :value="`${formatCurrency(stats.revenue.mrr || 0)}`"
        />

        <StatCard
          :icon="ClockIcon"
          icon-class="text-amber-400"
          :label="t('app.sysadmin.dashboard.pending_payments')"
          :value="stats.revenue.pending_payments || 0"
        />
      </div>

      <!-- Secondary Stats -->
      <div class="mt-6 grid grid-cols-2 gap-3 sm:gap-5 sm:grid-cols-3">
        <StatCard
          :icon="SparklesIcon"
          icon-class="text-blue-400"
          :label="t('app.sysadmin.dashboard.trial_restaurants')"
          :value="stats.restaurants.trial || 0"
        />

        <StatCard
          :icon="ExclamationTriangleIcon"
          icon-class="text-red-400"
          :label="t('app.sysadmin.dashboard.suspended_restaurants')"
          :value="stats.restaurants.suspended || 0"
        />

        <StatCard
          :icon="UsersIcon"
          icon-class="text-indigo-400"
          :label="t('app.sysadmin.dashboard.total_users')"
          :value="stats.users.total || 0"
        />
      </div>

      <!-- Activity Stats -->
      <div class="mt-6 grid grid-cols-2 gap-3 sm:gap-5">
        <StatCard
          :icon="ShoppingBagIcon"
          icon-class="text-purple-400"
          :label="t('app.sysadmin.dashboard.orders_30d')"
          :value="stats.activity.orders_30d || 0"
        />

        <StatCard
          :icon="BanknotesIcon"
          icon-class="text-green-400"
          :label="t('app.sysadmin.dashboard.revenue_30d')"
          :value="`${formatCurrency(stats.revenue.revenue_30d || 0)}`"
        />
      </div>

      <!-- Subscription Distribution -->
      <div class="mt-6">
        <SubscriptionDistribution
          :title="t('app.sysadmin.dashboard.subscription_distribution')"
          :distribution="stats.subscription_distribution || {}"
          :total="stats.restaurants.total || 0"
        />
      </div>

      <!-- Quick Actions -->
      <div class="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <QuickActionCard
          :icon="BuildingStorefrontIcon"
          :title="t('app.sysadmin.dashboard.manage_restaurants')"
          :description="t('app.sysadmin.dashboard.view_all_restaurants')"
          to="/sysadmin"
        />

        <QuickActionCard
          :icon="CreditCardIcon"
          icon-class="text-green-600"
          :title="t('app.sysadmin.dashboard.pending_payments')"
          :description="`${stats.revenue.pending_payments || 0} ${t('app.sysadmin.dashboard.payments_due')}`"
          to="/sysadmin/payments"
        />

        <QuickActionCard
          :icon="ArrowPathIcon"
          icon-class="text-gray-600"
          :title="t('app.sysadmin.dashboard.refresh_stats')"
          :description="t('app.sysadmin.dashboard.update_data')"
          is-button
          @click="handleRefresh"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import {
  BuildingStorefrontIcon,
  CheckCircleIcon,
  CurrencyDollarIcon,
  ClockIcon,
  SparklesIcon,
  ExclamationTriangleIcon,
  UsersIcon,
  ShoppingBagIcon,
  BanknotesIcon,
  CreditCardIcon,
  ArrowPathIcon
} from '@heroicons/vue/24/outline';
import { useSysAdminStats } from '@/composables/useSysAdminStats';
import { useToast } from '@/composables/useToast';
import { formatCurrency } from '@/utils/priceHelpers';
import StatCard from '@/components/sysadmin/StatCard.vue';
import SubscriptionDistribution from '@/components/sysadmin/SubscriptionDistribution.vue';
import QuickActionCard from '@/components/sysadmin/QuickActionCard.vue';

const { t } = useI18n();
const { showError } = useToast();

// Composable
const {
  stats,
  loading,
  error,
  loadStats,
  refreshStats
} = useSysAdminStats();

// Handlers
const handleRefresh = async () => {
  await refreshStats();
  if (error.value) {
    showError(error.value);
  }
};

// Initialize
onMounted(() => {
  loadStats();
});
</script>
