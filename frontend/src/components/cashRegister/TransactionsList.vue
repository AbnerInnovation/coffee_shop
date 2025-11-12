<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow">
    <div class="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
      <h2 class="text-base font-medium text-gray-900 dark:text-gray-100">
        {{ t('app.views.cashRegister.transactions') || 'Transactions' }}
      </h2>
    </div>
    
    <div v-if="transactions.length === 0" class="p-4 text-center">
      <p class="text-sm text-gray-500 dark:text-gray-400">
        {{ t('app.views.cashRegister.noTransactions') || 'No transactions yet.' }}
      </p>
    </div>
    
    <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
      <div 
        v-for="transaction in transactions" 
        :key="transaction.id" 
        class="px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
      >
        <div class="flex justify-between items-start gap-3">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 mb-0.5 flex-wrap">
              <p class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                {{ getDescription(transaction.description) }}
              </p>
              <span 
                v-if="transaction.payment_method" 
                class="px-1.5 py-0.5 text-xs font-medium rounded whitespace-nowrap"
                :class="getPaymentMethodBadgeClass(transaction.payment_method)"
              >
                {{ getPaymentMethod(transaction.payment_method) }}
              </span>
            </div>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              {{ formatDate(transaction.created_at) }}
            </p>
          </div>
          
          <div class="text-right flex-shrink-0">
            <p 
              class="text-base font-semibold whitespace-nowrap"
              :class="transaction.amount >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'"
            >
              {{ transaction.amount >= 0 ? '+' : '' }}{{ formatCurrency(Math.abs(transaction.amount) || 0) }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              {{ getTransactionType(transaction.transaction_type) }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { formatCurrency } from '@/utils/priceHelpers';
import {
  formatTransactionDate,
  translateDescription,
  translateTransactionType,
  translatePaymentMethod,
  getPaymentMethodBadgeClass,
  type Transaction
} from '@/utils/cashRegisterHelpers';

const { t } = useI18n();

defineProps<{
  transactions: Transaction[];
}>();

const formatDate = (dateString: string) => formatTransactionDate(dateString);
const getDescription = (description: string) => translateDescription(description, t);
const getTransactionType = (type: string) => translateTransactionType(type, t);
const getPaymentMethod = (method: string) => translatePaymentMethod(method, t);
</script>
