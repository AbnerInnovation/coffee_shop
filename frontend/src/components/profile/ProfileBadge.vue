<template>
  <span :class="badgeClass" class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold">
    <slot>{{ label }}</slot>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type BadgeVariant = 'sysadmin' | 'admin' | 'staff' | 'customer' | 'active' | 'inactive' | 'default'

interface Props {
  variant?: BadgeVariant
  label?: string
  customClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default'
})

const badgeClass = computed(() => {
  if (props.customClass) return props.customClass
  
  const variantClasses: Record<BadgeVariant, string> = {
    sysadmin: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    admin: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    staff: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    customer: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    active: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    inactive: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    default: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
  }
  
  return variantClasses[props.variant]
})
</script>
