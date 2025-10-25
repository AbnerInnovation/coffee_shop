<template>
  <div class="overflow-hidden rounded-lg bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 px-3 py-4 sm:px-4 sm:py-5 shadow">
    <dt class="truncate text-xs sm:text-sm font-medium text-gray-500 dark:text-gray-400">
      {{ label }}
    </dt>
    <dd class="mt-1 text-2xl sm:text-3xl font-semibold tracking-tight text-gray-900 dark:text-white">
      {{ value }}
    </dd>
    <dd v-if="comparison !== null && comparison !== undefined" class="mt-2 flex items-center text-sm" :class="comparisonClass">
      <ArrowUpIcon v-if="comparison > 0" class="h-4 w-4 mr-1" />
      <ArrowDownIcon v-else-if="comparison < 0" class="h-4 w-4 mr-1" />
      <span>{{ comparisonText }}</span>
    </dd>
    <dd v-if="subtitle" class="mt-2 text-xs text-gray-500 dark:text-gray-400">
      {{ subtitle }}
    </dd>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/vue/24/outline';

const props = defineProps<{
  label: string;
  value: string | number;
  comparison?: number | null;
  comparisonLabel?: string;
  subtitle?: string;
}>();

const comparisonClass = computed(() => {
  if (props.comparison === null || props.comparison === undefined) return '';
  return props.comparison >= 0 ? 'text-green-600' : 'text-red-600';
});

const comparisonText = computed(() => {
  if (props.comparison === null || props.comparison === undefined) return '';
  const absValue = Math.abs(props.comparison);
  const formattedValue = props.comparisonLabel?.includes('$') 
    ? `$${absValue.toFixed(2)}` 
    : absValue.toString();
  return `${formattedValue} ${props.comparisonLabel || ''}`;
});
</script>
