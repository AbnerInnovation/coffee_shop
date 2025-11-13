<template>
  <div class="grid grid-cols-2 gap-3 sm:gap-5 md:grid-cols-2 lg:grid-cols-4 mb-8">
    <!-- Total Restaurants -->
    <StatCard
      :icon="BuildingStorefrontIcon"
      icon-class="text-indigo-500"
      :label="t('app.sysadmin.stats.total_restaurants')"
      :value="stats.total_restaurants"
      :subtitle="`${stats.restaurants_with_subscription} ${t('app.sysadmin.stats.with_subscription')}`"
      subtitle-class="text-green-600 dark:text-green-400"
    />

    <!-- Active Subscriptions -->
    <StatCard
      :icon="CheckCircleIcon"
      icon-class="text-green-500"
      :label="t('app.sysadmin.stats.active_subscriptions')"
      :value="stats.active_subscriptions"
      :subtitle="`${stats.trial_subscriptions} ${t('app.sysadmin.stats.in_trial')}`"
      subtitle-class="text-blue-600 dark:text-blue-400"
    />

    <!-- Monthly Revenue -->
    <StatCard
      :icon="CurrencyDollarIcon"
      icon-class="text-yellow-500"
      :label="t('app.sysadmin.stats.monthly_revenue')"
      :value="`$${formatMoney(stats.total_monthly_revenue)}`"
      :subtitle="`${t('app.sysadmin.stats.annual')}: $${formatMoney(stats.total_annual_revenue)}`"
      subtitle-class="text-gray-600 dark:text-gray-400"
    />
    
    <!-- Without Subscription -->
    <StatCard
      :icon="ExclamationTriangleIcon"
      icon-class="text-red-500"
      :label="t('app.sysadmin.stats.without_subscription')"
      :value="stats.restaurants_without_subscription"
      :subtitle="`${stats.cancelled_subscriptions} ${t('app.sysadmin.stats.cancelled')}`"
      subtitle-class="text-red-600 dark:text-red-400"
    />
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import {
  BuildingStorefrontIcon,
  CheckCircleIcon,
  CurrencyDollarIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline';
import StatCard from './StatCard.vue';

interface Props {
  stats: any;
}

defineProps<Props>();
const { t } = useI18n();

const formatMoney = (amount: number) => {
  return amount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};
</script>
