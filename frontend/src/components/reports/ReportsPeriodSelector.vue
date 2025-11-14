<template>
  <div class="mt-3 sm:mt-4 flex flex-wrap items-center gap-2 sm:gap-4">
    <!-- Period Buttons -->
    <div class="flex flex-wrap sm:flex-nowrap rounded-md shadow-sm gap-1 sm:gap-0">
      <button
        v-for="period in periods"
        :key="period.value"
        @click="$emit('period-change', period.value)"
        :class="[
          'px-3 sm:px-4 py-2 text-xs sm:text-sm font-medium',
          selectedPeriod === period.value
            ? 'bg-indigo-600 text-white'
            : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700',
          period.value === 'today' ? 'rounded-l-md' : '',
          period.value === 'custom' ? 'rounded-r-md' : '',
          'border border-gray-300 dark:border-gray-600'
        ]"
      >
        {{ period.label }}
      </button>
    </div>

    <!-- Custom Date Range -->
    <div v-if="selectedPeriod === 'custom'" class="w-full">
      <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-2">
        <input
          :value="customStartDate"
          @input="$emit('update:customStartDate', ($event.target as HTMLInputElement).value)"
          type="date"
          class="flex-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm px-4 py-2.5"
        />
        <span class="text-gray-500 dark:text-gray-400 text-sm">{{ t('app.reports.to') }}</span>
        <input
          :value="customEndDate"
          @input="$emit('update:customEndDate', ($event.target as HTMLInputElement).value)"
          type="date"
          class="flex-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm px-4 py-2.5"
        />
        <button
          @click="$emit('apply')"
          class="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 w-full sm:w-auto"
        >
          {{ t('app.reports.apply') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';

/**
 * Period selector component for reports
 * Allows selection of predefined periods or custom date range
 */

const { t } = useI18n();

defineProps<{
  periods: Array<{ value: string; label: string }>;
  selectedPeriod: string;
  customStartDate: string;
  customEndDate: string;
}>();

defineEmits<{
  'period-change': [value: string];
  'update:customStartDate': [value: string];
  'update:customEndDate': [value: string];
  'apply': [];
}>();
</script>
