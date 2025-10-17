<template>
  <button
    type="button"
    @click.stop="handleClick"
    class="w-full text-left px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2 transition-colors"
    :class="[variantClass, { 'opacity-50 cursor-not-allowed': disabled }]"
    role="menuitem"
    :disabled="disabled"
  >
    <component v-if="icon" :is="icon" class="h-4 w-4" />
    <slot></slot>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Component } from 'vue';

interface Props {
  icon?: Component;
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info';
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  disabled: false
});

const emit = defineEmits<{
  click: [];
}>();

const variantClass = computed(() => {
  const variants = {
    default: 'text-gray-700 dark:text-gray-300',
    primary: 'text-indigo-600 dark:text-indigo-400',
    success: 'text-green-600 dark:text-green-400',
    warning: 'text-amber-600 dark:text-amber-400',
    danger: 'text-red-600 dark:text-red-400',
    info: 'text-blue-600 dark:text-blue-400'
  };
  return variants[props.variant];
});

const handleClick = () => {
  if (!props.disabled) {
    emit('click');
  }
};
</script>
