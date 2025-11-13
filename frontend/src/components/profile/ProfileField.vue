<template>
  <div :class="fullWidth ? 'col-span-2' : ''">
    <label class="block text-xs sm:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
      {{ label }}
    </label>
    <div class="text-sm sm:text-base text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-700 px-3 py-2 sm:px-4 sm:py-3 rounded-lg">
      <slot>{{ value || '-' }}</slot>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  label: string
  value?: string | number
  fullWidth?: boolean
}

defineProps<Props>()
</script>
