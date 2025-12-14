<template>
  <div :class="[
    showBorder ? 'bg-blue-50 dark:bg-blue-900/30 p-3 rounded-md border border-blue-200 dark:border-blue-800' : ''
  ]">
    <h3 v-if="title" class="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
      {{ title }}
    </h3>
    <div v-if="isLoading" class="flex items-center justify-center py-2">
      <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
      <span class="ml-2 text-sm text-blue-600 dark:text-blue-400">{{ t('app.views.cashRegister.loading') }}</span>
    </div>
    <div v-else-if="cutData" class="space-y-2">
      <div class="grid grid-cols-2 gap-3">
        <div>
          <p class="text-xl font-bold text-blue-700 dark:text-blue-300">
            {{ formatCurrency(cutData.net_cash_flow || 0) }}
          </p>
          <p class="text-xs text-gray-600 dark:text-gray-400">
            {{ formatDate(cutData.generated_at || cutData.created_at) }}
          </p>
        </div>
        <div class="text-right">
          <p class="text-sm text-gray-700 dark:text-gray-300">
            {{ t('app.views.cashRegister.sessionNumber') }} #{{ cutData.session_id }}
          </p>
          <p class="text-xs text-gray-600 dark:text-gray-400">
            {{ cutData.total_transactions || 0 }} {{ t('app.views.cashRegister.transactions') }}
          </p>
        </div>
      </div>

      <!-- Payment Breakdown -->
      <div class="border-t border-blue-200 dark:border-blue-800 pt-2">
        <h4 class="text-sm font-medium text-blue-900 dark:text-blue-100 mb-1">
          {{ t('app.views.cashRegister.paymentBreakdown') }}
        </h4>
        <div class="flex flex-col text-sm space-y-0.5">
          <div v-if="cutData.payment_breakdown?.cash !== undefined || cutData.cash_payments !== undefined"
            class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">{{ t('app.views.cashRegister.cash') }}:</span>
            <span class="font-medium text-gray-900 dark:text-gray-100">{{ formatCurrency(cutData.payment_breakdown?.cash || cutData.cash_payments || 0) }}</span>
          </div>
          <div v-if="cutData.payment_breakdown?.card !== undefined || cutData.card_payments !== undefined"
            class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">{{ t('app.views.cashRegister.card') }}:</span>
            <span class="font-medium text-gray-900 dark:text-gray-100">{{ formatCurrency(cutData.payment_breakdown?.card || cutData.card_payments || 0) }}</span>
          </div>
          <div v-if="cutData.payment_breakdown?.digital !== undefined" class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">{{ t('app.views.cashRegister.digital') }}:</span>
            <span class="font-medium text-gray-900 dark:text-gray-100">{{ formatCurrency(cutData.payment_breakdown?.digital || 0) }}</span>
          </div>
          <div v-if="cutData.payment_breakdown?.other !== undefined" class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">{{ t('app.views.cashRegister.other') }}:</span>
            <span class="font-medium text-gray-900 dark:text-gray-100">{{ formatCurrency(cutData.payment_breakdown?.other || 0) }}</span>
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
            <span class="font-medium text-gray-900 dark:text-gray-100">{{ formatCurrency(cutData.total_sales || 0) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600 dark:text-gray-400">{{ t('app.views.cashRegister.totalExpenses') }}:</span>
            <span class="font-medium text-red-600 dark:text-red-400">{{ formatCurrency(cutData.total_expenses || 0) }}</span>
          </div>
        </div>
      </div>
    </div>
    <p v-else class="text-gray-600 dark:text-gray-400">
      {{ emptyMessage || t('app.views.cashRegister.noLastCut') }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { formatCurrency } from '@/utils/priceHelpers'

const formatDate = (dateString: string | null | undefined): string => {
  if (!dateString) return 'N/A';
  try {
    const date = new Date(dateString);
    return date.toLocaleString('es-MX', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return 'N/A';
  }
}

interface Props {
  cutData?: any
  isLoading?: boolean
  title?: string
  emptyMessage?: string
  showBorder?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  cutData: null,
  isLoading: false,
  title: '',
  emptyMessage: '',
  showBorder: true
})

const { t } = useI18n()
</script>
