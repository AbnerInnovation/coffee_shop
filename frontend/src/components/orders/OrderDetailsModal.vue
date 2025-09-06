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
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
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
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl sm:p-6">
              <div>
                <div class="flex items-center justify-between">
                  <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                    Order #{{ order.id }}
                  </DialogTitle>
                  <div class="flex items-center space-x-2">
                    <span 
                      class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
                      :class="getStatusBadgeClass(order.status)"
                    >
                      {{ order.status }}
                    </span>
                    <button
                      type="button"
                      class="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                      @click="$emit('close')"
                    >
                      <span class="sr-only">Close</span>
                      <XMarkIcon class="h-6 w-6" aria-hidden="true" />
                    </button>
                  </div>
                </div>
                
                <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <h4 class="text-sm font-medium text-gray-500">Table</h4>
                    <p class="mt-1 text-sm text-gray-900">{{ order.table_number || 'Takeaway' }}</p>
                  </div>
                  <div>
                    <h4 class="text-sm font-medium text-gray-500">Order Time</h4>
                    <p class="mt-1 text-sm text-gray-900">{{ formatDateTime(order.createdAt) }}</p>
                  </div>
                  <div>
                    <h4 class="text-sm font-medium text-gray-500">Customer</h4>
                    <p class="mt-1 text-sm text-gray-900">{{ order.customer_name || 'No name provided' }}</p>
                  </div>
                </div>
                
                <div class="mt-6">
                  <h4 class="text-sm font-medium text-gray-500">Order Items</h4>
                  <div class="mt-2 overflow-hidden border border-gray-200 rounded-lg">
                    <table class="min-w-full divide-y divide-gray-200">
                      <thead class="bg-gray-50">
                        <tr>
                          <th scope="col" class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Item</th>
                          <th scope="col" class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Qty</th>
                          <th scope="col" class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                          <th scope="col" class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                        </tr>
                      </thead>
                      <tbody class="bg-white divide-y divide-gray-200">
                        <tr v-for="item in order.items" :key="item.id">
                          <td class="px-4 py-3 text-sm text-gray-900">
                            <div class="font-medium">{{ item.name }}</div>
                            <div v-if="item.variant" class="text-xs text-gray-600 mt-1">
                              {{ item.variant.name }}
                            </div>
                            <div v-if="item.notes" class="text-xs text-gray-500 mt-1">
                              <span class="font-medium">Note:</span> {{ item.notes }}
                            </div>
                            <div v-if="item.special_instructions" class="text-xs text-gray-500 mt-1">
                              <span class="font-medium">Special Instructions:</span> {{ item.special_instructions }}
                            </div>
                          </td>
                          <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500 text-right">
                            {{ item.quantity }}
                          </td>
                          <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500 text-right">
                            ${{ (item.unit_price || 0).toFixed(2) }}
                          </td>
                          <td class="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900 text-right">
                            ${{ (item.quantity * (item.price || item.unit_price || 0)).toFixed(2) }}
                          </td>
                        </tr>
                      </tbody>
                      <tfoot>
                        <tr>
                          <td colspan="3" class="px-4 py-3 text-sm font-medium text-gray-900 text-right">
                            Subtotal
                          </td>
                          <td class="px-4 py-3 text-sm font-medium text-gray-900 text-right">
                            ${{ (order.subtotal || 0).toFixed(2) }}
                          </td>
                        </tr>
                        <tr v-if="(order.tax || 0) > 0">
                          <td colspan="3" class="px-4 py-1 text-sm text-gray-500 text-right">
                            Tax ({{ ((order.taxRate || 0) * 100).toFixed(1) }}%)
                          </td>
                          <td class="px-4 py-1 text-sm text-gray-500 text-right">
                            ${{ (order.tax || 0).toFixed(2) }}
                          </td>
                        </tr>
                        <tr>
                          <td colspan="3" class="px-4 py-3 text-base font-bold text-gray-900 text-right">
                            Total
                          </td>
                          <td class="px-4 py-3 text-base font-bold text-gray-900 text-right">
                            ${{ (order.total || 0).toFixed(2) }}
                          </td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                </div>
                
                <div v-if="order.notes" class="mt-4">
                  <h4 class="text-sm font-medium text-gray-500">Order Notes</h4>
                  <p class="mt-1 text-sm text-gray-900">{{ order.notes }}</p>
                </div>
              </div>
              
              <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                <button
                  v-if="order.status === 'Preparing'"
                  type="button"
                  class="inline-flex w-full justify-center rounded-md border border-transparent bg-green-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 sm:col-start-2 sm:text-sm"
                  @click="updateStatus('Ready')"
                >
                  Mark as Ready
                </button>
                <button
                  v-else-if="order.status === 'ready'"
                  type="button"
                  class="inline-flex w-full justify-center rounded-md border border-transparent bg-green-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 sm:col-start-2 sm:text-sm"
                  @click="updateStatus('Completed')"
                >
                  Mark as Completed
                </button>
                <button
                  type="button"
                  class="mt-3 inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:col-start-1 sm:mt-0 sm:text-sm"
                  @click="printOrder"
                >
                  Print Receipt
                </button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { 
  Dialog, 
  DialogPanel, 
  DialogTitle, 
  TransitionChild, 
  TransitionRoot 
} from '@headlessui/vue';
import { XMarkIcon } from '@heroicons/vue/24/outline';
import { useConfirm } from '@/composables/useConfirm';
import { useToast } from '@/composables/useToast';

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

const emit = defineEmits(['close', 'status-update']);

const { confirm } = useConfirm();
const { showSuccess, showError } = useToast();
const isMounted = ref(false);

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
</script>
