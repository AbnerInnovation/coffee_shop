<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-4 sm:p-8">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex items-center gap-3 mb-2">
          <div class="p-3 bg-indigo-100 dark:bg-indigo-900/30 rounded-xl">
            <svg class="w-8 h-8 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
          </div>
          <div>
            <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
              Pruebas de Impresión
            </h1>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Prueba tus configuraciones de impresora con datos de ejemplo
            </p>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Left Column: Environment & Printer Selection -->
        <div class="lg:col-span-3 space-y-6">
          <!-- Environment Info -->
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700">
            <div class="bg-gradient-to-r from-indigo-500 to-purple-600 px-4 py-3">
              <h2 class="text-lg font-semibold text-white flex items-center gap-2">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Entorno
              </h2>
            </div>
            <div class="p-4 space-y-3">
              <div class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Plataforma</span>
                <span class="flex items-center gap-2 text-sm font-semibold" :class="isElectronApp ? 'text-green-600 dark:text-green-400' : 'text-blue-600 dark:text-blue-400'">
                  {{ isElectronApp ? '🖥️ Electron' : '🌐 Navegador' }}
                </span>
              </div>
              <div v-if="isElectronApp" class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Impresoras</span>
                <span class="text-sm font-semibold text-indigo-600 dark:text-indigo-400">
                  {{ printers.length }} disponibles
                </span>
              </div>
              <div v-if="selectedPrinter" class="p-3 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
                <p class="text-xs font-medium text-indigo-600 dark:text-indigo-400 mb-1">Impresora Activa</p>
                <p class="text-sm font-semibold text-gray-900 dark:text-white truncate">{{ selectedPrinter }}</p>
              </div>
            </div>
          </div>

          <!-- Printer Selection (Electron only) -->
          <div v-if="isElectronApp" class="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700">
            <div class="bg-gradient-to-r from-green-500 to-emerald-600 px-4 py-3">
              <h2 class="text-lg font-semibold text-white flex items-center gap-2">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                </svg>
                Impresoras
              </h2>
            </div>
            <div class="p-4 space-y-4">
              <button
                @click="loadPrinters"
                :disabled="isLoadingPrinters"
                class="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
              >
                <ArrowPathIcon :class="['h-5 w-5', { 'animate-spin': isLoadingPrinters }]" />
                {{ isLoadingPrinters ? 'Buscando...' : 'Buscar Impresoras' }}
              </button>
              
              <div v-if="printers.length > 0" class="space-y-3">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Seleccionar Impresora
                </label>
                <select
                  v-model="selectedPrinter"
                  class="block w-full px-3 py-2.5 text-sm border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent rounded-lg transition-all"
                >
                  <option :value="null">Impresora predeterminada</option>
                  <option
                    v-for="printer in printers"
                    :key="printer.name"
                    :value="printer.name"
                  >
                    {{ printer.displayName || printer.name }}{{ printer.isDefault ? ' ⭐' : '' }}
                  </option>
                </select>

                <!-- Selected Printer Info -->
                <div v-if="selectedPrinterInfo" class="p-3 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg border border-green-200 dark:border-green-800">
                  <div class="flex items-start gap-2">
                    <svg class="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-semibold text-gray-900 dark:text-white truncate">
                        {{ selectedPrinterInfo.displayName || selectedPrinterInfo.name }}
                      </p>
                      <p v-if="selectedPrinterInfo.description" class="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
                        {{ selectedPrinterInfo.description }}
                      </p>
                      <p class="text-xs text-green-600 dark:text-green-400 mt-1 font-medium">
                        {{ getPrinterStatus(selectedPrinterInfo.status) }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Test Buttons & Console -->
        <div class="lg:col-span-9 space-y-6">
          <!-- Test Buttons -->
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700">
            <div class="bg-gradient-to-r from-blue-500 to-indigo-600 px-6 py-4">
              <h2 class="text-xl font-semibold text-white flex items-center gap-2">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Pruebas de Impresión
              </h2>
              <p class="text-blue-100 text-sm mt-1">Haz clic en cualquier botón para probar la impresión</p>
            </div>
            
            <div class="p-6 grid gap-4" :class="[
              showKitchen && !isPosOnlyMode ? 'grid-cols-3' : 'grid-cols-2',
              isPosOnlyMode ? 'grid-cols-1' : ''
            ]">
              <!-- Kitchen Ticket (only if kitchen module is enabled) -->
              <button
                v-if="showKitchen"
                @click="testKitchenPrint"
                :disabled="isPrintingKitchen"
                class="group relative overflow-hidden bg-gradient-to-br from-gray-700 to-gray-800 hover:from-gray-600 hover:to-gray-700 text-white rounded-xl p-4 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-2xl hover:scale-105 transform"
              >
                <div class="relative">
                  <div class="flex justify-center mb-2">
                    <div class="p-2 bg-white/10 rounded-full">
                      <svg class="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                    </div>
                  </div>
                  <h3 class="text-base font-bold mb-1">Ticket de Cocina</h3>
                  <p class="text-xs text-gray-300 mb-2">Imprime un ticket de ejemplo para la cocina</p>
                  <div class="flex items-center justify-center gap-2 text-xs font-semibold">
                    <svg v-if="!isPrintingKitchen" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                    </svg>
                    <svg v-else class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ isPrintingKitchen ? 'Imprimiendo...' : 'Imprimir' }}
                  </div>
                </div>
              </button>

              <!-- Customer Receipt -->
              <button
                @click="testCustomerReceipt"
                :disabled="isPrintingCustomer"
                class="group relative overflow-hidden bg-gradient-to-br from-gray-700 to-gray-800 hover:from-gray-600 hover:to-gray-700 text-white rounded-xl p-4 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-2xl hover:scale-105 transform"
              >
                <div class="relative">
                  <div class="flex justify-center mb-2">
                    <div class="p-2 bg-white/10 rounded-full">
                      <svg class="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                  </div>
                  <h3 class="text-base font-bold mb-1">Ticket de Cliente</h3>
                  <p class="text-xs text-gray-300 mb-2">Imprime un recibo de ejemplo para el cliente</p>
                  <div class="flex items-center justify-center gap-2 text-xs font-semibold">
                    <svg v-if="!isPrintingCustomer" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                    </svg>
                    <svg v-else class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ isPrintingCustomer ? 'Imprimiendo...' : 'Imprimir' }}
                  </div>
                </div>
              </button>

              <!-- Pre-bill (hidden in POS only mode) -->
              <button
                v-if="!isPosOnlyMode"
                @click="testPreBill"
                :disabled="isPrintingPreBill"
                class="group relative overflow-hidden bg-gradient-to-br from-gray-700 to-gray-800 hover:from-gray-600 hover:to-gray-700 text-white rounded-xl p-4 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-2xl hover:scale-105 transform"
              >
                <div class="relative">
                  <div class="flex justify-center mb-2">
                    <div class="p-2 bg-white/10 rounded-full">
                      <svg class="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2zM10 8.5a.5.5 0 11-1 0 .5.5 0 011 0zm5 5a.5.5 0 11-1 0 .5.5 0 011 0z" />
                      </svg>
                    </div>
                  </div>
                  <h3 class="text-base font-bold mb-1">Pre-cuenta</h3>
                  <p class="text-xs text-gray-300 mb-2">Imprime una pre-cuenta de ejemplo</p>
                  <div class="flex items-center justify-center gap-2 text-xs font-semibold">
                    <svg v-if="!isPrintingPreBill" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                    </svg>
                    <svg v-else class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ isPrintingPreBill ? 'Imprimiendo...' : 'Imprimir' }}
                  </div>
                </div>
              </button>
            </div>
          </div>

          <!-- Console Output -->
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700">
            <div class="bg-gradient-to-r from-gray-800 to-gray-900 px-6 py-4 flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="flex gap-1.5">
                  <div class="w-3 h-3 rounded-full bg-red-500"></div>
                  <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
                  <div class="w-3 h-3 rounded-full bg-green-500"></div>
                </div>
                <h2 class="text-lg font-semibold text-white flex items-center gap-2">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  Console Log
                </h2>
              </div>
              <button
                @click="clearLogs"
                class="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-white text-xs font-medium rounded-md transition-colors"
              >
                Limpiar
              </button>
            </div>
            <div class="bg-gray-950 p-4 font-mono text-xs h-80 overflow-y-auto">
              <div v-if="logs.length === 0" class="flex items-center justify-center h-full text-gray-500">
                <div class="text-center">
                  <svg class="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <p>No hay logs aún...</p>
                  <p class="text-xs mt-1">Los mensajes aparecerán aquí</p>
                </div>
              </div>
              <div v-for="(log, index) in logs" :key="index" class="mb-1 leading-relaxed">
                <span :class="{
                  'text-green-400': log.includes('✅'),
                  'text-blue-400': log.includes('🔍') || log.includes('📥') || log.includes('📏'),
                  'text-yellow-400': log.includes('⚠️'),
                  'text-red-400': log.includes('❌'),
                  'text-purple-400': log.includes('🖨️') || log.includes('🖥️'),
                  'text-gray-400': !log.includes('✅') && !log.includes('🔍') && !log.includes('⚠️') && !log.includes('❌') && !log.includes('🖨️')
                }">{{ log }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowPathIcon } from '@heroicons/vue/24/outline';
import { usePrintTest } from '@/composables/usePrintTest';
import { useOperationMode } from '@/composables/useOperationMode';

const {
  logs,
  isElectronApp,
  isPrinting,
  isPrintingKitchen,
  isPrintingCustomer,
  isPrintingPreBill,
  printers,
  selectedPrinter,
  selectedPrinterInfo,
  isLoadingPrinters,
  loadPrinters,
  testKitchenPrint,
  testCustomerReceipt,
  testPreBill,
  getPrinterStatus,
  clearLogs
} = usePrintTest();

// Operation mode for kitchen module check and POS mode
const { showKitchen, isPosOnlyMode } = useOperationMode();
</script>
