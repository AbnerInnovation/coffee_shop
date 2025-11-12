<template>
  <div
    :class="enabled ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' : 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700'"
    class="flex items-center gap-1.5 px-2 py-1.5 rounded-lg border"
  >
    <CheckCircleIcon
      v-if="enabled"
      class="h-4 w-4 text-green-600 dark:text-green-400 flex-shrink-0"
    />
    <XCircleIcon
      v-else
      class="h-4 w-4 text-gray-400 dark:text-gray-600 flex-shrink-0"
    />
    <span
      :class="enabled ? 'text-green-900 dark:text-green-100' : 'text-gray-500 dark:text-gray-400'"
      class="text-xs font-medium"
    >
      {{ label }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { CheckCircleIcon, XCircleIcon } from '@heroicons/vue/24/outline';

defineProps<{
  label: string;
  enabled: boolean;
}>();
</script>
