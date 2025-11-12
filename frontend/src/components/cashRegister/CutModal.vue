<template>
  <div v-if="isOpen" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
    <div class="w-full max-w-lg rounded-lg bg-white dark:bg-gray-900 p-6 shadow-lg">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
        {{ t('app.views.cashRegister.cutSession') || 'Cut Session' }}
      </h3>
      
      <div class="space-y-4">
        <!-- Summary -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100">
            {{ t('app.views.cashRegister.summary') || 'Summary' }}
          </h4>
          <div class="mt-2 space-y-2">
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-400">
                {{ t('app.views.cashRegister.totalSales') || 'Total Sales' }}
              </span>
              <span class="font-medium">{{ formatCurrency(report.total_sales || 0) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-400">
                {{ t('app.views.cashRegister.totalRefunds') || 'Total Refunds' }}
              </span>
              <span class="font-medium">{{ formatCurrency(report.total_refunds || 0) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-400">
                {{ t('app.views.cashRegister.totalTips') || 'Total Tips' }}
              </span>
              <span class="font-medium">{{ formatCurrency(report.total_tips || 0) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600 dark:text-gray-400">
                {{ t('app.views.cashRegister.totalExpenses') || 'Total Expenses' }}
              </span>
              <span class="font-medium text-red-600 dark:text-red-400">{{ formatCurrency(report.total_expenses || 0) }}</span>
            </div>
            <div class="flex justify-between font-bold">
              <span class="text-gray-900 dark:text-gray-100">
                {{ t('app.views.cashRegister.netCashFlow') || 'Net Cash Flow' }}
              </span>
              <span>{{ formatCurrency(report.net_cash_flow || 0) }}</span>
            </div>
          </div>
        </div>

        <!-- Payment Breakdown -->
        <div>
          <h4 class="font-medium text-gray-900 dark:text-gray-100">
            {{ t('app.views.cashRegister.paymentBreakdown') || 'Payment Breakdown' }}
          </h4>
          <div class="mt-2 space-y-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
                {{ t('app.views.cashRegister.cashPayments') || 'Cash Payments' }}
              </label>
              <input 
                v-model="localCash" 
                type="number" 
                step="0.01"
                class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
                {{ t('app.views.cashRegister.cardPayments') || 'Card Payments' }}
              </label>
              <input 
                v-model="localCard" 
                type="number" 
                step="0.01"
                class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
                {{ t('app.views.cashRegister.digitalPayments') || 'Digital Payments' }}
              </label>
              <input 
                v-model="localDigital" 
                type="number" 
                step="0.01"
                class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">
                {{ t('app.views.cashRegister.otherPayments') || 'Other Payments' }}
              </label>
              <input 
                v-model="localOther" 
                type="number" 
                step="0.01"
                class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>
        </div>
      </div>
      
      <div class="mt-6 flex justify-end space-x-3">
        <BaseButton type="button" variant="secondary" size="sm" @click="$emit('close')">
          {{ t('app.actions.cancel') || 'Cancel' }}
        </BaseButton>
        <BaseButton type="button" variant="info" size="sm" @click="handleSave">
          {{ t('app.actions.save') || 'Save' }}
        </BaseButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { formatCurrency } from '@/utils/priceHelpers';
import BaseButton from '@/components/ui/BaseButton.vue';
import type { CutReport } from '@/utils/cashRegisterHelpers';

const { t } = useI18n();

const props = defineProps<{
  isOpen: boolean;
  report: CutReport;
  cash: number;
  card: number;
  digital: number;
  other: number;
}>();

const emit = defineEmits<{
  close: [];
  save: [data: { cash: number; card: number; digital: number; other: number }];
}>();

const localCash = ref(props.cash);
const localCard = ref(props.card);
const localDigital = ref(props.digital);
const localOther = ref(props.other);

watch(() => props.cash, (newVal) => localCash.value = newVal);
watch(() => props.card, (newVal) => localCard.value = newVal);
watch(() => props.digital, (newVal) => localDigital.value = newVal);
watch(() => props.other, (newVal) => localOther.value = newVal);

const handleSave = () => {
  emit('save', {
    cash: localCash.value,
    card: localCard.value,
    digital: localDigital.value,
    other: localOther.value
  });
};
</script>
