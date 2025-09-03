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
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 w-full max-w-[95vw] sm:max-w-4xl sm:p-6 mx-2 sm:mx-0">
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

                <div class="mt-6 grid grid-cols-1 gap-4 sm:gap-6 sm:grid-cols-2">
                  <!-- Left Column: Order Details -->
                  <div class="space-y-3 sm:space-y-4">
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
                        :disabled="loading.tables"
                      >
                        <option v-if="loading.tables" value="" disabled>Loading tables...</option>
                        <option v-else-if="error.tables" value="" disabled>Error loading tables</option>
                        <option v-else-if="availableTables.length === 0" value="" disabled>No tables available</option>
                        <option v-else v-for="table in availableTables" :key="table.id" :value="table.id">
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
                  <div class="space-y-3 sm:space-y-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-1">Menu Items</label>
                      <div v-if="loading.menu" class="text-center py-4">
                        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto"></div>
                        <p class="mt-2 text-sm text-gray-500">Loading menu items...</p>
                      </div>
                      <div v-else-if="error.menu" class="text-center py-4 text-red-600">
                        <p>Error loading menu items. Please try again.</p>
                      </div>
                      <div v-else class="space-y-2 max-h-[50vh] sm:max-h-none overflow-y-auto pr-1 -mr-1 sm:mr-0">
                        <div v-for="item in menuItems" :key="item.id" class="flex items-center justify-between p-3 sm:p-2 border rounded-md hover:bg-gray-50">
                          <div class="flex-1 min-w-0">
                            <h4 class="text-sm font-medium text-gray-900 truncate">{{ item.name }}</h4>
                            <p class="text-sm text-gray-500">${{ (item.price || 0).toFixed(2) }}</p>
                          </div>
                          <div class="flex items-center space-x-2">
                            <button
                              type="button"
                              class="p-1 rounded-full text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                              @click="decreaseQuantity(item.id)"
                              :disabled="getItemQuantity(item.id) === 0"
                            >
                              <MinusIcon class="h-5 w-5" />
                            </button>
                            <span class="w-6 text-center">{{ getItemQuantity(item.id) }}</span>
                            <button
                              type="button"
                              class="p-1 rounded-full text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                              @click="increaseQuantity(item.id)"
                            >
                              <PlusIcon class="h-5 w-5" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="mt-5 sm:mt-6 grid grid-cols-1 sm:grid-cols-2 gap-3">
                <button
                  type="button"
                  class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-3 sm:py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:text-sm"
                  @click="$emit('close')"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  class="inline-flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-3 sm:py-2 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  :disabled="selectedItems.length === 0 || (form.type === 'Dine-in' && !form.tableId) || (form.type !== 'Dine-in' && !form.customerName)"
                  @click="createOrder"
                >
                  Create Order
                </button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import orderService from '@/services/orderService';
import menuService from '@/services/menuService';
import tableService from '@/services/tableService';
import { useToast } from '@/composables/useToast';
import { 
  Dialog, 
  DialogPanel, 
  DialogTitle, 
  TransitionChild, 
  TransitionRoot 
} from '@headlessui/vue';
import { XMarkIcon, PlusIcon, MinusIcon } from '@heroicons/vue/24/outline';

// Types
interface MenuItem {
  id: number;
  name: string;
  price: number;
  description?: string;
  category: string;
  image_url?: string;
  is_available: boolean;
}

interface TableItem {
  id: string;
  number: string;
  capacity: number;
  status: string;
}

interface FormItem {
  id: number;
  quantity: number;
  notes: string;
  special_instructions: string;
}

interface FormData {
  type: 'Dine-in' | 'Takeaway' | 'Delivery';
  tableId: string;
  customerName: string;
  notes: string;
  items: FormItem[];
}

// Props and Emits
const props = defineProps<{
  open: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'order-created', order: any): void;
}>();

// Form data
const form = ref<FormData>({
  type: 'Dine-in',
  tableId: '',
  customerName: '',
  notes: '',
  items: []
});

const { showError, showSuccess } = useToast();
const menuItems = ref<MenuItem[]>([]);
const availableTables = ref<TableItem[]>([]);
const loading = ref({
  menu: false,
  tables: false
});

const error = ref({
  menu: null as string | null,
  tables: null as string | null
});

// Fetch menu items
const fetchMenuItems = async () => {
  try {
    loading.value.menu = true;
    const items = await menuService.getMenuItems();
    menuItems.value = items.map(item => ({
      id: Number(item.id), // Ensure ID is a number
      name: item.name,
      price: Number(item.price), // Ensure price is a number
      category: item.category?.name || 'Uncategorized',
      description: item.description,
      image_url: item.image_url,
      is_available: Boolean(item.is_available) // Ensure boolean
    }));
  } catch (err) {
    console.error('Error fetching menu items:', err);
    error.value.menu = 'Failed to load menu items';
    showError('Failed to load menu items');
  } finally {
    loading.value.menu = false;
  }
};

