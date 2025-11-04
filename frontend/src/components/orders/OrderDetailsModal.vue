<template>
  <TransitionRoot as="template" :show="open">
    <Dialog as="div" class="relative z-[10001]" @close="handleClose">
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

      <div class="fixed inset-0 z-[10001] overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-0 sm:p-4 text-center sm:items-center">
          <TransitionChild
            as="template"
            enter="ease-out duration-300"
            enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          >
            <DialogPanel class="relative transform overflow-hidden rounded-none sm:rounded-lg bg-white dark:bg-gray-900 border-0 sm:border border-gray-200 dark:border-gray-800 px-4 pb-4 pt-4 sm:px-6 sm:pb-6 sm:pt-5 text-left shadow-xl transition-all w-full min-h-screen sm:min-h-0 sm:my-8 sm:max-w-2xl sm:p-6">
              <div>
                <!-- Header with close button -->
                <div class="flex items-start justify-between mb-3 sm:mb-4">
                  <DialogTitle as="h3" class="text-base sm:text-lg font-medium leading-6 text-gray-900 dark:text-gray-100">
                    {{$t('app.views.orders.modals.details.order_title', { id: order.order_number || order.id })}}
                  </DialogTitle>
                  <button
                    type="button"
                    class="rounded-md bg-white dark:bg-transparent text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 ml-2 flex-shrink-0"
                    @click="$emit('close')"
                  >
                    <span class="sr-only">{{$t('app.views.orders.modals.details.close')}}</span>
                    <XMarkIcon class="h-5 w-5 sm:h-6 sm:w-6" aria-hidden="true" />
                  </button>
                </div>

                <!-- Internal Toast Notification -->
                <Transition
                  enter-active-class="transition-all duration-300 ease-out"
                  enter-from-class="transform opacity-0 -translate-y-2"
                  enter-to-class="transform opacity-100 translate-y-0"
                  leave-active-class="transition-all duration-200 ease-in"
                  leave-from-class="transform opacity-100 translate-y-0"
                  leave-to-class="transform opacity-0 -translate-y-2"
                >
                  <div v-if="internalToast.show" class="mb-4 rounded-lg p-3 flex items-center justify-between shadow-md"
                    :class="{
                      'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800': internalToast.type === 'success',
                      'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800': internalToast.type === 'error',
                      'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800': internalToast.type === 'info',
                      'bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800': internalToast.type === 'warning'
                    }"
                  >
                    <span class="text-sm font-medium"
                      :class="{
                        'text-green-800 dark:text-green-200': internalToast.type === 'success',
                        'text-red-800 dark:text-red-200': internalToast.type === 'error',
                        'text-blue-800 dark:text-blue-200': internalToast.type === 'info',
                        'text-yellow-800 dark:text-yellow-200': internalToast.type === 'warning'
                      }"
                    >
                      {{ internalToast.message }}
                    </span>
                    <button @click="internalToast.show = false" class="ml-3 flex-shrink-0"
                      :class="{
                        'text-green-600 hover:text-green-700 dark:text-green-400': internalToast.type === 'success',
                        'text-red-600 hover:text-red-700 dark:text-red-400': internalToast.type === 'error',
                        'text-blue-600 hover:text-blue-700 dark:text-blue-400': internalToast.type === 'info',
                        'text-yellow-600 hover:text-yellow-700 dark:text-yellow-400': internalToast.type === 'warning'
                      }"
                    >
                      <XMarkIcon class="h-5 w-5" />
                    </button>
                  </div>
                </Transition>
                
                <!-- Status badges -->
                <div class="flex flex-wrap gap-2 mb-4">
                  <span 
                    class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
                    :class="getStatusBadgeClass(order.status)"
                  >
                    {{ order.status }}
                  </span>
                  <span
                    class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
                    :class="order.is_paid ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200' : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200'"
                  >
                    {{ order.is_paid ? $t('app.views.orders.payment.paid') : $t('app.views.orders.payment.pending') }}
                  </span>
                </div>
                
                <div class="grid grid-cols-1 gap-3 sm:gap-4 sm:grid-cols-2 mb-4">
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
                
                <div class="mb-4">
                  <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">{{$t('app.views.orders.modals.details.order_items')}}</h4>
                  <div class="overflow-x-auto -mx-4 sm:mx-0">
                    <div class="inline-block min-w-full align-middle px-4 sm:px-0">
                      <div class="overflow-hidden border border-gray-200 dark:border-gray-800 rounded-lg">
                        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-800">
                          <thead class="bg-gray-50 dark:bg-gray-800">
                            <tr>
                              <th scope="col" class="px-2 sm:px-4 py-2 sm:py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{$t('app.views.orders.modals.details.headers.item')}}</th>
                              <th scope="col" class="px-2 sm:px-4 py-2 sm:py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{$t('app.views.orders.modals.details.headers.qty')}}</th>
                              <th scope="col" class="hidden sm:table-cell px-2 sm:px-4 py-2 sm:py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{$t('app.views.orders.modals.details.headers.price')}}</th>
                              <th scope="col" class="px-2 sm:px-4 py-2 sm:py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{{$t('app.views.orders.modals.details.headers.total')}}</th>
                            </tr>
                          </thead>
                          <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
                            <tr v-for="item in order.items" :key="item.id">
                              <td class="px-2 sm:px-4 py-2 sm:py-3 text-sm text-gray-900 dark:text-gray-100">
                                <div class="font-medium text-gray-900 dark:text-gray-100 text-xs sm:text-sm">{{ item.name }}</div>
                                <div v-if="item.variant" class="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
                                  {{ item.variant.name }}
                                </div>
                                <div v-if="item.menu_item?.category" class="mt-1 flex items-center gap-1.5 flex-wrap">
                                  <span class="inline-flex items-center rounded-full bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 text-xs font-medium text-gray-600 dark:text-gray-300">
                                    {{ typeof item.menu_item.category === 'string' ? item.menu_item.category : item.menu_item.category.name }}
                                  </span>
                                  <!-- Kitchen visibility indicator -->
                                  <span v-if="getCategoryVisibility(item) === false" 
                                    class="inline-flex items-center gap-1 rounded-full bg-orange-100 dark:bg-orange-900/30 px-1.5 py-0.5 text-xs font-medium text-orange-700 dark:text-orange-300"
                                    :title="$t('app.views.orders.modals.details.not_visible_in_kitchen')"
                                  >
                                    <EyeSlashIcon class="h-3 w-3" />
                                    <span class="hidden sm:inline">{{$t('app.views.orders.modals.details.not_in_kitchen')}}</span>
                                  </span>
                                  <span v-else-if="getCategoryVisibility(item) === true" 
                                    class="inline-flex items-center gap-1 rounded-full bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 text-xs font-medium text-green-700 dark:text-green-300"
                                    :title="$t('app.views.orders.modals.details.visible_in_kitchen')"
                                  >
                                    <EyeIcon class="h-3 w-3" />
                                    <span class="hidden sm:inline">{{$t('app.views.orders.modals.details.in_kitchen')}}</span>
                                  </span>
                                </div>
                                <div v-if="item.notes" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                  <span class="font-medium">{{$t('app.views.orders.modals.details.note')}}</span> {{ item.notes }}
                                </div>
                                <div v-if="item.special_instructions" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                  <span class="font-medium">{{$t('app.views.orders.modals.details.special_instructions')}}</span> {{ item.special_instructions }}
                                </div>
                                <!-- Show extras if any -->
                                <div v-if="item.extras && item.extras.length > 0" class="mt-1 space-y-0.5">
                                  <p v-for="(extra, idx) in item.extras" :key="idx" class="text-xs text-indigo-600 dark:text-indigo-400">
                                    + {{ extra.name }} ({{ extra.quantity }}x ${{ extra.price.toFixed(2) }})
                                  </p>
                                </div>
                                <!-- Show price on mobile (hidden on desktop) -->
                                <div class="sm:hidden text-xs text-gray-500 dark:text-gray-400 mt-1">
                                  ${{ (item.unit_price || 0).toFixed(2) }} c/u
                                </div>
                              </td>
                              <td class="px-2 sm:px-4 py-2 sm:py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400 text-right align-top">
                                {{ item.quantity }}
                              </td>
                              <td class="hidden sm:table-cell px-2 sm:px-4 py-2 sm:py-3 whitespace-nowrap text-sm text-right align-top">
                            <div class="flex items-center justify-end gap-2">
                              <!-- Show original price if unit_price is less than menu item price (discount was applied) -->
                              <span v-if="item.menu_item?.price && item.unit_price < item.menu_item.price" class="text-gray-500 dark:text-gray-400 line-through text-xs">
                                ${{ (item.menu_item.price || 0).toFixed(2) }}
                              </span>
                              <span :class="item.menu_item?.price && item.unit_price < item.menu_item.price ? 'text-green-600 dark:text-green-400 font-medium' : 'text-gray-500 dark:text-gray-400'">
                                ${{ (item.unit_price || 0).toFixed(2) }}
                              </span>
                              <span v-if="item.menu_item?.price && item.unit_price < item.menu_item.price" class="inline-flex items-center rounded-full bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 text-xs font-medium text-green-800 dark:text-green-200">
                                {{ $t('app.forms.sale_badge') }}
                              </span>
                            </div>
                          </td>
                              <td class="px-2 sm:px-4 py-2 sm:py-3 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100 text-right align-top">
                                ${{ calculateItemTotal(item).toFixed(2) }}
                              </td>
                            </tr>
                          </tbody>
                          <tfoot>
                            <tr v-if="totalSavings > 0">
                              <td colspan="2" class="sm:colspan-3 px-2 sm:px-4 py-2 text-xs sm:text-sm text-green-600 dark:text-green-400 text-right">
                                {{$t('app.forms.total_savings')}}
                              </td>
                              <td class="hidden sm:table-cell"></td>
                              <td class="px-2 sm:px-4 py-2 text-xs sm:text-sm font-medium text-green-600 dark:text-green-400 text-right">
                                -${{ totalSavings.toFixed(2) }}
                              </td>
                            </tr>
                            <tr>
                              <td colspan="2" class="sm:colspan-3 px-2 sm:px-4 py-1 text-base sm:text-lg font-bold text-gray-900 dark:text-gray-100 text-right">
                                {{$t('app.views.orders.modals.details.subtotal')}}
                              </td>
                              <td class="hidden sm:table-cell"></td>
                              <td class="px-2 sm:px-4 py-1 text-base sm:text-lg font-bold text-gray-900 dark:text-gray-100 text-right">
                                ${{ (order.subtotal || 0).toFixed(2) }}
                              </td>
                            </tr>
                            <tr v-if="(order.tax || 0) > 0">
                              <td colspan="2" class="sm:colspan-3 px-2 sm:px-4 py-1 text-sm sm:text-base text-gray-600 dark:text-gray-300 text-right font-medium">
                                {{$t('app.views.orders.modals.details.tax', { rate: ((order.taxRate || 0) * 100).toFixed(1) })}}
                              </td>
                              <td class="hidden sm:table-cell"></td>
                              <td class="px-2 sm:px-4 py-1 text-sm sm:text-base text-gray-600 dark:text-gray-300 text-right font-medium">
                                ${{ (order.tax || 0).toFixed(2) }}
                              </td>
                            </tr>
                            <tr>
                              <td colspan="2" class="sm:colspan-3 px-2 sm:px-4 py-2 sm:py-3 text-base sm:text-lg font-bold text-gray-900 dark:text-white text-right">
                                {{$t('app.views.orders.modals.details.total')}}
                              </td>
                              <td class="hidden sm:table-cell"></td>
                              <td class="px-2 sm:px-4 py-2 sm:py-3 text-base sm:text-lg font-bold text-gray-900 dark:text-white text-right">
                                ${{ (order.total || 0).toFixed(2) }}
                              </td>
                            </tr>
                          </tfoot>
                        </table>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div v-if="order.notes" class="mb-4">
                  <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">{{$t('app.views.orders.modals.details.order_notes')}}</h4>
                  <p class="text-sm text-gray-900 dark:text-gray-100">{{ order.notes }}</p>
                </div>
                
                <!-- Payment Method Selection -->
                <div v-if="!order.is_paid && order.status !== 'cancelled' && showPaymentMethodSelector && canProcessPayments" class="mb-4 p-3 sm:p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                  <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">{{$t('app.views.orders.payment.select_method') || 'Select Payment Method'}}</h4>
                  <div class="grid grid-cols-2 gap-2 sm:gap-3">
                    <button
                      v-for="method in paymentMethods"
                      :key="method.value"
                      type="button"
                      class="flex items-center justify-center gap-1 sm:gap-2 px-2 sm:px-4 py-2 sm:py-3 rounded-md border-2 transition-all text-xs sm:text-sm"
                      :class="selectedPaymentMethod === method.value 
                        ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20 text-indigo-700 dark:text-indigo-300' 
                        : 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:border-indigo-300 dark:hover:border-indigo-600'"
                      @click="selectedPaymentMethod = method.value"
                    >
                      <component :is="method.icon" class="h-4 w-4 sm:h-5 sm:w-5" />
                      <span class="font-medium text-xs sm:text-sm">{{ method.label }}</span>
                    </button>
                  </div>
                </div>
                
                <div class="flex flex-col gap-2 sm:grid sm:grid-flow-row-dense sm:grid-cols-3 sm:gap-3">
                  <button
                    v-if="!order.is_paid"
                    type="button"
                    class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-3 py-2 sm:px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:col-start-1 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-700 dark:hover:bg-gray-700"
                    @click="emit('edit-order', order)"
                  >
                    {{$t('app.forms.edit')}}
                  </button>
                  <button
                    v-if="!order.is_paid && order.status !== 'cancelled' && canProcessPayments"
                    type="button"
                    class="inline-flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-3 py-2 sm:px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:col-start-2"
                    @click="showPaymentMethodSelector ? completePayment() : showPaymentMethodSelector = true"
                  >
                    {{showPaymentMethodSelector ? $t('app.views.orders.payment.confirm_payment') || 'Confirm Payment' : $t('app.views.orders.modals.details.complete_payment') || 'Complete Payment'}}
                  </button>
                  <button
                    v-if="order.status === 'Preparing'"
                    type="button"
                    class="inline-flex w-full justify-center rounded-md border border-transparent bg-green-600 px-3 py-2 sm:px-4 text-sm font-medium text-white shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 sm:col-start-2"
                    @click="updateStatus('Ready')"
                  >
                    {{$t('app.views.orders.modals.details.mark_ready')}}
                  </button>
                  <button
                    v-else-if="order.status === 'ready'"
                    type="button"
                    class="inline-flex w-full justify-center rounded-md border border-transparent bg-green-600 px-3 py-2 sm:px-4 text-sm font-medium text-white shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 sm:col-start-2"
                    @click="updateStatus('completed')"
                  >
                    {{$t('app.views.orders.modals.details.mark_completed')}}
                  </button>
                  <button
                    type="button"
                    class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white dark:bg-gray-800 px-3 py-2 sm:px-4 text-sm font-medium text-gray-700 dark:text-gray-200 shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:col-start-1 dark:border-gray-700"
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
import { XMarkIcon, BanknotesIcon, CreditCardIcon, DevicePhoneMobileIcon, EllipsisHorizontalIcon, EyeIcon, EyeSlashIcon } from '@heroicons/vue/24/outline'
import orderService from '@/services/orderService'
import { useI18n } from 'vue-i18n'
import { useToast } from '@/composables/useToast'
import { useConfirm } from '@/composables/useConfirm'
import { useTheme } from '@/composables/useTheme'
import { usePermissions } from '@/composables/usePermissions'

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

