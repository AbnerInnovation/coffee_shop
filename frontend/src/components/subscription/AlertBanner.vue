<template>
  <div :class="[
    'border-l-4 p-3 sm:p-4 rounded-lg',
    variantClasses
  ]">
    <div class="flex items-start">
      <component :is="icon" class="h-6 w-6 mr-3 flex-shrink-0" :class="iconColorClass" />
      <div class="flex-1">
        <h3 :class="['text-sm font-semibold', titleColorClass]">
          {{ title }}
        </h3>
        <p :class="['mt-1 text-sm', textColorClass]">
          {{ message }}
        </p>
        <button
          v-if="showButton"
          @click="$emit('action')"
          :class="['mt-3 px-4 py-2 text-white rounded-lg transition-colors text-sm font-medium', buttonColorClass]"
        >
          {{ buttonText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'
import {
  ExclamationTriangleIcon,
  ExclamationCircleIcon,
  InformationCircleIcon
} from '@heroicons/vue/24/outline'

type AlertVariant = 'warning' | 'error' | 'info'

interface Props {
  variant?: AlertVariant
  title: string
  message: string
  buttonText?: string
  showButton?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'info',
  showButton: true
})

defineEmits<{
  action: []
}>()

const icon = computed(() => {
  const icons: Record<AlertVariant, Component> = {
    warning: ExclamationTriangleIcon,
    error: ExclamationCircleIcon,
    info: InformationCircleIcon
  }
  return icons[props.variant]
})

const variantClasses = computed(() => {
  const classes: Record<AlertVariant, string> = {
    warning: 'bg-amber-50 dark:bg-amber-900/20 border-amber-500',
    error: 'bg-red-50 dark:bg-red-900/20 border-red-500',
    info: 'bg-blue-50 dark:bg-blue-900/20 border-blue-500'
  }
  return classes[props.variant]
})

const iconColorClass = computed(() => {
  const classes: Record<AlertVariant, string> = {
    warning: 'text-amber-500',
    error: 'text-red-500',
    info: 'text-blue-500'
  }
  return classes[props.variant]
})

const titleColorClass = computed(() => {
  const classes: Record<AlertVariant, string> = {
    warning: 'text-amber-800 dark:text-amber-200',
    error: 'text-red-800 dark:text-red-200',
    info: 'text-blue-800 dark:text-blue-200'
  }
  return classes[props.variant]
})

const textColorClass = computed(() => {
  const classes: Record<AlertVariant, string> = {
    warning: 'text-amber-700 dark:text-amber-300',
    error: 'text-red-700 dark:text-red-300',
    info: 'text-blue-700 dark:text-blue-300'
  }
  return classes[props.variant]
})

const buttonColorClass = computed(() => {
  const classes: Record<AlertVariant, string> = {
    warning: 'bg-amber-600 hover:bg-amber-700',
    error: 'bg-red-600 hover:bg-red-700',
    info: 'bg-blue-600 hover:bg-blue-700'
  }
  return classes[props.variant]
})
</script>
