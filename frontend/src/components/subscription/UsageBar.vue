<template>
  <div class="space-y-1">
    <div class="flex justify-between items-center">
      <span class="text-xs font-medium text-gray-700 dark:text-gray-300">
        {{ label }}
      </span>
      <span class="text-xs text-gray-500 dark:text-gray-400">
        {{ current }} / {{ maxDisplay }}
      </span>
    </div>
    
    <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
      <div
        :class="getBarColor(percentage)"
        class="h-2 rounded-full transition-all duration-300"
        :style="{ width: `${Math.min(percentage, 100)}%` }"
      ></div>
    </div>
    
    <div v-if="percentage >= 80" class="flex items-center gap-1 text-xs">
      <ExclamationTriangleIcon class="h-3 w-3 text-yellow-500" />
      <span class="text-yellow-600 dark:text-yellow-400">
        {{ percentage >= 100 ? 'Límite alcanzado' : 'Cerca del límite' }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline';

const props = defineProps<{
  label: string;
  current: number;
  max: number;
  percentage: number;
}>();

const maxDisplay = computed(() => {
  return props.max === -1 ? '∞' : props.max;
});

const getBarColor = (percentage: number) => {
  if (percentage >= 100) return 'bg-red-600';
  if (percentage >= 80) return 'bg-yellow-500';
  return 'bg-green-500';
};
</script>
