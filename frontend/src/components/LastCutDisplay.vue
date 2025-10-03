<template>
  <div class="bg-orange-50 dark:bg-orange-900 p-4 rounded-md">
    <h3 class="text-lg font-medium text-orange-800 dark:text-orange-200">
      {{ t('app.views.cashRegister.lastCut') || 'Last Cut' }}
    </h3>
    <div v-if="isLoading" class="flex items-center justify-center py-2">
      <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-orange-600"></div>
      <span class="ml-2 text-orange-600 dark:text-orange-400">{{ t('app.views.cashRegister.loading') ||
        'Loading...' }}</span>
    </div>
    <div v-else-if="lastCut" class="space-y-3">
      <div class="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p class="text-lg font-bold text-orange-600 dark:text-orange-400">
            ${{ lastCut.net_cash_flow?.toFixed(2) || '0.00' }}
          </p>
          <p class="text-xs text-orange-500 dark:text-orange-300">
            {{ formatDate(lastCut.created_at) }}
          </p>
        </div>
        <div class="text-right">
          <p class="text-sm text-orange-600 dark:text-orange-400">
            Session #{{ lastCut.session_id }}
          </p>
          <p class="text-sm text-orange-600 dark:text-orange-400">
            {{ lastCut.total_transactions || 0 }} transactions
          </p>
        </div>
      </div>

      <!-- Payment Breakdown -->
      <div class="border-t border-orange-200 dark:border-orange-800 pt-2">
        <h4 class="text-sm font-medium text-orange-800 dark:text-orange-200 mb-2">
          {{ t('app.views.cashRegister.paymentBreakdown') || 'Payment Breakdown' }}
        </h4>
        <div class="flex flex-col text-xs">
          <div v-if="lastCut.payment_breakdown?.cash !== undefined || lastCut.cash_payments !== undefined"
            class="flex justify-between">
            <span class="text-orange-600 dark:text-orange-300">{{ t('app.views.cashRegister.cash') || 'Cash'
              }}:</span>
            <span class="font-medium">${{ (lastCut.payment_breakdown?.cash || lastCut.cash_payments ||
              0).toFixed(2) }}</span>
          </div>
          <div v-if="lastCut.payment_breakdown?.card !== undefined || lastCut.card_payments !== undefined"
            class="flex justify-between">
            <span class="text-orange-600 dark:text-orange-300">{{ t('app.views.cashRegister.card') || 'Card'
              }}:</span>
            <span class="font-medium">${{ (lastCut.payment_breakdown?.card || lastCut.card_payments ||
              0).toFixed(2) }}</span>
          </div>
          <div v-if="lastCut.payment_breakdown?.digital !== undefined" class="flex justify-between">
            <span class="text-orange-600 dark:text-orange-300">{{ t('app.views.cashRegister.digital') ||
              'Digital' }}:</span>
            <span class="font-medium">${{ (lastCut.payment_breakdown?.digital || 0).toFixed(2) }}</span>
          </div>
          <div v-if="lastCut.payment_breakdown?.other !== undefined" class="flex justify-between">
            <span class="text-orange-600 dark:text-orange-300">{{ t('app.views.cashRegister.other') || 'Other'
              }}:</span>
            <span class="font-medium">${{ (lastCut.payment_breakdown?.other || 0).toFixed(2) }}</span>
          </div>
        </div>
      </div>

      <!-- Transaction Summary -->
      <div class="border-t border-orange-200 dark:border-orange-800 pt-2">
        <h4 class="text-sm font-medium text-orange-800 dark:text-orange-200 mb-2">
          {{ t('app.views.cashRegister.transactionSummary') || 'Transaction Summary' }}
        </h4>
        <div class="grid grid-cols-2 gap-2 text-xs">
          <div class="flex justify-between">
            <span class="text-orange-600 dark:text-orange-300">{{ t('app.views.cashRegister.totalSales') ||
              'Sales' }}:</span>
            <span class="font-medium">${{ (lastCut.total_sales || 0).toFixed(2) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-orange-600 dark:text-orange-300">{{ t('app.views.cashRegister.totalRefunds') ||
              'Refunds' }}:</span>
            <span class="font-medium">${{ (lastCut.total_refunds || 0).toFixed(2) }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-orange-600 dark:text-orange-300">{{ t('app.views.cashRegister.totalTips') ||
              'Tips' }}:</span>
            <span class="font-medium">${{ (lastCut.total_tips || 0).toFixed(2) }}</span>
          </div>
        </div>
      </div>
    </div>
    <p v-else class="text-orange-600 dark:text-orange-400">
      {{ t('app.views.cashRegister.noLastCut') || 'No cuts yet' }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

interface Props {
  lastCut?: any
  isLoading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  lastCut: null,
  isLoading: false
})

const { t } = useI18n()

const formatDate = (dateString: string) => {
  if (!dateString) return 'No date'
  try {
    return new Date(dateString).toLocaleString()
  } catch (error) {
    console.error('Error formatting date:', dateString, error)
    return 'Invalid date'
  }
}
</script>
