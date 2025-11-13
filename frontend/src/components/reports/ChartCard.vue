<template>
  <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-3 sm:p-4">
    <h3 class="text-sm sm:text-base font-medium text-gray-900 dark:text-white mb-3">
      {{ title }}
    </h3>
    <div v-if="hasData" :class="heightClass">
      <slot />
    </div>
    <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
      {{ emptyMessage }}
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string
  hasData: boolean
  emptyMessage?: string
  height?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  emptyMessage: 'No hay datos disponibles',
  height: 'md'
})

const heightClass = {
  sm: 'h-48',
  md: 'h-56 sm:h-64',
  lg: 'h-72 sm:h-80'
}[props.height]
</script>
