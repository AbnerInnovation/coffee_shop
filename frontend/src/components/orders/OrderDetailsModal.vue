<template>
  <TransitionRoot as="template" :show="open">
    <Dialog as="div" class="relative z-10" @close="handleClose">
      <TransitionChild
        as="template"
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div :class="backdropClasses" />
      </TransitionChild>

      <div class="fixed inset-0 z-10 overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild
            as="template"
            enter="ease-out duration-300"
            enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          >
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl sm:p-6">
              <div>
                <div class="flex items-center justify-between">
                  <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900 dark:text-gray-100">
                    {{$t('app.views.orders.modals.details.order_title', { id: order.id })}}
                  </DialogTitle>
                  <div class="flex items-center space-x-2">
                    <span 
                      class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
                      :class="getStatusBadgeClass(order.status)"
                    >
                      {{ order.status }}
                    </span>
                    <span
                      class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
                      :class="order.is_paid ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'"
                    >
                      {{ order.is_paid ? $t('app.views.orders.payment.paid') : $t('app.views.orders.payment.pending') }}
                    </span>
                    <button
                      type="button"
                      class="rounded-md bg-white dark:bg-transparent text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                      @click="$emit('close')"
                    >
                      <span class="sr-only">{{$t('app.views.orders.modals.details.close')}}</span>
                      <XMarkIcon class="h-6 w-6" aria-hidden="true" />
                    </button>
                  </div>
                </div>
                
                <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">{{$t('app.views.orders.modals.details.table')}}</h4>
                    <p class="mt-1 text-sm text-gray-900 dark:text-gray-100">{{ order.table_number || $t('app.views.orders.modals.details.takeaway') }}</p>
                  </div>
                  <div>
                    <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">{{$t('app.views.orders.modals.details.order_time')}}</h4>
                    <p class="mt-1 text-sm text-gray-900 dark:text-gray-100">{{ formatDateTime(order.createdAt) }}</p>
                  </div>
                  <div>
                    <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">{{$t('app.views.orders.modals.details.customer')}}</h4>
                    <p class="mt-1 text-sm text-gray-900 dark:text-gray-100">{{ order.customer_name || $t('app.views.orders.modals.details.no_name') }}</p>
                  </div>
                </div>
                
                <div class="mt-6">
                  <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">{{$t('app.views.orders.modals.details.order_items')}}</h4>
                  <div class="mt-2 overflow-hidden border border-gray-200 dark:border-gray-800 rounded-lg">
                    <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-800">
                      <thead class="bg-gray-50 dark:bg-gray-800">
                        <tr>
                          <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{$t('app.views.orders.modals.details.headers.item')}}</th>
                          <th scope="col" class="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{$t('app.views.orders.modals.details.headers.qty')}}</th>
                          <th scope="col" class="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{$t('app.views.orders.modals.details.headers.price')}}</th>
                          <th scope="col" class="px-4 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{$t('app.views.orders.modals.details.headers.total')}}</th>
                        </tr>
                      </thead>
                      <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
                        <tr v-for="item in order.items" :key="item.id">
                          <td class="px-4 py-3 text-sm text-gray-900 dark:text-gray-100">
                            <div class="font-medium text-gray-900 dark:text-gray-100">{{ item.name }}</div>
                            <div v-if="item.variant" class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                              {{ item.variant.name }}
                            </div>
                            <div v-if="item.notes" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                              <span class="font-medium">{{$t('app.views.orders.modals.details.note')}}</span> {{ item.notes }}
                            </div>
                            <div v-if="item.special_instructions" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                              <span class="font-medium">{{$t('app.views.orders.modals.details.special_instructions')}}</span> {{ item.special_instructions }}
                            </div>
                          </td>
                          <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 text-right">
                            {{ item.quantity }}
                          </td>
                          <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 text-right">
                            ${{ (item.unit_price || 0).toFixed(2) }}
                          </td>
                          <td class="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100 text-right">
                            ${{ (item.quantity * (item.price || item.unit_price || 0)).toFixed(2) }}
                          </td>
                        </tr>
                      </tbody>
                      <tfoot>
                        <tr>
                          <td colspan="3" class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 text-right">
                            {{$t('app.views.orders.modals.details.subtotal')}}
                          </td>
                          <td class="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100 text-right">
                            ${{ (order.subtotal || 0).toFixed(2) }}
                          </td>
                        </tr>
                        <tr v-if="(order.tax || 0) > 0">
                          <td colspan="3" class="px-4 py-1 text-sm text-gray-500 dark:text-gray-400 text-right">
                            {{$t('app.views.orders.modals.details.tax', { rate: ((order.taxRate || 0) * 100).toFixed(1) })}}
                          </td>
                          <td class="px-4 py-1 text-sm text-gray-500 dark:text-gray-400 text-right">
                            ${{ (order.tax || 0).toFixed(2) }}
                          </td>
                        </tr>
                        <tr>
                          <td colspan="3" class="px-4 py-3 text-base font-bold text-gray-900 dark:text-white text-right">
                            {{$t('app.views.orders.modals.details.total')}}
                          </td>
                          <td class="px-4 py-3 text-base font-bold text-gray-900 dark:text-white text-right">
                            ${{ (order.total || 0).toFixed(2) }}
                          </td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                </div>
                
                <div v-if="order.notes" class="mt-4">
                  <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">{{$t('app.views.orders.modals.details.order_notes')}}</h4>
                  <p class="mt-1 text-sm text-gray-900 dark:text-gray-100">{{ order.notes }}</p>
                </div>
                
                <!-- Payment Method Selection -->
                <div v-if="!order.is_paid && order.status !== 'cancelled' && showPaymentMethodSelector" class="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                  <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">{{$t('app.views.orders.payment.select_method') || 'Select Payment Method'}}</h4>
                  <div class="grid grid-cols-2 gap-3">
                    <button
                      v-for="method in paymentMethods"
                      :key="method.value"
                      type="button"
                      class="flex items-center justify-center gap-2 px-4 py-3 rounded-md border-2 transition-all"
                      :class="selectedPaymentMethod === method.value 
                        ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20 text-indigo-700 dark:text-indigo-300' 
                        : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:border-indigo-300 dark:hover:border-indigo-600'"
                      @click="selectedPaymentMethod = method.value"
                    >
                      <component :is="method.icon" class="h-5 w-5" />
                      <span class="font-medium">{{ method.label }}</span>
                    </button>
                  </div>
                </div>
                
                <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-3 sm:gap-3">
                  <button
                    type="button"
                    class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:col-start-1 sm:text-sm dark:bg-gray-800 dark:text-gray-200 dark:border-gray-700 dark:hover:bg-gray-700"
                    @click="emit('edit-order', order)"
                  >
                    {{$t('app.forms.edit')}}
                  </button>
                  <button
                    v-if="!order.is_paid && order.status !== 'cancelled'"
                    type="button"
                    class="inline-flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:col-start-2 sm:text-sm"
                    @click="showPaymentMethodSelector ? completePayment() : showPaymentMethodSelector = true"
                  >
                    {{showPaymentMethodSelector ? $t('app.views.orders.payment.confirm_payment') || 'Confirm Payment' : $t('app.views.orders.modals.details.complete_payment') || 'Complete Payment'}}
                  </button>
                  <button
                    v-if="order.status === 'Preparing'"
                    type="button"
                    class="inline-flex w-full justify-center rounded-md border border-transparent bg-green-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 sm:col-start-2 sm:text-sm"
                    @click="updateStatus('Ready')"
                  >
                    {{$t('app.views.orders.modals.details.mark_ready')}}
                  </button>
                  <button
                    v-else-if="order.status === 'ready'"
                    type="button"
                    class="inline-flex w-full justify-center rounded-md border border-transparent bg-green-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 sm:col-start-2 sm:text-sm"
                    @click="updateStatus('completed')"
                  >
                    {{$t('app.views.orders.modals.details.mark_completed')}}
                  </button>
                  <button
                    type="button"
                    class="mt-3 inline-flex w-full justify-center rounded-md border border-gray-300 bg-white dark:bg-gray-800 px-4 py-2 text-base font-medium text-gray-700 dark:text-gray-200 shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:col-start-1 sm:mt-0 sm:text-sm dark:border-gray-700"
                    @click="printOrder"
                  >
                    {{$t('app.views.orders.modals.details.print_receipt')}}
                  </button>
                </div>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue'
