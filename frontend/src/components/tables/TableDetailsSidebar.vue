<template>
  <TransitionRoot as="template" :show="open">
    <Dialog as="div" class="relative z-10" @close="$emit('close')">
      <TransitionChild
        as="template"
        enter="ease-in-out duration-500"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in-out duration-500"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-hidden">
        <div class="absolute inset-0 overflow-hidden">
          <div class="pointer-events-none fixed inset-y-0 right-0 flex max-w-full pl-10">
            <TransitionChild
              as="template"
              enter="transform transition ease-in-out duration-500 sm:duration-700"
              enter-from="translate-x-full"
              enter-to="translate-x-0"
              leave="transform transition ease-in-out duration-500 sm:duration-700"
              leave-from="translate-x-0"
              leave-to="translate-x-full"
            >
              <DialogPanel class="pointer-events-auto w-screen max-w-md">
                <div class="flex h-full flex-col overflow-y-scroll bg-white shadow-xl">
                  <div class="px-4 py-6 sm:px-6">
                    <div class="flex items-start justify-between">
                      <DialogTitle class="text-lg font-medium text-gray-900">
                        Table {{ table?.number }}
                      </DialogTitle>
                      <div class="ml-3 flex h-7 items-center">
                        <button
                          type="button"
                          class="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                          @click="$emit('close')"
                        >
                          <span class="sr-only">Close panel</span>
                          <XMarkIcon class="h-6 w-6" aria-hidden="true" />
                        </button>
                      </div>
                    </div>
                    
                    <div class="mt-1">
                      <div class="flex items-center">
                        <span
                          class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
                          :class="getStatusBadgeClass(table?.status)"
                        >
                          {{ table?.status }}
                        </span>
                        <span class="ml-2 text-sm text-gray-500">
                          {{ table?.capacity }} seats
                        </span>
                        <span class="ml-2 text-sm text-gray-500">
                          • {{ table?.location }}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Active Order Section -->
                  <div v-if="table?.currentOrder" class="border-t border-gray-200 px-4 py-5 sm:px-6">
                    <h3 class="text-lg font-medium leading-6 text-gray-900">Current Order</h3>
                    <div class="mt-4">
                      <div class="flex items-center justify-between">
                        <h4 class="text-sm font-medium text-gray-900">Order #{{ table.currentOrder.id }}</h4>
                        <span class="text-sm text-gray-500">
                          {{ formatTimeAgo(table.currentOrder.createdAt) }}
                        </span>
                      </div>
                      
                      <div class="mt-2">
                        <div v-for="item in table.currentOrder.items" :key="item.id" class="flex items-start py-2">
                          <div class="flex-1">
                            <p class="text-sm font-medium text-gray-900">{{ item.name }}</p>
                            <p v-if="item.notes" class="text-xs text-gray-500">{{ item.notes }}</p>
                          </div>
                          <div class="ml-4 text-right">
                            <p class="text-sm font-medium text-gray-900">
                              {{ item.quantity }} × ${{ item.price.toFixed(2) }}
                            </p>
                            <p class="text-xs text-gray-500">
                              ${{ (item.quantity * item.price).toFixed(2) }}
                            </p>
                          </div>
                        </div>
                      </div>
                      
                      <div class="mt-4 border-t border-gray-200 pt-4">
                        <div class="flex justify-between text-sm font-medium text-gray-900">
                          <p>Total</p>
                          <p>${{ table.currentOrder.total.toFixed(2) }}</p>
                        </div>
                      </div>
                      
                      <div class="mt-4 flex space-x-3">
                        <button
                          type="button"
                          class="flex-1 rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                          @click="$emit('view-order', table.currentOrder.id)"
                        >
                          View Order
                        </button>
                        <button
                          type="button"
                          class="flex-1 rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                          @click="printReceipt"
                        >
                          Print Receipt
                        </button>
                      </div>
                    </div>
                  </div>
                  
                  <!-- No Active Order Section -->
                  <div v-else class="border-t border-gray-200 px-4 py-5 sm:px-6">
                    <div class="text-center">
                      <ShoppingBagIcon class="mx-auto h-12 w-12 text-gray-400" />
                      <h3 class="mt-2 text-sm font-medium text-gray-900">No active order</h3>
                      <p class="mt-1 text-sm text-gray-500">
                        Start a new order for this table
                      </p>
                      <div class="mt-6">
                        <button
                          type="button"
                          class="inline-flex items-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                          @click="$emit('start-order')"
                        >
                          <PlusIcon class="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
                          New Order
                        </button>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Table Actions -->
                  <div class="flex-1 border-t border-gray-200 px-4 py-5 sm:px-6">
                    <div class="space-y-4">
                      <div>
                        <h3 class="text-sm font-medium text-gray-900">Table Actions</h3>
                        <div class="mt-2 grid grid-cols-1 gap-2">
                          <button
                            v-if="table?.currentOrder"
                            type="button"
                            class="inline-flex items-center justify-center rounded-md border border-transparent bg-green-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                            @click="$emit('checkout')"
                          >
                            <CurrencyDollarIcon class="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
                            Checkout
                          </button>
                          <button
                            type="button"
                            class="inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                            @click="editTable"
                          >
                            <PencilIcon class="-ml-1 mr-2 h-5 w-5 text-gray-500" aria-hidden="true" />
                            Edit Table
                          </button>
                          <button
                            v-if="!table?.currentOrder"
                            type="button"
                            class="inline-flex items-center justify-center rounded-md border border-transparent bg-red-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                            @click="deleteTable"
                          >
                            <TrashIcon class="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
                            Delete Table
                          </button>
                        </div>
                      </div>
                      
                      <div>
                        <h3 class="text-sm font-medium text-gray-900">Table Information</h3>
                        <div class="mt-2">
                          <dl class="divide-y divide-gray-200">
                            <div class="py-2 sm:grid sm:grid-cols-3 sm:gap-4">
                              <dt class="text-sm font-medium text-gray-500">Table Number</dt>
                              <dd class="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                                {{ table?.number }}
                              </dd>
                            </div>
                            <div class="py-2 sm:grid sm:grid-cols-3 sm:gap-4">
                              <dt class="text-sm font-medium text-gray-500">Capacity</dt>
                              <dd class="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                                {{ table?.capacity }} people
                              </dd>
                            </div>
                            <div class="py-2 sm:grid sm:grid-cols-3 sm:gap-4">
                              <dt class="text-sm font-medium text-gray-500">Location</dt>
                              <dd class="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                                {{ table?.location }}
                              </dd>
                            </div>
                            <div class="py-2 sm:grid sm:grid-cols-3 sm:gap-4">
                              <dt class="text-sm font-medium text-gray-500">Status</dt>
                              <dd class="mt-1 text-sm text-gray-900 sm:col-span-2 sm:mt-0">
                                <span
                                  class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
                                  :class="getStatusBadgeClass(table?.status)"
                                >
                                  {{ table?.status }}
                                </span>
                              </dd>
                            </div>
                          </dl>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { ref } from 'vue';
