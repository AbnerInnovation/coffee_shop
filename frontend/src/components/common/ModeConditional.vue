<template>
  <slot v-if="shouldShow" />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useOperationMode } from '@/composables/useOperationMode'

/**
 * ModeConditional - Conditional rendering based on operation mode
 * 
 * Simplifies showing/hiding components based on operation mode features.
 * 
 * Usage:
 *   <ModeConditional feature="show_tables">
 *     <TablesSection />
 *   </ModeConditional>
 */

const props = defineProps<{
  feature?: 'show_tables' | 'show_kitchen' | 'show_waiters' | 'show_delivery'
  requiresKitchen?: boolean
  requiresTables?: boolean
  invert?: boolean  // Show when feature is NOT enabled
}>()

const { modeConfig, isLoaded } = useOperationMode()

const shouldShow = computed(() => {
  // While loading, show nothing to avoid flicker
  if (!isLoaded.value) {
    return false
  }

  let show = true

  // Check specific feature
  if (props.feature && modeConfig.value) {
    show = modeConfig.value[props.feature] ?? true
  }

  // Check kitchen requirement
  if (props.requiresKitchen && modeConfig.value) {
    show = show && (modeConfig.value.allows_kitchen_orders ?? true)
  }

  // Check tables requirement
  if (props.requiresTables && modeConfig.value) {
    show = show && (modeConfig.value.show_tables ?? true)
  }

  // Invert logic if needed
  if (props.invert) {
    show = !show
  }

  return show
})
</script>
