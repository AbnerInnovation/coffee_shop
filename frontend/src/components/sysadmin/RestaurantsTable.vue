<template>
  <div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
      <thead class="bg-gray-50 dark:bg-gray-700">
        <tr>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
            {{ t('app.sysadmin.table.restaurant') }}
          </th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
            {{ t('app.sysadmin.table.plan') }}
          </th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
            {{ t('app.sysadmin.table.status') }}
          </th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
            {{ t('app.sysadmin.table.price') }}
          </th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
            {{ t('app.sysadmin.table.renewal') }}
          </th>
          <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
            {{ t('app.sysadmin.table.actions') }}
          </th>
        </tr>
      </thead>
      <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
        <tr v-for="restaurant in restaurants" :key="restaurant.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
          <!-- Restaurant Info -->
          <td class="px-6 py-4">
            <div class="flex items-center">
              <div>
                <div class="text-sm font-medium text-gray-900 dark:text-white">
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
            </div>
          </td>

          <!-- Plan -->
          <td class="px-6 py-4">
            <div v-if="restaurant.plan_name" class="text-sm">
              <div class="font-medium text-gray-900 dark:text-white">
                {{ restaurant.plan_name }}
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400">
                {{ restaurant.plan_tier }}
              </div>
            </div>
            <span v-else class="text-sm text-gray-400 dark:text-gray-500 italic">
              {{ t('app.sysadmin.table.no_plan') }}
            </span>
          </td>

          <!-- Status -->
          <td class="px-6 py-4">
            <span
              v-if="restaurant.subscription_status"
              :class="getStatusClass(restaurant.subscription_status)"
              class="px-2 py-1 text-xs font-semibold rounded-full"
            >
              {{ t(`app.sysadmin.status.${restaurant.subscription_status}`) }}
            </span>
            <span v-else class="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
              {{ t('app.sysadmin.status.none') }}
            </span>
          </td>

          <!-- Price -->
          <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
            <span v-if="restaurant.monthly_price !== null">
              ${{ formatMoney(restaurant.monthly_price) }}/{{ t('app.common.month') }}
            </span>
            <span v-else class="text-gray-400 dark:text-gray-500">-</span>
          </td>

          <!-- Renewal -->
          <td class="px-6 py-4 text-sm">
            <div v-if="restaurant.days_until_renewal !== null">
              <div class="text-gray-900 dark:text-white">
                {{ restaurant.days_until_renewal }} {{ t('app.common.days') }}
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400">
                {{ formatDate(restaurant.current_period_end) }}
              </div>
            </div>
            <span v-else class="text-gray-400 dark:text-gray-500">-</span>
          </td>

          <!-- Actions -->
          <td class="px-6 py-4 text-right text-sm font-medium">
            <button
              @click="$emit('action', restaurant)"
              class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300"
            >
              {{ restaurant.subscription_id ? t('app.sysadmin.actions.manage') : t('app.sysadmin.actions.assign_plan') }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { ArrowTopRightOnSquareIcon } from '@heroicons/vue/24/outline';

interface Props {
  restaurants: any[];
}

defineProps<Props>();
const { t } = useI18n();

defineEmits<{
  'action': [restaurant: any];
}>();

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
