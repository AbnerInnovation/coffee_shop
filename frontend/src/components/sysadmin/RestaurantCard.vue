<template>
  <div class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700 border-b border-gray-200 dark:border-gray-700">
    <!-- Restaurant Name & Subdomain -->
    <div class="mb-3">
      <div class="text-base font-semibold text-gray-900 dark:text-white">
        {{ restaurant.name }}
      </div>
      <div class="text-sm text-gray-500 dark:text-gray-400">
        {{ restaurant.subdomain }}
      </div>
      <a 
        :href="getRestaurantUrl(restaurant.subdomain)" 
        target="_blank"
        class="inline-flex items-center gap-1 text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 mt-1"
      >
        <ArrowTopRightOnSquareIcon class="h-3 w-3" />
        {{ t('app.sysadmin.actions.open_system') }}
      </a>
    </div>

    <!-- Status Badge -->
    <div class="mb-3">
      <span
        v-if="restaurant.subscription_status"
        :class="getStatusClass(restaurant.subscription_status)"
        class="inline-flex px-2.5 py-1 text-xs font-semibold rounded-full"
      >
        {{ t(`app.sysadmin.status.${restaurant.subscription_status}`) }}
      </span>
      <span v-else class="inline-flex px-2.5 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
        {{ t('app.sysadmin.status.none') }}
      </span>
    </div>

    <!-- Plan & Price -->
    <div class="grid grid-cols-2 gap-3 mb-3 text-sm">
      <div>
        <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">{{ t('app.sysadmin.table.plan') }}</div>
        <div v-if="restaurant.plan_name">
          <div class="font-medium text-gray-900 dark:text-white">{{ restaurant.plan_name }}</div>
          <div class="text-xs text-gray-500 dark:text-gray-400">{{ restaurant.plan_tier }}</div>
        </div>
        <div v-else class="text-gray-400 dark:text-gray-500 italic">{{ t('app.sysadmin.table.no_plan') }}</div>
      </div>
      <div>
        <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">{{ t('app.sysadmin.table.price') }}</div>
        <div v-if="restaurant.monthly_price !== null" class="font-medium text-gray-900 dark:text-white">
          ${{ formatMoney(restaurant.monthly_price) }}/{{ t('app.common.month') }}
        </div>
        <div v-else class="text-gray-400 dark:text-gray-500">-</div>
      </div>
    </div>

    <!-- Renewal -->
    <div v-if="restaurant.days_until_renewal !== null" class="mb-3 text-sm">
      <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">{{ t('app.sysadmin.table.renewal') }}</div>
      <div class="text-gray-900 dark:text-white">
        {{ restaurant.days_until_renewal }} {{ t('app.common.days') }}
      </div>
      <div class="text-xs text-gray-500 dark:text-gray-400">
        {{ formatDate(restaurant.current_period_end) }}
      </div>
    </div>

    <!-- Action Button -->
    <button
      @click="handleAction"
      class="w-full px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
    >
      {{ restaurant.subscription_id ? t('app.sysadmin.actions.manage') : t('app.sysadmin.actions.assign_plan') }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { ArrowTopRightOnSquareIcon } from '@heroicons/vue/24/outline';

interface Props {
  restaurant: any;
}

const props = defineProps<Props>();
const { t } = useI18n();

const emit = defineEmits<{
  'action': [restaurant: any];
}>();

const handleAction = () => {
  emit('action', props.restaurant);
};

const getRestaurantUrl = (subdomain: string) => {
  const hostname = window.location.hostname;
  if (hostname === 'localhost' || hostname.startsWith('127.')) {
    return `http://${subdomain}.shopacoffee.local:3000`;
  }
  return `https://${subdomain}.shopacoffee.com`;
};

const getStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    'trial': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'active': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'past_due': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    'cancelled': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    'expired': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
  };
  return classes[status] || 'bg-gray-100 text-gray-800';
};

const formatMoney = (amount: number) => {
  return amount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};

const formatDate = (date: string) => {
  if (!date) return '-';
  return new Date(date).toLocaleDateString();
};
</script>
