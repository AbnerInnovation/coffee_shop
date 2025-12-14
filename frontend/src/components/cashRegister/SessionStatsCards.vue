<template>
  <div class="space-y-3">
    <!-- Primera fila: Saldos -->
    <div class="grid grid-cols-2 gap-2 sm:gap-3">
      <!-- Initial Balance -->
      <div class="bg-green-50 dark:bg-green-900/30 p-3 rounded-lg border border-green-200 dark:border-green-800">
        <div class="flex items-center justify-between mb-1">
          <h3 class="text-xs font-medium text-green-800 dark:text-green-200">
            {{ t('app.views.cashRegister.initialBalance') || 'Saldo Inicial' }}
          </h3>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-600 dark:text-green-400" viewBox="0 0 20 20" fill="currentColor">
            <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd" />
          </svg>
        </div>
        <p class="text-lg sm:text-xl font-bold text-green-600 dark:text-green-400">
          {{ formatCurrency(initialBalance) }}
        </p>
      </div>

      <!-- Current Balance -->
      <div class="bg-blue-50 dark:bg-blue-900/30 p-3 rounded-lg border border-blue-200 dark:border-blue-800">
        <div class="flex items-center justify-between mb-1">
          <h3 class="text-xs font-medium text-blue-800 dark:text-blue-200">
            {{ t('app.views.cashRegister.currentBalance') || 'Saldo Actual' }}
          </h3>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-blue-600 dark:text-blue-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v4a2 2 0 002 2V6h10a2 2 0 00-2-2H4zm2 6a2 2 0 012-2h8a2 2 0 012 2v4a2 2 0 01-2 2H8a2 2 0 01-2-2v-4zm6 4a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd" />
          </svg>
        </div>
        <p class="text-lg sm:text-xl font-bold text-blue-600 dark:text-blue-400">
          {{ formatCurrency(currentBalance) }}
        </p>
      </div>
    </div>

    <!-- Segunda fila: Ventas -->
    <div class="grid grid-cols-2 gap-2 sm:gap-3">
      <!-- Sales Amount -->
      <div class="bg-emerald-50 dark:bg-emerald-900/30 p-3 rounded-lg border border-emerald-200 dark:border-emerald-800">
        <div class="flex items-center justify-between mb-1">
          <h3 class="text-xs font-medium text-emerald-800 dark:text-emerald-200">
            {{ t('app.views.cashRegister.salesAmount') || 'Monto de Ventas' }}
          </h3>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-emerald-600 dark:text-emerald-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clip-rule="evenodd" />
          </svg>
        </div>
        <p class="text-lg sm:text-xl font-bold text-emerald-600 dark:text-emerald-400">
          {{ formatCurrency(salesAmount) }}
        </p>
      </div>

      <!-- Sales Count -->
      <div class="bg-teal-50 dark:bg-teal-900/30 p-3 rounded-lg border border-teal-200 dark:border-teal-800">
        <div class="flex items-center justify-between mb-1">
          <h3 class="text-xs font-medium text-teal-800 dark:text-teal-200">
            {{ t('app.views.cashRegister.salesCount') || 'Transacciones de Venta' }}
          </h3>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-teal-600 dark:text-teal-400" viewBox="0 0 20 20" fill="currentColor">
            <path d="M3 1a1 1 0 000 2h1.22l.305 1.222a.997.997 0 00.01.042l1.358 5.43-.893.892C3.74 11.846 4.632 14 6.414 14H15a1 1 0 000-2H6.414l1-1H14a1 1 0 00.894-.553l3-6A1 1 0 0017 3H6.28l-.31-1.243A1 1 0 005 1H3zM16 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM6.5 18a1.5 1.5 0 100-3 1.5 1.5 0 000 3z" />
          </svg>
        </div>
        <p class="text-lg sm:text-xl font-bold text-teal-600 dark:text-teal-400">
          {{ salesCount }}
        </p>
      </div>
    </div>

    <!-- Tercera fila: Gastos -->
    <div class="grid grid-cols-2 gap-2 sm:gap-3">
      <!-- Total Expenses -->
      <div class="bg-amber-50 dark:bg-amber-900/30 p-3 rounded-lg border border-amber-200 dark:border-amber-800">
        <div class="flex items-center justify-between mb-1">
          <h3 class="text-xs font-medium text-amber-800 dark:text-amber-200">
            {{ t('app.views.cashRegister.totalExpenses') || 'Gastos Totales' }}
          </h3>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-amber-600 dark:text-amber-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v3.586L7.707 9.293a1 1 0 00-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 10.586V7z" clip-rule="evenodd" />
          </svg>
        </div>
        <p class="text-lg sm:text-xl font-bold text-amber-600 dark:text-amber-400">
          {{ formatCurrency(totalExpenses) }}
        </p>
      </div>

      <!-- Expenses Count -->
      <div class="bg-orange-50 dark:bg-orange-900/30 p-3 rounded-lg border border-orange-200 dark:border-orange-800">
        <div class="flex items-center justify-between mb-1">
          <h3 class="text-xs font-medium text-orange-800 dark:text-orange-200">
            {{ t('app.views.cashRegister.expensesCount') || 'Transacciones de Gastos' }}
          </h3>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-orange-600 dark:text-orange-400" viewBox="0 0 20 20" fill="currentColor">
            <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
            <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm9.707 5.707a1 1 0 00-1.414-1.414L9 12.586l-1.293-1.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
        </div>
        <p class="text-lg sm:text-xl font-bold text-orange-600 dark:text-orange-400">
          {{ expensesCount }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { formatCurrency } from '@/utils/priceHelpers';

const { t } = useI18n();

defineProps<{
  initialBalance: number;
  currentBalance: number;
  salesAmount: number;
  salesCount: number;
  totalExpenses: number;
  expensesCount: number;
}>();
</script>
