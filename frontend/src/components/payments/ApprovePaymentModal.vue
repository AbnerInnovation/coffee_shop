<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto" @click.self="$emit('close')">
    <div class="flex items-center justify-center min-h-screen px-4">
      <div class="fixed inset-0 bg-black/60 backdrop-blur-sm" @click="$emit('close')"></div>
      
      <div class="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          {{ t('app.pending_payments.approve_title') }}
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
          {{ t('app.pending_payments.approve_confirm') }} <strong>${{ formatMoney(payment?.amount || 0) }}</strong> 
          {{ t('app.pending_payments.approve_for') }} {{ payment?.restaurant_name }}?
        </p>
        <div class="flex gap-3">
          <button
            @click="$emit('close')"
            class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            {{ t('app.pending_payments.cancel') }}
          </button>
          <button
            @click="$emit('confirm')"
            :disabled="processing"
            class="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
          >
            {{ processing ? t('app.pending_payments.processing') : t('app.pending_payments.confirm') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import type { Payment } from '@/composables/usePendingPayments';

const { t } = useI18n();

interface Props {
  show: boolean;
  payment: Payment | null;
  processing?: boolean;
}

withDefaults(defineProps<Props>(), {
  processing: false
});

defineEmits<{
  'close': [];
  'confirm': [];
}>();

const formatMoney = (amount: number) => {
  return amount.toLocaleString('es-MX', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};
</script>
