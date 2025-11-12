<template>
  <div>
    <!-- Empty State -->
    <div v-if="groupedItems.length === 0" class="text-center py-12 px-4 bg-white dark:bg-gray-900 rounded-lg shadow">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"
        aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">
        {{ t('app.views.kitchen.no_active') }}
      </h3>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        {{ t('app.views.kitchen.no_active_description') }}
      </p>
    </div>

    <!-- Grouped Items List -->
    <div v-else
      class="bg-white dark:bg-gray-900 rounded-lg shadow-md overflow-hidden divide-y divide-gray-200 dark:divide-gray-700">
      <div v-for="item in groupedItems" :key="`${item.menu_item_id}_${item.variant_id}`"
        class="p-4 sm:p-6 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
        <div class="flex-1 min-w-0 space-y-3">
          <!-- Item Header -->
          <div class="flex items-center gap-3">
            <span class="font-bold text-3xl sm:text-4xl text-indigo-600 dark:text-indigo-400">
              {{ item.total_quantity }}x
            </span>
            <h3 class="flex-1 text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
              {{ item.menu_item_name }}
            </h3>
            <p v-if="item.variant_name" class="text-lg sm:text-xl text-gray-600 dark:text-gray-400">
              {{ item.variant_name }}
            </p>
          </div>

          <!-- Category Badge -->
          <span v-if="item.category"
            class="inline-flex items-center rounded-full bg-gray-100 dark:bg-gray-700 px-3 py-1 text-sm font-semibold text-gray-600 dark:text-gray-300 uppercase">
            {{ item.category }}
          </span>

          <!-- Orders Breakdown -->
          <div>
            <p class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              {{ t('app.views.kitchen.grouped.from_orders') }}:
            </p>
            <div class="flex flex-wrap gap-2">
              <span v-for="(orderInfo, idx) in item.orders" :key="idx"
                class="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 rounded-full text-sm font-medium">
                <span class="font-bold">{{ orderInfo.quantity }}x</span>
                <span>{{ t('app.views.kitchen.order', { id: orderInfo.order_number || orderInfo.order_id }) }}</span>
                <span v-if="orderInfo.table_number" class="text-xs">
                  ({{ t('app.views.kitchen.table_short', { number: orderInfo.table_number }) }})
                </span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import type { GroupedKitchenItem } from '@/utils/kitchenHelpers';

interface Props {
  groupedItems: GroupedKitchenItem[];
}

defineProps<Props>();

const { t } = useI18n();
</script>
