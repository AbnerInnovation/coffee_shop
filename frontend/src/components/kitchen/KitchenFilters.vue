<template>
  <div class="space-y-4">
    <!-- Order Type Filter Dropdown -->
    <div class="flex items-center gap-2">
      <label for="order-type-filter" class="text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">
        {{ t('app.views.kitchen.order_type_filter.label') }}:
      </label>
      <select id="order-type-filter" :value="selectedOrderType" @change="$emit('update:selectedOrderType', ($event.target as HTMLSelectElement).value as OrderTypeFilter)"
        class="block w-full sm:w-48 rounded-md border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm py-2 px-3">
        <option v-for="typeTab in orderTypeTabs" :key="typeTab.value" :value="typeTab.value">
          {{ typeTab.label }} ({{ typeTab.count }})
        </option>
      </select>
    </div>

    <!-- Status Tabs -->
    <div class="bg-white dark:bg-gray-900 rounded-lg shadow">
      <div class="border-b border-gray-200 dark:border-gray-700 overflow-x-auto">
        <nav class="-mb-px flex space-x-2 sm:space-x-6 px-2 sm:px-3 min-w-max" aria-label="Tabs">
          <button v-for="tab in statusTabs" :key="tab.value" @click="$emit('update:selectedStatus', tab.value)" :class="[
            selectedStatus === tab.value
              ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
            'whitespace-nowrap py-2 sm:py-3 px-2 border-b-2 font-semibold text-xs sm:text-base flex-shrink-0'
          ]">
            {{ tab.label }}
            <span v-if="tab.count > 0" :class="[
              selectedStatus === tab.value
                ? 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400'
                : 'bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-300',
              'ml-1 py-0.5 px-1.5 sm:px-2 rounded-full text-xs font-medium'
            ]">
              {{ tab.count }}
            </span>
          </button>
        </nav>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import type { KitchenStatusFilter, OrderTypeFilter } from '@/composables/useKitchenFilters';

interface StatusTab {
  value: KitchenStatusFilter;
  label: string;
  count: number;
}

interface OrderTypeTab {
  value: OrderTypeFilter;
  label: string;
  count: number;
}

interface Props {
  selectedStatus: KitchenStatusFilter;
  selectedOrderType: OrderTypeFilter;
  statusTabs: StatusTab[];
  orderTypeTabs: OrderTypeTab[];
}

defineProps<Props>();

defineEmits<{
  'update:selectedStatus': [value: KitchenStatusFilter];
  'update:selectedOrderType': [value: OrderTypeFilter];
}>();

const { t } = useI18n();
</script>

<style scoped>
/* Smooth scrolling for tabs on mobile */
.overflow-x-auto {
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  /* Firefox */
  -ms-overflow-style: none;
  /* IE and Edge */
}

.overflow-x-auto::-webkit-scrollbar {
  display: none;
  /* Chrome, Safari, Opera */
}
</style>