const emit = defineEmits(['close', 'status-update', 'paymentCompleted', 'openCashRegister', 'edit-order']);

const { confirm } = useConfirm();
const { showSuccess, showError } = useToast();
const { t } = useI18n();
const { canProcessPayments } = usePermissions();
const isMounted = ref(false);

// Internal toast notification state
const internalToast = ref({
  show: false,
  message: '',
  type: 'success' as 'success' | 'error' | 'info' | 'warning'
});

// Function to show internal toast
const showInternalToast = (message: string, type: 'success' | 'error' | 'info' | 'warning' = 'success', duration = 3000) => {
  internalToast.value = { show: true, message, type };
  setTimeout(() => {
    internalToast.value.show = false;
  }, duration);
};

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

// Helper function to get category visibility
const getCategoryVisibility = (item: any): boolean | null => {
  if (!item.menu_item?.category) return null;
  
  // If category is an object with visible_in_kitchen property
  if (typeof item.menu_item.category === 'object' && item.menu_item.category !== null) {
    return item.menu_item.category.visible_in_kitchen ?? true;
  }
  
  // If category is just a string, we don't have visibility info
  return null;
};

// Calculate item total including extras
const calculateItemTotal = (item: any): number => {
  let total = item.quantity * (item.price || item.unit_price || 0);
  
  // Add extras to total
  if (item.extras && item.extras.length > 0) {
    const extrasTotal = item.extras.reduce((sum: number, extra: any) => {
      return sum + (extra.price * extra.quantity);
    }, 0);
    total += extrasTotal;
  }
  
  return total;
};