import { 
  Dialog, 
  DialogPanel, 
  DialogTitle, 
  TransitionChild, 
  TransitionRoot 
} from '@headlessui/vue';
import { 
  XMarkIcon,
  PlusIcon,
  ShoppingBagIcon,
  CurrencyDollarIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/vue/24/outline';
import { useConfirm } from '@/composables/useConfirm';
import { useToast } from '@/composables/useToast';

defineProps({
  open: {
    type: Boolean,
    required: true
  },
  table: {
    type: Object,
    default: () => ({
      id: '',
      number: '',
      capacity: 0,
      location: '',
      status: 'Available',
      currentOrder: null
    })
  }
});

const emit = defineEmits(['close', 'checkout', 'start-order', 'edit-table', 'delete-table']);

const { confirm } = useConfirm();
const { showSuccess, showError } = useToast();

function getStatusBadgeClass(status) {
  const statusClasses = {
    'Available': 'bg-green-100 text-green-800',
    'Occupied': 'bg-yellow-100 text-yellow-800',
    'Reserved': 'bg-blue-100 text-blue-800',
    'Out of Service': 'bg-red-100 text-red-800',
  };
  return statusClasses[status] || 'bg-gray-100 text-gray-800';
}

function formatTimeAgo(date) {
  if (!date) return '';
  
  const now = new Date();
  const diffInSeconds = Math.floor((now - new Date(date)) / 1000);
  
  if (diffInSeconds < 60) return 'Just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  return `${Math.floor(diffInSeconds / 86400)}d ago`;
}

function printReceipt() {
  // In a real app, this would open a print dialog with a formatted receipt
  console.log('Printing receipt for order:', props.table.currentOrder?.id);
  showSuccess('Opening print dialog...');
}

async function editTable() {
  emit('edit-table', props.table);
  emit('close');
}

async function deleteTable() {
  const confirmed = await confirm({
    title: 'Delete Table',
    message: `Are you sure you want to delete Table ${props.table.number}? This action cannot be undone.`,
    confirmText: 'Yes, delete',
    cancelText: 'No, keep it',
    confirmClass: 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
  });
  
  if (confirmed) {
    try {
      // In a real app, you would call an API here
      emit('delete-table', props.table.id);
      showSuccess(`Table ${props.table.number} has been deleted`);
      emit('close');
    } catch (error) {
      console.error('Error deleting table:', error);
      showError('Failed to delete table');
    }
  }
}
</script>