// Fetch available tables
const fetchAvailableTables = async () => {
  try {
    loading.value.tables = true;
    const tables = await tableService.getTables({ occupied: false });
    availableTables.value = tables.map(table => ({
      id: table.id.toString(),
      number: table.number.toString().padStart(2, '0'),
      capacity: table.capacity,
      status: table.is_occupied ? 'Occupied' : 'Available'
    }));
  } catch (err) {
    console.error('Error fetching tables:', err);
    error.value.tables = 'Failed to load tables';
    showError('Failed to load tables');
  } finally {
    loading.value.tables = false;
  }
};

// Computed properties
const selectedItems = computed(() => {
  return form.value.items
    .filter(item => item.quantity > 0)
    .map(item => {
      const menuItem = menuItems.value.find(mi => mi.id === item.id);
      return {
        ...menuItem,
        quantity: item.quantity,
        special_instructions: item.special_instructions
      };
    });
});

const orderTotal = computed(() => {
  return selectedItems.value.reduce((total, item) => {
    return total + ((item.price || 0) * item.quantity);
  }, 0);
});

// Methods
function getItemQuantity(itemId: number): number {
  const item = form.value.items.find(i => i.id === itemId);
  return item ? item.quantity : 0;
}

function increaseQuantity(itemId: number) {
  const itemIndex = form.value.items.findIndex(i => i.id === itemId);
  if (itemIndex !== -1) {
    form.value.items[itemIndex].quantity++;
  }
}

function decreaseQuantity(itemId: number) {
  const itemIndex = form.value.items.findIndex(i => i.id === itemId);
  if (itemIndex !== -1) {
    if (form.value.items[itemIndex].quantity > 0) {
      form.value.items[itemIndex].quantity--;
    }
  }
}

async function createOrder() {
  try {
    // Prepare the order data for the API
    const orderData = {
      table_id: form.value.type === 'Dine-in' ? parseInt(form.value.tableId) : null,
      customer_name: form.value.type !== 'Dine-in' ? form.value.customerName : null,
      notes: form.value.notes || null,
      items: selectedItems.value
        .filter(item => item.quantity > 0 && item.id !== undefined)
        .map(item => ({
          menu_item_id: item.id as number, // We've filtered out undefined ids
          quantity: item.quantity,
          special_instructions: item.special_instructions || null,
          unit_price: menuItems.value.find(mi => mi.id === item.id)?.price || 0
        }))
    };

    console.log('Sending order data:', orderData);
    
    // Call the order service to create the order
    console.log('Creating order with data:', orderData);
    const response = await orderService.createOrder(orderData);
    console.log('Order creation response:', response);
    
    if (!response) {
      throw new Error('No response received from the server');
    }
    
    // Reset the form
    form.value = {
      type: 'Dine-in',
      tableId: '',
      customerName: '',
      notes: '',
      items: menuItems.value.map(item => ({
        id: item.id,
        quantity: 0,
        notes: '',
        special_instructions: ''
      }))
    };
    
    // Create a minimal order object with required fields
    const emittedOrder = {
      id: response.id,
      status: response.status || 'pending',
      customer_name: response.customer_name || (response.table_id ? 'Dine-in' : 'Takeaway'),
      table_id: response.table_id || null,
      table_number: response.table?.number || (response.table_id || null),
      table: response.table_id ? `Table ${response.table?.number || response.table_id}` : 'Takeaway',
      total: response.total_amount || 0,
      total_amount: response.total_amount || 0,
      notes: response.notes || null,
      created_at: response.created_at || new Date().toISOString(),
      updated_at: response.updated_at || new Date().toISOString(),
      items: (response.items || []).map(item => ({
        ...item,
        name: item.name || 'Unknown Item',
        price: item.price || 0,
        quantity: item.quantity || 0
      }))
    };
    
    console.log('Emitting order:', emittedOrder);
    
    // Emit the order-created event and close the modal
    emit('order-created', emittedOrder);
    emit('close');
  } catch (error) {
    console.error('Error creating order:', error);
    showError('Failed to create order');
  }
}

// Initialize component
onMounted(async () => {
  await Promise.all([
    fetchMenuItems(),
    fetchAvailableTables()
  ]);
  
  // Initialize form items after menu is loaded
  if (menuItems.value.length > 0) {
    form.value.items = menuItems.value.map(item => ({
      id: item.id,
      quantity: 0,
      notes: '',
      special_instructions: ''
    }));
  }
});
</script>
