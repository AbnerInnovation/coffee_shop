<template>
  <div class="max-w-7xl mx-auto px-3 sm:px-4 lg:px-6 py-3 sm:py-6">
    <!-- Header -->
    <div class="mb-4 sm:mb-6">
      <h1 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
        {{ t('app.subscription.settings.title') }}
      </h1>
      <p class="mt-1 text-xs sm:text-sm text-gray-600 dark:text-gray-400">
        {{ t('app.subscription.settings.subtitle') }}
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex justify-center items-center py-12">
      <ArrowPathIcon class="h-12 w-12 animate-spin text-indigo-600" />
    </div>

    <!-- Content -->
    <div v-else class="space-y-4 sm:space-y-6">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        <div class="p-4 sm:p-6 space-y-4 sm:space-y-6">
          <!-- Kitchen Print Settings -->
          <div class="bg-gray-50 dark:bg-gray-900/50 rounded-lg sm:rounded-xl p-4 sm:p-5 border border-gray-200 dark:border-gray-700">
            <div class="flex items-center justify-between gap-3">
              <div class="flex items-center gap-2 sm:gap-3 flex-1 min-w-0">
                <div class="p-1.5 sm:p-2 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg flex-shrink-0">
                  <svg class="w-5 h-5 sm:w-6 sm:h-6 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <h3 class="text-sm sm:text-base font-semibold text-gray-900 dark:text-white">
                    {{ t('app.subscription.settings.kitchen_print.title') }}
                  </h3>
                  <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                    {{ t('app.subscription.settings.kitchen_print.description') }}
                  </p>
                </div>
              </div>
              <button
                @click="restaurantSettings.toggleKitchenPrint"
                :disabled="isSaving"
                :class="[
                  'relative inline-flex h-6 w-11 sm:h-7 sm:w-12 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2 dark:focus:ring-offset-gray-800',
                  kitchenPrintEnabled
                    ? 'bg-indigo-600'
                    : 'bg-gray-300 dark:bg-gray-600',
                  isSaving ? 'opacity-50 cursor-not-allowed' : ''
                ]"
              >
                <span
                  :class="[
                    'pointer-events-none inline-block h-5 w-5 sm:h-6 sm:w-6 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out',
                    kitchenPrintEnabled ? 'translate-x-5' : 'translate-x-0'
                  ]"
                />
              </button>
            </div>
          </div>

          <!-- Paper Width Settings -->
          <transition
            enter-active-class="transition ease-out duration-200"
            enter-from-class="opacity-0 -translate-y-2"
            enter-to-class="opacity-100 translate-y-0"
            leave-active-class="transition ease-in duration-150"
            leave-from-class="opacity-100 translate-y-0"
            leave-to-class="opacity-0 -translate-y-2"
          >
            <div v-if="kitchenPrintEnabled" class="bg-gray-50 dark:bg-gray-900/50 rounded-lg sm:rounded-xl p-4 sm:p-5 border border-gray-200 dark:border-gray-700">
              <div class="flex items-center gap-2 sm:gap-3 mb-3 sm:mb-4">
                <div class="p-1.5 sm:p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex-shrink-0">
                  <svg class="w-5 h-5 sm:w-6 sm:h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <h3 class="text-sm sm:text-base font-semibold text-gray-900 dark:text-white">
                    {{ t('app.subscription.settings.paper_width.title') }}
                  </h3>
                  <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                    {{ t('app.subscription.settings.paper_width.description') }}
                  </p>
                </div>
              </div>

              <!-- Paper Width Options -->
              <div class="grid grid-cols-2 gap-3 sm:gap-4">
                <button
                  @click="() => restaurantSettings.setPaperWidth(58)"
                  :disabled="isSaving"
                  :class="[
                    'relative overflow-hidden rounded-lg border-2 transition-all duration-200',
                    currentPaperWidth === 58 
                      ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20' 
                      : 'border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600'
                  ]"
                >
                  <div class="p-3 sm:p-4 text-center">
                    <div class="mx-auto w-8 h-8 sm:w-10 sm:h-10 mb-2 flex items-center justify-center">
                      <svg class="w-full h-full text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div :class="[
                      'text-xl sm:text-2xl font-bold',
                      currentPaperWidth === 58 ? 'text-indigo-700 dark:text-indigo-300' : 'text-gray-900 dark:text-white'
                    ]">
                      58mm
                    </div>
                    <div :class="[
                      'text-[9px] sm:text-[10px] font-medium uppercase tracking-wide mt-0.5',
                      currentPaperWidth === 58 ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-500 dark:text-gray-400'
                    ]">
                      {{ t('app.subscription.settings.paper_width.compact') }}
                    </div>
                  </div>
                  <div v-if="currentPaperWidth === 58" class="absolute top-1 right-1 sm:top-1.5 sm:right-1.5">
                    <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-indigo-600 dark:text-indigo-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                  </div>
                </button>

                <button
                  @click="() => restaurantSettings.setPaperWidth(80)"
                  :disabled="isSaving"
                  :class="[
                    'relative overflow-hidden rounded-lg border-2 transition-all duration-200',
                    currentPaperWidth === 80 
                      ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20' 
                      : 'border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600'
                  ]"
                >
                  <div class="p-3 sm:p-4 text-center">
                    <div class="mx-auto w-8 h-8 sm:w-10 sm:h-10 mb-2 flex items-center justify-center">
                      <svg class="w-full h-full text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div :class="[
                      'text-xl sm:text-2xl font-bold',
                      currentPaperWidth === 80 ? 'text-indigo-700 dark:text-indigo-300' : 'text-gray-900 dark:text-white'
                    ]">
                      80mm
                    </div>
                    <div :class="[
                      'text-[9px] sm:text-[10px] font-medium uppercase tracking-wide mt-0.5',
                      currentPaperWidth === 80 ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-500 dark:text-gray-400'
                    ]">
                      {{ t('app.subscription.settings.paper_width.standard') }}
                    </div>
                  </div>
                  <div v-if="currentPaperWidth === 80" class="absolute top-1 right-1 sm:top-1.5 sm:right-1.5">
                    <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-indigo-600 dark:text-indigo-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                  </div>
                </button>
              </div>
            </div>
          </transition>

          <!-- Dine-in Without Table Settings -->
          <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
            <div class="flex items-center justify-between">
              <div class="flex-1">
                <h3 class="text-base font-semibold text-gray-900 dark:text-white">
                  {{ t('app.subscription.settings.dine_in_without_table.title') }}
                </h3>
                <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  {{ t('app.subscription.settings.dine_in_without_table.description') }}
                </p>
              </div>
              <div class="ml-4">
                <button
                  @click="restaurantSettings.toggleDineInWithoutTable"
                  :disabled="isSaving"
                  :class="[
                    allowDineInWithoutTable ? 'bg-indigo-600 hover:bg-indigo-700' : 'bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600',
                    'relative inline-flex h-5 w-9 sm:h-6 sm:w-11 flex-shrink-0 cursor-pointer rounded-full transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'
                  ]"
                >
                  <span
                    :class="[
                      allowDineInWithoutTable ? 'translate-x-5 sm:translate-x-6' : 'translate-x-0',
                      'pointer-events-none inline-block h-4 w-4 sm:h-5 sm:w-5 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out'
                    ]"
                  />
                </button>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ArrowPathIcon } from '@heroicons/vue/24/outline'
import { useRestaurantSettings } from '@/composables/useRestaurantSettings'

const { t } = useI18n()

// Restaurant settings management
const restaurantSettings = useRestaurantSettings()

// Computed properties to avoid repetitive .value access
const currentPaperWidth = computed(() => restaurantSettings.paperWidth.value)
const isSaving = computed(() => restaurantSettings.savingSettings.value)
const isLoading = computed(() => restaurantSettings.loadingSettings.value)
const kitchenPrintEnabled = computed(() => restaurantSettings.kitchenPrintEnabled.value)
const allowDineInWithoutTable = computed(() => restaurantSettings.allowDineInWithoutTable.value)

// Lifecycle
onMounted(() => {
  restaurantSettings.loadSettings()
})
</script>
