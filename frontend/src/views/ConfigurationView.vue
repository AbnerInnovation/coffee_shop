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
    <div v-else class="space-y-6 sm:space-y-8">
      <!-- Print Settings Section -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div class="px-3 sm:px-4 py-2 sm:py-3 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-2">
            <div class="p-1.5 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg">
              <svg class="w-5 h-5 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
              </svg>
            </div>
            <div>
              <h2 class="text-base sm:text-lg font-bold text-gray-900 dark:text-white">
                Configuración de Impresión
              </h2>
              <p class="text-xs text-gray-600 dark:text-gray-400">
                Configura tus impresoras y tickets térmicos
              </p>
            </div>
          </div>
        </div>
        <div class="p-3 sm:p-4 space-y-3">
          <!-- Advanced Printing Toggle (Cloud only AND not POS mode) -->
          <div v-if="platformFeatures.cloudOnly.menuManagement && !isPosOnlyMode" class="bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 rounded-lg p-4 border-2 border-purple-200 dark:border-purple-800">
            <div class="flex items-center justify-between gap-3">
              <div class="flex items-center gap-3 flex-1 min-w-0">
                <div class="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex-shrink-0">
                  <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <h3 class="text-base font-bold text-gray-900 dark:text-white">
                    Impresión Avanzada
                  </h3>
                  <p class="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                    Activa el sistema multi-impresoras con routing por categoría y configuración individual
                  </p>
                </div>
              </div>
              <button
                @click="restaurantSettings.toggleAdvancedPrinting"
                :disabled="isSaving"
                :class="[
                  'relative inline-flex h-7 w-12 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-purple-600 focus:ring-offset-2 dark:focus:ring-offset-gray-800',
                  advancedPrintingEnabled
                    ? 'bg-purple-600'
                    : 'bg-gray-300 dark:bg-gray-600',
                  isSaving ? 'opacity-50 cursor-not-allowed' : ''
                ]"
              >
                <span
                  :class="[
                    'pointer-events-none inline-block h-6 w-6 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out',
                    advancedPrintingEnabled ? 'translate-x-5' : 'translate-x-0'
                  ]"
                />
              </button>
            </div>
            
            <!-- Link to Printer Management when enabled -->
            <div v-if="advancedPrintingEnabled" class="mt-3 pt-3 border-t border-purple-200 dark:border-purple-800">
              <router-link
                to="/printers"
                class="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium rounded-lg transition-colors duration-200"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                </svg>
                Configurar Impresoras
              </router-link>
            </div>
          </div>

          <!-- Kitchen Print Settings (only if kitchen module is enabled AND advanced printing is disabled) -->
          <div v-if="showKitchen && !advancedPrintingEnabled" class="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
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

          <!-- Paper Width Settings (only if kitchen module is enabled AND advanced printing is disabled) -->
          <transition
            enter-active-class="transition ease-out duration-200"
            enter-from-class="opacity-0 -translate-y-2"
            enter-to-class="opacity-100 translate-y-0"
            leave-active-class="transition ease-in duration-150"
            leave-from-class="opacity-100 translate-y-0"
            leave-to-class="opacity-0 -translate-y-2"
          >
            <div v-if="showKitchen && kitchenPrintEnabled && !advancedPrintingEnabled" class="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
              <div class="flex items-center gap-2 mb-3">
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
              <div class="grid grid-cols-2 gap-2">
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
                  <div class="p-2 text-center">
                    <div class="mx-auto w-6 h-6 mb-1 flex items-center justify-center">
                      <svg class="w-full h-full text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div :class="[
                      'text-lg font-bold',
                      currentPaperWidth === 58 ? 'text-indigo-700 dark:text-indigo-300' : 'text-gray-900 dark:text-white'
                    ]">
                      58mm
                    </div>
                    <div :class="[
                      'text-[9px] font-medium uppercase tracking-wide',
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
                  <div class="p-2 text-center">
                    <div class="mx-auto w-6 h-6 mb-1 flex items-center justify-center">
                      <svg class="w-full h-full text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div :class="[
                      'text-lg font-bold',
                      currentPaperWidth === 80 ? 'text-indigo-700 dark:text-indigo-300' : 'text-gray-900 dark:text-white'
                    ]">
                      80mm
                    </div>
                    <div :class="[
                      'text-[9px] font-medium uppercase tracking-wide',
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

          <!-- Customer Print Settings (only if advanced printing is disabled) -->
          <div v-if="!advancedPrintingEnabled" class="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
            <div class="flex items-center justify-between gap-3">
              <div class="flex items-center gap-2 sm:gap-3 flex-1 min-w-0">
                <div class="p-1.5 sm:p-2 bg-green-100 dark:bg-green-900/30 rounded-lg flex-shrink-0">
                  <svg class="w-5 h-5 sm:w-6 sm:h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <h3 class="text-sm sm:text-base font-semibold text-gray-900 dark:text-white">
                    {{ t('app.subscription.settings.customer_print.title') }}
                  </h3>
                  <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                    {{ t('app.subscription.settings.customer_print.description') }}
                  </p>
                </div>
              </div>
              <button
                @click="restaurantSettings.toggleCustomerPrint"
                :disabled="isSaving"
                :class="[
                  'relative inline-flex h-6 w-11 sm:h-7 sm:w-12 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-green-600 focus:ring-offset-2 dark:focus:ring-offset-gray-800',
                  customerPrintEnabled
                    ? 'bg-green-600'
                    : 'bg-gray-300 dark:bg-gray-600',
                  isSaving ? 'opacity-50 cursor-not-allowed' : ''
                ]"
              >
                <span
                  :class="[
                    'pointer-events-none inline-block h-5 w-5 sm:h-6 sm:w-6 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out',
                    customerPrintEnabled ? 'translate-x-5' : 'translate-x-0'
                  ]"
                />
              </button>
            </div>
          </div>

          <!-- Customer Paper Width Settings (only if advanced printing is disabled) -->
          <transition
            enter-active-class="transition ease-out duration-200"
            enter-from-class="opacity-0 -translate-y-2"
            enter-to-class="opacity-100 translate-y-0"
            leave-active-class="transition ease-in duration-150"
            leave-from-class="opacity-100 translate-y-0"
            leave-to-class="opacity-0 -translate-y-2"
          >
            <div v-if="customerPrintEnabled && !advancedPrintingEnabled" class="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
              <div class="flex items-center gap-2 mb-3">
                <div class="p-1.5 sm:p-2 bg-green-100 dark:bg-green-900/30 rounded-lg flex-shrink-0">
                  <svg class="w-5 h-5 sm:w-6 sm:h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <h3 class="text-sm sm:text-base font-semibold text-gray-900 dark:text-white">
                    {{ t('app.subscription.settings.customer_paper_width.title') }}
                  </h3>
                  <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                    {{ t('app.subscription.settings.customer_paper_width.description') }}
                  </p>
                </div>
              </div>

              <!-- Customer Paper Width Options -->
              <div class="grid grid-cols-2 gap-2">
                <button
                  @click="() => restaurantSettings.setCustomerPaperWidth(58)"
                  :disabled="isSaving"
                  :class="[
                    'relative overflow-hidden rounded-lg border-2 transition-all duration-200',
                    currentCustomerPaperWidth === 58 
                      ? 'border-green-500 bg-green-50 dark:bg-green-900/20' 
                      : 'border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600'
                  ]"
                >
                  <div class="p-2 text-center">
                    <div class="mx-auto w-6 h-6 mb-1 flex items-center justify-center">
                      <svg class="w-full h-full text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div :class="[
                      'text-lg font-bold',
                      currentCustomerPaperWidth === 58 ? 'text-green-700 dark:text-green-300' : 'text-gray-900 dark:text-white'
                    ]">
                      58mm
                    </div>
                    <div :class="[
                      'text-[9px] font-medium uppercase tracking-wide',
                      currentCustomerPaperWidth === 58 ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'
                    ]">
                      {{ t('app.subscription.settings.customer_paper_width.compact') }}
                    </div>
                  </div>
                  <div v-if="currentCustomerPaperWidth === 58" class="absolute top-1 right-1 sm:top-1.5 sm:right-1.5">
                    <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                  </div>
                </button>

                <button
                  @click="() => restaurantSettings.setCustomerPaperWidth(80)"
                  :disabled="isSaving"
                  :class="[
                    'relative overflow-hidden rounded-lg border-2 transition-all duration-200',
                    currentCustomerPaperWidth === 80 
                      ? 'border-green-500 bg-green-50 dark:bg-green-900/20' 
                      : 'border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600'
                  ]"
                >
                  <div class="p-2 text-center">
                    <div class="mx-auto w-6 h-6 mb-1 flex items-center justify-center">
                      <svg class="w-full h-full text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div :class="[
                      'text-lg font-bold',
                      currentCustomerPaperWidth === 80 ? 'text-green-700 dark:text-green-300' : 'text-gray-900 dark:text-white'
                    ]">
                      80mm
                    </div>
                    <div :class="[
                      'text-[9px] font-medium uppercase tracking-wide',
                      currentCustomerPaperWidth === 80 ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'
                    ]">
                      {{ t('app.subscription.settings.customer_paper_width.standard') }}
                    </div>
                  </div>
                  <div v-if="currentCustomerPaperWidth === 80" class="absolute top-1 right-1 sm:top-1.5 sm:right-1.5">
                    <svg class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                  </div>
                </button>
              </div>
            </div>
          </transition>

          <!-- Print Test Button -->
          <div class="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
            <div class="flex items-center justify-between gap-3">
              <div class="flex items-center gap-2 sm:gap-3 flex-1 min-w-0">
                <div class="p-1.5 sm:p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex-shrink-0">
                  <svg class="w-5 h-5 sm:w-6 sm:h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div class="flex-1 min-w-0">
                  <h3 class="text-sm sm:text-base font-semibold text-gray-900 dark:text-white">
                    Probar Impresión
                  </h3>
                  <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                    Prueba tus tickets de cocina y cliente con datos de ejemplo
                  </p>
                </div>
              </div>
              <router-link
                to="/print-test"
                class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                </svg>
                <span class="hidden sm:inline">Probar Impresión</span>
                <span class="sm:hidden">Probar</span>
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- General Settings Section (hidden in POS only mode) -->
      <div v-if="!isPosOnlyMode" class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div class="px-3 sm:px-4 py-2 sm:py-3 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-2">
            <div class="p-1.5 bg-gray-100 dark:bg-gray-700 rounded-lg">
              <svg class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <div>
              <h2 class="text-base sm:text-lg font-bold text-gray-900 dark:text-white">
                Configuración General
              </h2>
              <p class="text-xs text-gray-600 dark:text-gray-400">
                Opciones generales del restaurante
              </p>
            </div>
          </div>
        </div>
        <div class="p-3 sm:p-4">
          <!-- Dine-in Without Table Settings -->
          <div>
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

      <!-- Payment Methods Section -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div class="px-3 sm:px-4 py-2 sm:py-3 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-2">
            <div class="p-1.5 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg">
              <svg class="w-5 h-5 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
              </svg>
            </div>
            <div>
              <h2 class="text-base sm:text-lg font-bold text-gray-900 dark:text-white">
                Métodos de Pago
              </h2>
              <p class="text-xs text-gray-600 dark:text-gray-400">
                Configura los métodos de pago disponibles
              </p>
            </div>
          </div>
        </div>
        <div class="p-3 sm:p-4">
          <!-- Payment Methods Configuration -->
          <div class="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3 border border-gray-200 dark:border-gray-700">
            <div class="flex items-center gap-2 sm:gap-3 mb-4">
              <div class="p-1.5 sm:p-2 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg flex-shrink-0">
                <svg class="w-5 h-5 sm:w-6 sm:h-6 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <h3 class="text-sm sm:text-base font-semibold text-gray-900 dark:text-white">
                  {{ t('app.subscription.settings.payment_methods.title') }}
                </h3>
                <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                  {{ t('app.subscription.settings.payment_methods.description') }}
                </p>
              </div>
            </div>

            <!-- Payment Methods Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <!-- Cash (Always Enabled) -->
                <div class="flex items-center justify-between p-2.5 bg-white dark:bg-gray-800 rounded-lg border-2 border-emerald-500 dark:border-emerald-600">
                  <div class="flex items-center gap-3">
                    <svg class="w-5 h-5 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                    <span class="text-sm font-medium text-gray-900 dark:text-white">
                      {{ t('app.subscription.settings.payment_methods.cash') }}
                    </span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-xs text-emerald-600 dark:text-emerald-400 font-medium">Siempre activo</span>
                    <svg class="w-5 h-5 text-emerald-600 dark:text-emerald-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                  </div>
                </div>

                <!-- Card -->
                <div class="flex items-center justify-between p-2.5 bg-white dark:bg-gray-800 rounded-lg border-2 transition-colors" :class="paymentMethodsConfig.card ? 'border-indigo-500 dark:border-indigo-600' : 'border-gray-200 dark:border-gray-700'">
                  <div class="flex items-center gap-3">
                    <svg class="w-5 h-5" :class="paymentMethodsConfig.card ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                    </svg>
                    <span class="text-sm font-medium text-gray-900 dark:text-white">
                      {{ t('app.subscription.settings.payment_methods.card') }}
                    </span>
                  </div>
                  <button
                    @click="() => restaurantSettings.togglePaymentMethod('card')"
                    :disabled="isSaving"
                    :class="[
                      'relative inline-flex h-5 w-9 sm:h-6 sm:w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2 dark:focus:ring-offset-gray-800',
                      paymentMethodsConfig.card ? 'bg-indigo-600' : 'bg-gray-300 dark:bg-gray-600',
                      isSaving ? 'opacity-50 cursor-not-allowed' : ''
                    ]"
                  >
                    <span :class="['pointer-events-none inline-block h-4 w-4 sm:h-5 sm:w-5 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out', paymentMethodsConfig.card ? 'translate-x-4 sm:translate-x-5' : 'translate-x-0']" />
                  </button>
                </div>

                <!-- Digital -->
                <div class="flex items-center justify-between p-2.5 bg-white dark:bg-gray-800 rounded-lg border-2 transition-colors" :class="paymentMethodsConfig.digital ? 'border-indigo-500 dark:border-indigo-600' : 'border-gray-200 dark:border-gray-700'">
                  <div class="flex items-center gap-3">
                    <svg class="w-5 h-5" :class="paymentMethodsConfig.digital ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                    <span class="text-sm font-medium text-gray-900 dark:text-white">
                      {{ t('app.subscription.settings.payment_methods.digital') }}
                    </span>
                  </div>
                  <button
                    @click="() => restaurantSettings.togglePaymentMethod('digital')"
                    :disabled="isSaving"
                    :class="[
                      'relative inline-flex h-5 w-9 sm:h-6 sm:w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2 dark:focus:ring-offset-gray-800',
                      paymentMethodsConfig.digital ? 'bg-indigo-600' : 'bg-gray-300 dark:bg-gray-600',
                      isSaving ? 'opacity-50 cursor-not-allowed' : ''
                    ]"
                  >
                    <span :class="['pointer-events-none inline-block h-4 w-4 sm:h-5 sm:w-5 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out', paymentMethodsConfig.digital ? 'translate-x-4 sm:translate-x-5' : 'translate-x-0']" />
                  </button>
                </div>

                <!-- Other -->
                <div class="flex items-center justify-between p-2.5 bg-white dark:bg-gray-800 rounded-lg border-2 transition-colors" :class="paymentMethodsConfig.other ? 'border-indigo-500 dark:border-indigo-600' : 'border-gray-200 dark:border-gray-700'">
                  <div class="flex items-center gap-3">
                    <svg class="w-5 h-5" :class="paymentMethodsConfig.other ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    <span class="text-sm font-medium text-gray-900 dark:text-white">
                      {{ t('app.subscription.settings.payment_methods.other') }}
                    </span>
                  </div>
                  <button
                    @click="() => restaurantSettings.togglePaymentMethod('other')"
                    :disabled="isSaving"
                    :class="[
                      'relative inline-flex h-5 w-9 sm:h-6 sm:w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2 dark:focus:ring-offset-gray-800',
                      paymentMethodsConfig.other ? 'bg-indigo-600' : 'bg-gray-300 dark:bg-gray-600',
                      isSaving ? 'opacity-50 cursor-not-allowed' : ''
                    ]"
                  >
                    <span :class="['pointer-events-none inline-block h-4 w-4 sm:h-5 sm:w-5 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out', paymentMethodsConfig.other ? 'translate-x-4 sm:translate-x-5' : 'translate-x-0']" />
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
import { useOperationMode } from '@/composables/useOperationMode'
import { platformFeatures } from '@/utils/platform'

const { t } = useI18n()

// Restaurant settings management
const restaurantSettings = useRestaurantSettings()

// Operation mode for kitchen module check and POS mode
const { showKitchen, isPosOnlyMode } = useOperationMode()

// Computed properties to avoid repetitive .value access
const advancedPrintingEnabled = computed(() => restaurantSettings.advancedPrintingEnabled.value)
const currentPaperWidth = computed(() => restaurantSettings.paperWidth.value)
const currentCustomerPaperWidth = computed(() => restaurantSettings.customerPaperWidth.value)
const isSaving = computed(() => restaurantSettings.savingSettings.value)
const isLoading = computed(() => restaurantSettings.loadingSettings.value)
const kitchenPrintEnabled = computed(() => restaurantSettings.kitchenPrintEnabled.value)
const customerPrintEnabled = computed(() => restaurantSettings.customerPrintEnabled.value)
const allowDineInWithoutTable = computed(() => restaurantSettings.allowDineInWithoutTable.value)
const paymentMethodsConfig = computed(() => restaurantSettings.paymentMethodsConfig.value)

// Lifecycle
onMounted(() => {
  restaurantSettings.loadSettings()
})
</script>
