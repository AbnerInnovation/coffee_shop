<template>
  <div class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <div class="p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900">
            New Order for Table #{{ tableNumber }}
          </h3>
          <button 
            @click="$emit('close')" 
            class="text-gray-400 hover:text-gray-500"
          >
            <span class="sr-only">Close</span>
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Menu Items Selection -->
        <div class="mb-6">
          <div class="flex justify-between items-center mb-2">
            <h4 class="text-sm font-medium text-gray-700">Menu Items</h4>
            <button 
              type="button" 
              @click="addNewItem"
              class="text-sm text-indigo-600 hover:text-indigo-500"
            >
              + Add Item
            </button>
          </div>
          
          <div v-for="(item, index) in orderItems" :key="index" class="mb-4 p-3 border rounded-lg">
            <div class="flex justify-between items-start mb-2">
              <div class="flex-1 mr-4">
                <select 
                  v-model="item.menu_item_id"
                  class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  required
                >
                  <option value="">Select an item</option>
                  <option v-for="menuItem in menuItems" :key="menuItem.id" :value="menuItem.id">
                    {{ menuItem.name }} - ${{ menuItem.price.toFixed(2) }}
                  </option>
                </select>
              </div>
              <div class="w-24">
                <input 
                  v-model.number="item.quantity" 
                  type="number" 
                  min="1" 
                  class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  required
                >
              </div>
              <button 
                type="button" 
                @click="removeItem(index)"
                class="ml-2 text-red-600 hover:text-red-500"
              >
                <span class="sr-only">Remove</span>
                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
            <div class="mt-2">
              <label class="block text-sm font-medium text-gray-700 mb-1">Special Instructions</label>
              <input 
                v-model="item.special_instructions"
                type="text" 
                class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                placeholder="E.g. No onions, extra sauce, etc."
              >
            </div>
          </div>
        </div>

        <!-- Order Notes -->
        <div class="mb-6">
          <label for="order-notes" class="block text-sm font-medium text-gray-700 mb-1">Order Notes</label>
          <textarea
            id="order-notes"
            v-model="orderNotes"
            rows="2"
            class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            placeholder="Any special instructions for the kitchen..."
          ></textarea>
        </div>

        <!-- Order Summary -->
        <div class="bg-gray-50 p-4 rounded-lg mb-6">
          <h4 class="text-sm font-medium text-gray-700 mb-3">Order Summary</h4>
          <div v-if="orderItems.length > 0" class="space-y-2">
            <div v-for="(item, index) in orderItems" :key="index" class="flex justify-between text-sm">
              <div class="text-gray-600">
                {{ getMenuItemName(item.menu_item_id) }} × {{ item.quantity }}
                <p v-if="item.special_instructions" class="text-xs text-gray-400">
                  {{ item.special_instructions }}
                </p>
              </div>
              <div class="font-medium">
                ${{ (getMenuItemPrice(item.menu_item_id) * item.quantity).toFixed(2) }}
              </div>
            </div>
            <div class="border-t border-gray-200 pt-2 mt-2">
              <div class="flex justify-between font-medium">
                <div>Total</div>
                <div>${{ calculateTotal().toFixed(2) }}</div>
              </div>
            </div>
          </div>
          <p v-else class="text-sm text-gray-500">
            Add items to the order
          </p>
        </div>

        <!-- Actions -->
        <div class="flex justify-end space-x-3">
          <button
            type="button"
            @click="$emit('close')"
            class="inline-flex justify-center rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            Cancel
          </button>
          <button
            type="button"
            @click="submitOrder"
            :disabled="isSubmitting || orderItems.length === 0"
            :class="{
              'opacity-50 cursor-not-allowed': isSubmitting || orderItems.length === 0,
              'bg-indigo-600 hover:bg-indigo-700': !isSubmitting,
              'bg-indigo-400': isSubmitting
            }"
            class="inline-flex justify-center rounded-md border border-transparent py-2 px-4 text-sm font-medium text-white shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            <span v-if="isSubmitting" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </span>
            <span v-else>Place Order</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, onMounted, computed } from 'vue';