// Calculate total savings from discounts
const totalSavings = computed(() => {
  if (!props.order.items) return 0;
  
  return props.order.items.reduce((total, item) => {
    // Check if unit_price is less than menu item price (discount was applied)
    if (item.menu_item?.price && item.unit_price && item.unit_price < item.menu_item.price) {
      const savings = (item.menu_item.price - item.unit_price) * item.quantity;
      return total + savings;
    }
    return total;
  }, 0);
});

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
  const confirmed = await confirm(
    'Cancel Order',
    'Are you sure you want to cancel this order? This action cannot be undone.',
    'Yes, cancel order',
    'No, keep it',
    'bg-red-600 hover:bg-red-700 focus:ring-red-500'
  );

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
  { value: 'cash' as const, label: t('app.views.cashRegister.cash') || 'Cash', icon: BanknotesIcon },
  { value: 'card' as const, label: t('app.views.cashRegister.card') || 'Card', icon: CreditCardIcon },
  { value: 'digital' as const, label: t('app.views.cashRegister.digital') || 'Digital', icon: DevicePhoneMobileIcon },
  { value: 'other' as const, label: t('app.views.cashRegister.other') || 'Other', icon: EllipsisHorizontalIcon }
]

async function completePayment() {
  try {
    await orderService.markOrderPaid(props.order.id, selectedPaymentMethod.value);
    showInternalToast(t('app.views.orders.payment.success') || 'Pago completado exitosamente', 'success');
    showPaymentMethodSelector.value = false;
    
    // Close modal immediately to prevent showing stale data
    emit('close');
    
    // Emit payment completed event after closing
    emit('paymentCompleted', props.order);
  } catch (e: any) {
    console.error('Failed to complete payment:', e);

    // Get error message from response
    const errorMessage = e.response?.data?.error?.message || e.response?.data?.detail || '';
    
    // Handle specific cash register session error with friendly message
    if (errorMessage.includes('No open cash register session') || errorMessage.includes('cash register session')) {
      showInternalToast(
        'No hay una sesión de caja abierta. Por favor abre una sesión de caja antes de procesar pagos.',
        'warning',
        5000
      );
    } else {
      // Show generic error for other payment failures
      const friendlyMessage = errorMessage || t('app.views.cashRegister.paymentFailedGeneric') || 'Error al procesar el pago';
      showInternalToast(friendlyMessage, 'error', 5000);
    }
  }
}
</script>
