<template>
  <TransitionRoot as="template" :show="open">
    <Dialog as="div" class="relative z-10" @close="$emit('close')">
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
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-4xl sm:p-6">
              <div>
                <div class="flex items-center justify-between">
                  <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                    New Order
                  </DialogTitle>
                  <button
                    type="button"
                    class="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                    @click="$emit('close')"
                  >
                    <span class="sr-only">Close</span>
                    <XMarkIcon class="h-6 w-6" aria-hidden="true" />
                  </button>
                </div>

                <div class="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2">
                  <!-- Left Column: Order Details -->
                  <div class="space-y-4">
                    <div>
                      <label for="order-type" class="block text-sm font-medium text-gray-700">Order Type</label>
                      <select
                        id="order-type"
                        v-model="form.type"
                        class="mt-1 block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
                      >
                        <option value="Dine-in">Dine-in</option>
                        <option value="Takeaway">Takeaway</option>
                        <option value="Delivery">Delivery</option>
                      </select>
                    </div>

                    <div v-if="form.type === 'Dine-in'">
                      <label for="table" class="block text-sm font-medium text-gray-700">Table</label>
                      <select
                        id="table"
                        v-model="form.tableId"
                        class="mt-1 block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
                      >
                        <option v-for="table in availableTables" :key="table.id" :value="table.id">
                          Table {{ table.number }} ({{ table.capacity }} pax)
                        </option>
                      </select>
                    </div>

                    <div v-else>
                      <label for="customer-name" class="block text-sm font-medium text-gray-700">
                        {{ form.type === 'Delivery' ? 'Delivery Address' : 'Customer Name' }}
                      </label>
                      <input
                        id="customer-name"
                        v-model="form.customerName"
                        type="text"
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        :placeholder="form.type === 'Delivery' ? 'Enter delivery address' : 'Enter customer name'"
                      />
                    </div>

                    <div>
                      <label for="notes" class="block text-sm font-medium text-gray-700">Order Notes</label>
                      <textarea
                        id="notes"
                        v-model="form.notes"
                        rows="3"
                        class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        placeholder="Any special instructions?"
                      />
                    </div>
                  </div>

                  <!-- Right Column: Menu Items -->
                  <div class="space-y-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Menu Items</label>
                      <div class="space-y-2">
                        <div v-for="item in menuItems" :key="item.id" class="flex items-center justify-between p-2 border rounded-md hover:bg-gray-50">
                          <div>
                            <div class="font-medium text-gray-900">{{ item.name }}</div>
                            <div class="text-sm text-gray-500">${{ item.price.toFixed(2) }}</div>
                          </div>
                          <div class="flex items-center space-x-2">
                            <button
                              type="button"
                              class="inline-flex items-center p-1 border border-transparent rounded-full shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                              @click="decreaseQuantity(item.id)"
                            >
                              <MinusIcon class="h-4 w-4" aria-hidden="true" />
                            </button>
                            <span class="w-8 text-center">{{ getItemQuantity(item.id) }}</span>
                            <button
                              type="button"
                              class="inline-flex items-center p-1 border border-transparent rounded-full shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                              @click="increaseQuantity(item.id)"
                            >
                              <PlusIcon class="h-4 w-4" aria-hidden="true" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Selected Items -->
                    <div v-if="selectedItems.length > 0" class="mt-4">
                      <h4 class="text-sm font-medium text-gray-700 mb-2">Order Summary</h4>
                      <div class="border rounded-md divide-y divide-gray-200">
                        <div v-for="item in selectedItems" :key="item.id" class="p-3 text-sm">
                          <div class="flex justify-between">
                            <span class="font-medium">{{ item.quantity }}x {{ item.name }}</span>
                            <span>${{ (item.quantity * item.price).toFixed(2) }}</span>
                          </div>
                          <div v-if="item.notes" class="text-xs text-gray-500 mt-1">{{ item.notes }}</div>
                        </div>
                        <div class="p-3 bg-gray-50 text-right">
                          <div class="font-medium">Total: ${{ orderTotal.toFixed(2) }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                <button
                  type="button"
                  class="inline-flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:col-start-2 sm:text-sm disabled:opacity-50"
                  :disabled="selectedItems.length === 0 || (form.type === 'Dine-in' && !form.tableId) || (form.type !== 'Dine-in' && !form.customerName)"
                  @click="createOrder"
                >
                  Create Order
                </button>
                <button
                  type="button"
                  class="mt-3 inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:col-start-1 sm:mt-0 sm:text-sm"
                  @click="$emit('close')"
                >
                  Cancel
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
import { XMarkIcon, PlusIcon, MinusIcon } from '@heroicons/vue/24/outline';
import { useToast } from '@/composables/useToast';

const props = defineProps({
  open: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(['close', 'order-created']);

const { showSuccess, showError } = useToast();

// Form data
const form = ref({
  type: 'Dine-in',
  tableId: '',
  customerName: '',
  notes: '',
  items: [] // Array of { id, quantity, notes }
});

// Mock data - replace with API calls
const menuItems = ref([
  { id: 1, name: 'Cappuccino', price: 4.50, category: 'Coffee' },
  { id: 2, name: 'Latte', price: 4.00, category: 'Coffee' },
  { id: 3, name: 'Espresso', price: 3.50, category: 'Coffee' },
  { id: 4, name: 'Avocado Toast', price: 12.00, category: 'Food' },
  { id: 5, name: 'Croissant', price: 3.50, category: 'Pastry' },
  { id: 6, name: 'Orange Juice', price: 5.50, category: 'Juice' },
]);

const availableTables = ref([
  { id: '1', number: '01', capacity: 4, status: 'Available' },
  { id: '2', number: '02', capacity: 2, status: 'Available' },
  { id: '3', number: '03', capacity: 6, status: 'Available' },
  { id: '4', number: '04', capacity: 4, status: 'Available' },
]);

// Computed properties
const selectedItems = computed(() => {
  return form.value.items
    .filter(item => item.quantity > 0)
    .map(item => {
      const menuItem = menuItems.value.find(mi => mi.id === item.id);
      return {
        ...menuItem,
        quantity: item.quantity,
        notes: item.notes
      };
    });
});

const orderTotal = computed(() => {
  return selectedItems.value.reduce((total, item) => {
    return total + (item.price * item.quantity);
  }, 0);
});

// Methods
function getItemQuantity(itemId) {
  const item = form.value.items.find(i => i.id === itemId);
  return item ? item.quantity : 0;
}

function increaseQuantity(itemId) {
  const itemIndex = form.value.items.findIndex(i => i.id === itemId);
  if (itemIndex === -1) {
    form.value.items.push({ id: itemId, quantity: 1, notes: '' });
  } else {
    form.value.items[itemIndex].quantity++;
  }
}

function decreaseQuantity(itemId) {
  const itemIndex = form.value.items.findIndex(i => i.id === itemId);
  if (itemIndex !== -1) {
    if (form.value.items[itemIndex].quantity > 1) {
      form.value.items[itemIndex].quantity--;
    } else {
      form.value.items.splice(itemIndex, 1);
    }
  }
}

function createOrder() {
  try {
    // In a real app, you would call an API here
    const newOrder = {
      id: Math.floor(1000 + Math.random() * 9000).toString(),
      status: 'Pending',
      type: form.value.type,
      customerName: form.value.customerName || 'Walk-in',
      table: form.value.tableId ? `T-${form.value.tableId.padStart(2, '0')}` : null,
      items: selectedItems.value,
      subtotal: orderTotal.value,
      tax: orderTotal.value * 0.1, // 10% tax
      taxRate: 0.1,
      total: orderTotal.value * 1.1, // subtotal + tax
      notes: form.value.notes,
      createdAt: new Date()
    };

    // Reset form
    form.value = {
      type: 'Dine-in',
      tableId: '',
      customerName: '',
      notes: '',
      items: []
    };

    // Emit the new order
    emit('order-created', newOrder);
    showSuccess('Order created successfully');
    emit('close');
  } catch (error) {
    console.error('Error creating order:', error);
    showError('Failed to create order');
  }
}

// Initialize form with all menu items and quantity 0
onMounted(() => {
  form.value.items = menuItems.value.map(item => ({
    id: item.id,
    quantity: 0,
    notes: ''
  }));
});
</script>