import { XMarkIcon, BanknotesIcon, CreditCardIcon, DevicePhoneMobileIcon, EllipsisHorizontalIcon } from '@heroicons/vue/24/outline'
import orderService from '@/services/orderService'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import { useTheme } from '@/composables/useTheme'

const props = defineProps({
  open: {
    type: Boolean,
    required: true
  },
  order: {
    type: Object,
    required: true,
    default: () => ({
      id: '',
      status: '',
      customerName: '',
      table: '',
      type: 'Dine-in',
      createdAt: new Date(),
      items: [],
      subtotal: 0,
      tax: 0,
      taxRate: 0.1,
      total: 0,
      notes: ''
    })
  }
});

const emit = defineEmits(['close', 'status-update', 'paymentCompleted', 'openCashRegister']);

const { confirm } = useConfirm();
const { showSuccess, showError } = useToast();
const { t } = useI18n();
const isMounted = ref(false);

// Watch for confirmation dialog state
const { isOpen: isConfirmOpen } = useConfirm();

// Computed property for backdrop classes
const backdropClasses = computed(() => [
  'fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity',
  isConfirmOpen.value ? 'pointer-events-none' : ''
]);

onMounted(() => {
  isMounted.value = true;
});

const handleClose = () => {
  if (isMounted.value) {
    emit('close');
  }
};

