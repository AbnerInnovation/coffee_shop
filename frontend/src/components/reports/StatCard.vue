<template>
  <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg" :class="fullWidth ? 'col-span-2 sm:col-span-1' : ''">
    <div class="p-3">
      <div class="flex items-center gap-2">
        <div class="flex-shrink-0">
          <component :is="icon" :class="iconColorClass" class="h-5 w-5" />
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-xs font-medium text-gray-500 dark:text-gray-400 truncate mb-0.5">
            {{ label }}
          </p>
          <p class="text-lg font-bold text-gray-900 dark:text-white">
            <slot>{{ formattedValue }}</slot>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'

interface Props {
  icon: Component
  label: string
  value?: number | string
  iconColor?: 'green' | 'blue' | 'purple' | 'amber' | 'red'
  fullWidth?: boolean
  decimals?: number
  prefix?: string
}

const props = withDefaults(defineProps<Props>(), {
  iconColor: 'blue',
  decimals: 2,
  prefix: '$'
})

const iconColorClass = computed(() => {
  const colors = {
    green: 'text-green-600',
    blue: 'text-blue-600',
    purple: 'text-purple-600',
    amber: 'text-amber-600',
    red: 'text-red-600'
  }
  return colors[props.iconColor]
})

const formattedValue = computed(() => {
  if (props.value === undefined) return ''
  
  if (typeof props.value === 'number') {
    const formatted = props.value.toLocaleString('es-MX', {
      minimumFractionDigits: props.decimals,
      maximumFractionDigits: props.decimals
    })
    return props.prefix ? `${props.prefix}${formatted}` : formatted
  }
  
  return props.value
})
</script>
