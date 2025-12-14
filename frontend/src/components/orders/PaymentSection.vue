<template>
  <div v-if="!isEditMode && canProcessPayments">
    <div v-if="!hideTitle" class="flex items-center justify-between mb-3">
      <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100">
        {{ $t('app.views.orders.payment.title') || 'Payment' }}
      </h4>
      <button
        type="button"
        @click="!disableToggle && $emit('update:mark-as-paid', !markAsPaid)"
        class="relative inline-flex h-6 w-11 flex-shrink-0 rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
        :class="[
          markAsPaid ? 'bg-indigo-600' : 'bg-gray-200 dark:bg-gray-700',
          disableToggle ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
        ]"
        role="switch"
        :aria-checked="markAsPaid"
        :disabled="disableToggle"
      >
        <span class="sr-only">{{ $t('app.views.orders.payment.mark_as_paid') || 'Mark as paid' }}</span>
        <span
          :class="markAsPaid ? 'translate-x-5' : 'translate-x-0'"
          class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
        />
      </button>
    </div>
    
    <!-- Toggle when title is hidden -->
    <div v-else class="flex items-center justify-end mb-3">
      <button
        type="button"
        @click="!disableToggle && $emit('update:mark-as-paid', !markAsPaid)"
        class="relative inline-flex h-6 w-11 flex-shrink-0 rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
        :class="[
          markAsPaid ? 'bg-indigo-600' : 'bg-gray-200 dark:bg-gray-700',
          disableToggle ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
        ]"
        role="switch"
        :aria-checked="markAsPaid"
        :disabled="disableToggle"
      >
        <span class="sr-only">{{ $t('app.views.orders.payment.mark_as_paid') || 'Mark as paid' }}</span>
        <span
          :class="markAsPaid ? 'translate-x-5' : 'translate-x-0'"
          class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out"
        />
      </button>
    </div>
    
    <!-- Payment Method Selection -->
    <div v-if="markAsPaid" class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <h5 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">
        {{ $t('app.views.orders.payment.select_method') || 'Select Payment Method' }}
      </h5>
      <div class="grid grid-cols-2 gap-3">
        <button
          v-for="method in paymentMethods"
          :key="method.value"
          type="button"
          class="flex items-center justify-center gap-2 px-4 py-3 rounded-md border-2 transition-all"
          :class="selectedPaymentMethod === method.value 
            ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20 text-indigo-700 dark:text-indigo-300' 
            : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:border-indigo-300 dark:hover:border-indigo-600'"
          @click="$emit('update:selected-payment-method', method.value as 'cash' | 'card' | 'digital' | 'other')"
        >
          <component :is="method.icon" class="h-5 w-5" />
          <span class="font-medium">{{ method.label }}</span>
        </button>
      </div>

      <!-- Cash Change Calculator -->
      <div v-if="selectedPaymentMethod === 'cash'" class="mt-4 space-y-3">
        <div class="bg-white dark:bg-gray-900 p-3 rounded-lg border border-gray-200 dark:border-gray-700">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ $t('app.views.orders.payment.amount_received') || 'Monto Recibido' }}
          </label>
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 dark:text-gray-400">$</span>
            <input
              ref="cashReceivedInput"
              v-model.number="cashReceived"
              type="number"
              step="0.01"
              min="0"
              class="block w-full pl-7 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-sm"
              :placeholder="orderTotal.toFixed(2)"
            />
          </div>
        </div>
        
        <!-- Total and Change Display -->
        <div class="grid grid-cols-2 gap-3">
          <div class="bg-indigo-50 dark:bg-indigo-900/20 p-3 rounded-lg border border-indigo-200 dark:border-indigo-800">
            <p class="text-xs text-indigo-600 dark:text-indigo-400 font-medium mb-1">
              {{ $t('app.views.orders.payment.total_to_pay') || 'Total a Pagar' }}
            </p>
            <p class="text-lg font-bold text-indigo-900 dark:text-indigo-100">
              ${{ orderTotal.toFixed(2) }}
            </p>
          </div>
          <div class="p-3 rounded-lg border" :class="changeAmount >= 0 ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'">
            <p class="text-xs font-medium mb-1" :class="changeAmount >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
              {{ changeAmount >= 0 ? ($t('app.views.orders.payment.change') || 'Cambio') : ($t('app.views.orders.payment.insufficient') || 'Falta') }}
            </p>
            <p class="text-lg font-bold" :class="changeAmount >= 0 ? 'text-green-900 dark:text-green-100' : 'text-red-900 dark:text-red-100'">
              ${{ Math.abs(changeAmount).toFixed(2) }}
            </p>
          </div>
        </div>
        
        <!-- Insufficient amount warning -->
        <div v-if="changeAmount < 0" class="flex items-start gap-2 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <svg class="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p class="text-xs text-red-700 dark:text-red-300">
            {{ $t('app.views.orders.payment.insufficient_warning') || 'El monto recibido es insuficiente para completar el pago' }}
          </p>
        </div>
      </div>

      <p class="mt-3 text-xs text-gray-500 dark:text-gray-400">
        {{ $t('app.views.orders.payment.paid_order_warning') || 'Note: Paid orders cannot be edited.' }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { 
  BanknotesIcon, 
  CreditCardIcon, 
  DevicePhoneMobileIcon, 
  EllipsisHorizontalIcon 
} from '@heroicons/vue/24/outline';

interface Props {
  isEditMode: boolean;
  canProcessPayments: boolean;
  markAsPaid: boolean;
  selectedPaymentMethod: 'cash' | 'card' | 'digital' | 'other';
  orderTotal: number;
  cashReceived?: number;
  disableToggle?: boolean;
  hideTitle?: boolean;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'update:mark-as-paid': [value: boolean];
  'update:selected-payment-method': [value: 'cash' | 'card' | 'digital' | 'other'];
  'update:cash-received': [value: number];
}>();

const paymentMethods = [
  { value: 'cash', label: 'Efectivo', icon: BanknotesIcon },
  { value: 'card', label: 'Tarjeta', icon: CreditCardIcon },
  { value: 'digital', label: 'Digital', icon: DevicePhoneMobileIcon },
  { value: 'other', label: 'Otro', icon: EllipsisHorizontalIcon }
];

// Cash change calculator
const cashReceived = ref<number>(props.cashReceived || 0);
const cashReceivedInput = ref<HTMLInputElement | null>(null);

const changeAmount = computed(() => {
  return cashReceived.value - props.orderTotal;
});

// Focus on cash received input
function focusCashInput() {
  if (cashReceivedInput.value) {
    cashReceivedInput.value.focus();
    cashReceivedInput.value.select();
  }
}

// Blur cash received input
function blurCashInput() {
  if (cashReceivedInput.value) {
    cashReceivedInput.value.blur();
  }
}

// Emit changes to parent
watch(cashReceived, (newValue) => {
  emit('update:cash-received', newValue);
});

// Sync local state when prop changes from parent (e.g., form reset)
watch(() => props.cashReceived, (newValue) => {
  cashReceived.value = newValue || 0;
});

// Reset cash received when payment method changes
watch(() => props.selectedPaymentMethod, (newMethod) => {
  if (newMethod !== 'cash') {
    cashReceived.value = 0;
  }
});

// Reset when mark as paid is toggled off
watch(() => props.markAsPaid, (newValue) => {
  if (!newValue) {
    cashReceived.value = 0;
  }
});

// Expose focus and blur functions
defineExpose({
  focusCashInput,
  blurCashInput
});
</script>
