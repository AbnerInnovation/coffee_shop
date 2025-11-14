<template>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <!-- Cash Register Summary -->
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
        <BanknotesIcon class="h-5 w-5 mr-2 text-green-600" />
        {{ t('app.reports.cash_register') }}
      </h3>
      <dl class="space-y-3">
        <div class="flex justify-between">
          <dt class="text-sm text-gray-500 dark:text-gray-400">
            {{ t('app.reports.open_sessions') }}
          </dt>
          <dd class="text-sm font-medium text-gray-900 dark:text-white">
            {{ cashRegister.open_sessions }}
          </dd>
        </div>
        <div class="flex justify-between">
          <dt class="text-sm text-gray-500 dark:text-gray-400">
            {{ t('app.reports.closed_sessions') }}
          </dt>
          <dd class="text-sm font-medium text-gray-900 dark:text-white">
            {{ cashRegister.closed_sessions }}
          </dd>
        </div>
        <div class="flex justify-between pt-3 border-t border-gray-200 dark:border-gray-700">
          <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
            {{ t('app.reports.total_cash_collected') }}
          </dt>
          <dd class="text-sm font-semibold text-green-600 dark:text-green-400">
            ${{ formatNumber(cashRegister.total_cash_collected) }}
          </dd>
        </div>
      </dl>
    </div>

    <!-- Inventory Alerts -->
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center">
        <ExclamationTriangleIcon class="h-5 w-5 mr-2 text-amber-600" />
        {{ t('app.reports.inventory_alerts') }}
      </h3>
      <div v-if="inventoryAlerts.unavailable_count > 0">
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
          {{ t('app.reports.unavailable_products_count', { count: inventoryAlerts.unavailable_count }) }}
        </p>
        <ul class="space-y-2 max-h-40 overflow-y-auto">
          <li
            v-for="product in inventoryAlerts.unavailable_products"
            :key="product.id"
            class="text-sm text-gray-700 dark:text-gray-300 flex items-center"
          >
            <span class="h-2 w-2 bg-red-500 rounded-full mr-2"></span>
            {{ product.name }}
          </li>
        </ul>
      </div>
      <div v-else class="text-center py-8">
        <CheckCircleIcon class="h-12 w-12 text-green-500 mx-auto mb-2" />
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {{ t('app.reports.all_products_available') }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import {
  BanknotesIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline';

/**
 * Additional information section for reports
 * Shows cash register summary and inventory alerts
 */

const { t } = useI18n();

defineProps<{
  cashRegister: {
    open_sessions: number;
    closed_sessions: number;
    total_cash_collected: number;
  };
  inventoryAlerts: {
    unavailable_count: number;
    unavailable_products: Array<{ id: number; name: string }>;
  };
  formatNumber: (value: number) => string;
}>();
</script>