// Calculate totals if needed
const orderWithTotals = computed(() => {
  // If total_amount is already calculated, use it
  if (props.order.total_amount > 0) return props.order;

  // Otherwise calculate from items
  const subtotal = props.order.items.reduce((sum, item) => {
    return sum + (item.quantity * item.unit_price);
  }, 0);

  // Assuming 10% tax for example
  const tax = subtotal * 0.1;
  const total = subtotal + tax;

  return {
    ...props.order,
    subtotal,
    tax,
    total_amount: total
  };
});

function getStatusBadgeClass(status) {
  const statusClasses = {
    'Pending': 'bg-yellow-100 text-yellow-800',
    'Preparing': 'bg-blue-100 text-blue-800',
    'Ready': 'bg-green-100 text-green-800',
    'Completed': 'bg-gray-100 text-gray-800',
    'Cancelled': 'bg-red-100 text-red-800',
  };
  return statusClasses[status] || 'bg-gray-100 text-gray-800';
}

function formatDateTime(date) {
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function updateStatus(newStatus) {
  emit('status-update', {
    orderId: props.order.id,
    status: newStatus
  });
  emit('close');
}

async function cancelOrder() {
  const confirmed = await confirm({
    title: 'Cancel Order',
    message: 'Are you sure you want to cancel this order? This action cannot be undone.',
    confirmText: 'Yes, cancel order',
    cancelText: 'No, keep it',
    confirmClass: 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
  });

  if (confirmed) {
    updateStatus('Cancelled');
  }
}

function printOrder() {
  // In a real app, this would open a print dialog with a formatted receipt
  window.print();
}

const showPaymentMethodSelector = ref(false)
const selectedPaymentMethod = ref<'cash' | 'card' | 'digital' | 'other'>('cash')

const paymentMethods = [
  { value: 'cash', label: t('app.views.cashRegister.cash') || 'Cash', icon: BanknotesIcon },
  { value: 'card', label: t('app.views.cashRegister.card') || 'Card', icon: CreditCardIcon },
  { value: 'digital', label: t('app.views.cashRegister.digital') || 'Digital', icon: DevicePhoneMobileIcon },
  { value: 'other', label: t('app.views.cashRegister.other') || 'Other', icon: EllipsisHorizontalIcon }
]

async function completePayment() {
  try {
    await orderService.markOrderPaid(props.order.id, selectedPaymentMethod.value);
    emit('paymentCompleted', props.order);
    emit('close');
    showPaymentMethodSelector.value = false;
  } catch (e) {
    console.error('Failed to complete payment:', e);
    console.log('Full error object:', e);
    console.log('Error response:', e.response);
    console.log('Error response data:', e.response?.data);

    // Handle specific cash register session error
    const errorDetail = e.response?.data?.detail || '';
    console.log('Error detail:', errorDetail);

    if (errorDetail.includes('No open cash register session found') || errorDetail.includes('cash register session')) {
      const openSession = await confirm(
        t('app.views.cashRegister.cashRegisterSessionRequiredTitle'),
        t('app.views.cashRegister.cashRegisterSessionRequiredMessage'),
        t('app.views.cashRegister.openCashRegisterButton'),
        t('app.views.cashRegister.cancelPaymentButton'),
        'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500'
      );

      if (openSession) {
        emit('openCashRegister');
      }
    } else {
      // Show generic error for other payment failures
      showError(errorDetail || t('app.views.cashRegister.paymentFailedGeneric'));
    }
  }
}
</script>
