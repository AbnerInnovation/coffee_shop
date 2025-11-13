<template>
  <div class="border border-gray-200 dark:border-gray-700 overflow-hidden rounded-lg">
    <div class="p-3 sm:p-5">
      <div class="flex items-start gap-2 sm:gap-3">
        <div class="flex-shrink-0">
          <component :is="icon" :class="iconClass" class="h-5 w-5 sm:h-6 sm:w-6" />
        </div>
        <div class="flex-1 min-w-0">
          <dl>
            <dt class="text-xs sm:text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
              {{ label }}
            </dt>
            <dd class="mt-1">
              <div class="text-xl sm:text-2xl font-semibold text-gray-900 dark:text-white break-words">
                {{ value }}
              </div>
              <div v-if="subtitle" :class="subtitleClass" class="mt-0.5 text-xs sm:text-sm font-semibold">
                {{ subtitle }}
              </div>
            </dd>
          </dl>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue';

interface Props {
  icon: Component;
  iconClass?: string;
  label: string;
  value: string | number;
  subtitle?: string;
  subtitleClass?: string;
}

withDefaults(defineProps<Props>(), {
  iconClass: 'text-gray-400',
  subtitleClass: 'text-gray-500 dark:text-gray-400'
});
</script>
