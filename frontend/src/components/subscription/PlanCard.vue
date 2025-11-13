<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
    <div class="px-3 py-2 sm:px-4 sm:py-3 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between gap-3">
        <h2 class="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">
          {{ title }}
        </h2>
        <div v-if="hasSubscription" class="flex items-center gap-2">
          <h3 class="text-lg sm:text-xl font-bold text-gray-900 dark:text-white">
            {{ planName }}
          </h3>
          <span :class="statusClass" class="px-2 py-0.5 text-xs font-semibold rounded-full">
            {{ statusLabel }}
          </span>
        </div>
      </div>
    </div>

    <!-- With Subscription -->
    <div v-if="hasSubscription" class="p-3 sm:p-4">
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
        <div>
          <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">{{ priceLabel }}</p>
          <p class="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">
            {{ formattedPrice }}
          </p>
        </div>
        <div v-if="daysUntilRenewal !== null && daysUntilRenewal !== undefined">
          <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">{{ renewalLabel }}</p>
          <p class="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">
            {{ daysUntilRenewal }} {{ daysLabel }}
          </p>
        </div>
      </div>
    </div>

    <!-- No Subscription -->
    <div v-else class="p-4 text-center">
      <p class="text-gray-500 dark:text-gray-400 mb-4">
        {{ noSubscriptionMessage }}
      </p>
      <button
        @click="$emit('choose-plan')"
        class="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
      >
        {{ choosePlanLabel }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string
  hasSubscription: boolean
  planName?: string
  statusClass?: string
  statusLabel?: string
  priceLabel?: string
  formattedPrice?: string
  renewalLabel?: string
  daysUntilRenewal?: number | null
  daysLabel?: string
  noSubscriptionMessage?: string
  choosePlanLabel?: string
}

defineProps<Props>()

defineEmits<{
  'choose-plan': []
}>()
</script>