import orderService, { 
  type OrderItem, 
  type Order, 
  type MenuItem, 
  type CreateOrderData, 
  type CreateOrderItemData 
} from '@/services/orderService';

const props = defineProps({
  tableId: {
    type: Number,
    required: true
  },
  tableNumber: {
    type: Number,
    required: true
  }
});

const emit = defineEmits(['close', 'order-created']);

const menuItems = ref<MenuItem[]>([]);
// This is the form data structure, not the final OrderItem type
interface OrderItemFormData extends Omit<CreateOrderItemData, 'menu_item_id' | 'variant_id'> {
  menu_item_id: number | string;
  variant_id: number | string | null;
}

const orderItems = ref<OrderItemFormData[]>([]);

const orderNotes = ref('');
const isSubmitting = ref(false);

// Fetch menu items when component mounts
onMounted(async () => {
  try {
    const response = await orderService.getMenuItems();
    menuItems.value = response;
  } catch (error) {
    console.error('Error fetching menu items:', error);
    // Handle error (show toast/notification)
  }
});

// Add new empty order item
const addNewItem = () => {
  orderItems.value.push({ 
    menu_item_id: '', 
    variant_id: null, 
    quantity: 1, 
    special_instructions: '',
    unit_price: 0
  });
};

// Remove order item
const removeItem = (index: number) => {
  if (orderItems.value.length > 1) {
    orderItems.value.splice(index, 1);
  }
};

// Get menu item name by ID
const getMenuItemName = (id: number | string) => {
  const item = menuItems.value.find(item => item.id === Number(id));
  return item ? item.name : 'Unknown Item';
};

const selectedMenuItem = (index: number) => {
  return menuItems.value.find(item => item.id === Number(orderItems.value[index].menu_item_id));
};

const updateUnitPrice = (index: number) => {
  const item = selectedMenuItem(index);
  if (item) {
    if (orderItems.value[index].variant_id) {
      const variant = item.variants?.find(v => v.id === Number(orderItems.value[index].variant_id));
      orderItems.value[index].unit_price = variant ? variant.price : item.price;
    } else {
      orderItems.value[index].unit_price = item.price;
    }
  }
};

// Get menu item price by ID
const getMenuItemPrice = (id: number | string, variantId?: number | string | null) => {
  const item = menuItems.value.find(item => item.id === Number(id));
  if (!item) return 0;
  
  if (variantId && item.variants) {
    const variant = item.variants.find(v => v.id === Number(variantId));
    return variant ? variant.price : item.price;
  }
  
  return item.price;
};

// Calculate order total
const calculateTotal = () => {
  return orderItems.value.reduce((total, item) => {
    if (!item.menu_item_id) return total;
    return total + (item.unit_price * item.quantity);
  }, 0);
};

// Submit order
const submitOrder = async () => {
  if (orderItems.value.length === 0) return;
  
  // Validate all items have a menu item selected
  const invalidItems = orderItems.value.some(item => !item.menu_item_id);
  if (invalidItems) {
    alert('Please select a menu item for all order items');
    return;
  }

  try {
    isSubmitting.value = true;
    
    const orderData: CreateOrderData = {
      table_id: props.tableId,
      items: orderItems.value
        .filter(item => item.menu_item_id && item.quantity > 0)
        .map(item => ({
          menu_item_id: Number(item.menu_item_id),
          variant_id: item.variant_id ? Number(item.variant_id) : null,
          quantity: item.quantity,
          special_instructions: item.special_instructions || null,
          unit_price: item.unit_price
        })),
      notes: orderNotes.value || null,
      customer_name: null,
      user_id: null
    };

    const createdOrder = await orderService.createOrder(orderData);
    emit('order-created', createdOrder);
    emit('close');
  } catch (error) {
    console.error('Error creating order:', error);
    alert('Failed to create order. Please try again.');
  } finally {
    isSubmitting.value = false;
  }
};
</script>
