<template>
  <div class="bg-blue-50 dark:bg-blue-900/30 p-3 rounded-md border border-blue-200 dark:border-blue-800">
    <h3 class="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
      {{ t('app.views.cashRegister.lastCut') }}
    </h3>
    <div v-if="isLoading" class="flex items-center justify-center py-2">
      <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
      <span class="ml-2 text-sm text-blue-600 dark:text-blue-400">{{ t('app.views.cashRegister.loading') }}</span>
    </div>
    <div v-else-if="lastCut" class="space-y-2">
      <div class="grid grid-cols-2 gap-3">
        <div>
          <p class="text-xl font-bold text-blue-700 dark:text-blue-300">
            {{ formatCurrency(lastCut.net_cash_flow || 0) }}
          </p>
          <p class="text-xs text-gray-600 dark:text-gray-400">
            {{ formatDate(lastCut.created_at) }}
          </p>
        </div>
        <div class="text-right">
          <p class="text-sm text-gray-700 dark:text-gray-300">
            {{ t('app.views.cashRegister.sessionNumber') }} #{{ lastCut.session_id }}
          </p>
          <p class="text-xs text-gray-600 dark:text-gray-400">
            {{ lastCut.total_transactions || 0 }} {{ t('app.views.cashRegister.transactions') }}
          </p>
        </div>
      </div>

      <!-- Payment Breakdown -->
      <div class="border-t border-blue-200 dark:border-blue-800 pt-2">
        <h4 class="text-sm font-medium text-blue-900 dark:text-blue-100 mb-1">
          {{ t('app.views.cashRegister.paymentBreakdown') }}
        </h4>
        <div class="flex flex-col text-sm space-y-0.5">
          <div v-if="lastCut.payment_breakdown?.cash !== undefined || lastCut.cash_payments !== undefined"
            class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">{{ t('app.views.cashRegister.cash') }}:</span>
            <span class="font-medium text-gray-900 dark:text-gray-100">{{ formatCurrency(lastCut.payment_breakdown?.cash || lastCut.cash_payments || 0) }}</span>
          </div>
          <div v-if="lastCut.payment_breakdown?.card !== undefined || lastCut.card_payments !== undefined"
            class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">{{ t('app.views.cashRegister.card') }}:</span>
            <span class="font-medium text-gray-900 dark:text-gray-100">{{ formatCurrency(lastCut.payment_breakdown?.card || lastCut.card_payments || 0) }}</span>
          </div>
          <div v-if="lastCut.payment_breakdown?.digital !== undefined" class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">{{ t('app.views.cashRegister.digital') }}:</span>
            <span class="font-medium text-gray-900 dark:text-gray-100">{{ formatCurrency(lastCut.payment_breakdown?.digital || 0) }}</span>
          </div>
          <div v-if="lastCut.payment_breakdown?.other !== undefined" class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">{{ t('app.views.cashRegister.other') }}:</span>
            <span class="font-medium text-gray-900 dark:text-gray-100">{{ formatCurrency(lastCut.payment_breakdown?.other || 0) }}</span>
          </div>
        </div>
      </div>

      <!-- Transaction Summary -->
      <div class="border-t border-blue-200 dark:border-blue-800 pt-2">
        <h4 class="text-sm font-medium text-blue-900 dark:text-blue-100 mb-1">
          {{ t('app.views.cashRegister.transactionSummary') }}
        </h4>
        <div class="grid grid-cols-2 gap-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">{{ t('app.views.cashRegister.totalSales') }}:</span>
            <span class="font-medium text-gray-900 dark:text-gray-100">{{ formatCurrency(lastCut.total_sales || 0) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">{{ t('app.views.cashRegister.totalRefunds') }}:</span>
            <span class="font-medium text-gray-900 dark:text-gray-100">{{ formatCurrency(lastCut.total_refunds || 0) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">{{ t('app.views.cashRegister.totalTips') }}:</span>
            <span class="font-medium text-gray-900 dark:text-gray-100">{{ formatCurrency(lastCut.total_tips || 0) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">{{ t('app.views.cashRegister.totalExpenses') }}:</span>
            <span class="font-medium text-red-600 dark:text-red-400">{{ formatCurrency(lastCut.total_expenses || 0) }}</span>
          </div>
        </div>
      </div>
    </div>
    <p v-else class="text-gray-600 dark:text-gray-400">
      {{ t('app.views.cashRegister.noLastCut') }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { formatDateTime as formatDate } from '@/utils/dateHelpers'
import { formatCurrency } from '@/utils/priceHelpers'

interface Props {
  lastCut?: any
  isLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  lastCut: null,
  isLoading: false
})

const { t } = useI18n()
</script>
