<template>
  <component
    :is="isButton ? 'button' : 'router-link'"
    :to="isButton ? undefined : to"
    @click="isButton ? $emit('click') : undefined"
    class="relative rounded-lg border border-gray-300 dark:border-gray-700 px-6 py-5 flex items-center space-x-3 hover:border-gray-400 dark:hover:border-gray-600 hover:bg-gray-50/50 dark:hover:bg-gray-800/50 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500 transition-colors"
  >
    <div class="flex-shrink-0">
      <component :is="icon" :class="iconClass" class="h-6 w-6" />
    </div>
    <div class="flex-1 min-w-0" :class="{ 'text-left': isButton }">
      <span v-if="!isButton" class="absolute inset-0" aria-hidden="true"></span>
      <p class="text-sm font-medium text-gray-900 dark:text-white">
        {{ title }}
      </p>
      <p class="text-sm text-gray-500 dark:text-gray-400 truncate">
        {{ description }}
      </p>
    </div>
  </component>
</template>

<script setup lang="ts">
import type { Component } from 'vue';

interface Props {
  icon: Component;
  iconClass?: string;
  title: string;
  description: string;
  to?: string;
  isButton?: boolean;
}

withDefaults(defineProps<Props>(), {
  iconClass: 'text-primary-600',
  isButton: false
});

defineEmits<{
  'click': [];
}>();
</script>
