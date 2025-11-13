<template>
  <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
    <div class="p-4 sm:p-6">
      <div class="flex items-start justify-between">
        <!-- Payment Info -->
        <div class="flex-1">
          <div class="flex items-center gap-3 mb-2 flex-wrap">
            <h3 class="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">
              {{ payment.restaurant_name || `Restaurant #${payment.restaurant_id}` }}
            </h3>
            <span class="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
              {{ t('app.pending_payments.status_pending') }}
            </span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 mt-4">
            <div>
              <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">{{ t('app.pending_payments.plan') }}</p>
              <p class="text-sm font-medium text-gray-900 dark:text-white">
                {{ payment.plan_name || 'N/A' }}
              </p>
            </div>

            <div>
              <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">{{ t('app.pending_payments.amount') }}</p>
              <p class="text-lg font-bold text-gray-900 dark:text-white">
                ${{ formatMoney(payment.amount) }}
              </p>
            </div>

            <div>
              <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">{{ t('app.pending_payments.cycle') }}</p>
              <p class="text-sm font-medium text-gray-900 dark:text-white">
                {{ payment.billing_cycle === 'monthly' ? t('app.pending_payments.cycle_monthly') : t('app.pending_payments.cycle_annual') }}
              </p>
            </div>

            <div>
              <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">{{ t('app.pending_payments.reference') }}</p>
              <p class="text-sm font-mono font-medium text-gray-900 dark:text-white break-all">
                {{ payment.reference_number }}
              </p>
            </div>

            <div>
              <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">{{ t('app.pending_payments.payment_date') }}</p>
              <p class="text-sm font-medium text-gray-900 dark:text-white">
                {{ formatDate(payment.payment_date) }}
              </p>
            </div>

            <div>
              <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">{{ t('app.pending_payments.submitted') }}</p>
              <p class="text-sm font-medium text-gray-900 dark:text-white">
                {{ formatDate(payment.created_at) }}
              </p>
            </div>
          </div>

          <!-- Proof Image -->
          <div v-if="payment.proof_image_url" class="mt-4">
            <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mb-2">{{ t('app.pending_payments.proof') }}</p>
            <a 
              :href="payment.proof_image_url" 
              target="_blank"
              class="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 underline inline-flex items-center gap-1"
            >
              {{ t('app.pending_payments.view_proof') }}
              <ArrowTopRightOnSquareIcon class="h-3 w-3" />
            </a>
          </div>

          <!-- Notes -->
          <div v-if="payment.notes" class="mt-4">
            <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mb-1">{{ t('app.pending_payments.notes') }}</p>
            <p class="text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 p-3 rounded">
              {{ payment.notes }}
            </p>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="mt-6 flex flex-col sm:flex-row gap-3">
        <button
          @click="$emit('approve', payment)"
          class="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium flex items-center justify-center gap-2"
        >
          <CheckCircleIcon class="w-5 h-5" />
          {{ t('app.pending_payments.approve') }}
        </button>
        <button
          @click="$emit('reject', payment)"
          class="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium flex items-center justify-center gap-2"
        >
          <XCircleIcon class="w-5 h-5" />
          {{ t('app.pending_payments.reject') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { CheckCircleIcon, XCircleIcon, ArrowTopRightOnSquareIcon } from '@heroicons/vue/24/outline';
import type { Payment } from '@/composables/usePendingPayments';

const { t } = useI18n();

interface Props {
  payment: Payment;
}

defineProps<Props>();

defineEmits<{
  'approve': [payment: Payment];
  'reject': [payment: Payment];
}>();

const formatMoney = (amount: number) => {
  return amount.toLocaleString('es-MX', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};

const formatDate = (dateString: string | null) => {
  if (!dateString) return 'N/A';
  
  const date = new Date(dateString);
  return date.toLocaleDateString('es-MX', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};
</script>
