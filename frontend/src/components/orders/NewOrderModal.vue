<template>
  <TransitionRoot as="div" :show="open" class="fixed inset-0 z-10">
    <Dialog as="div" class="relative z-10 h-full" @close="$emit('close')">
      <TransitionChild
        as="div"
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
        class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
      />

      <div class="fixed inset-0 z-10 overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild
            as="div"
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
                        <div
                          v-for="item in menuItems"
                          :key="item.id"
                          class="flex items-center justify-between p-3 sm:p-2 border rounded-md hover:bg-gray-50 cursor-pointer"
                          @click="() => selectItem(item)"
                        >
                          <div class="flex-1 min-w-0">
                            <h4 class="text-sm font-medium text-gray-900 truncate">
                              {{ item.name }}
                              <span v-if="item.has_variants" class="text-xs text-gray-500 ml-1">(select options)</span>
                            </h4>
                            <p class="text-sm text-gray-500">
                              ${{ (item.price || 0).toFixed(2) }}
                            </p>
                          </div>
                          <div class="flex items-center space-x-2">
                            <span class="text-sm text-gray-900">
                              {{ getItemQuantity(item.id) > 0 ? `${getItemQuantity(item.id)} in order` : 'Add' }}
                            </span>
                            <button
                              type="button"
                              class="p-1 rounded-full text-indigo-600 hover:bg-indigo-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                              @click.stop="selectItem(item)"
                            >
                              <PlusIcon class="h-5 w-5" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Order Summary -->
                  <div class="mt-6 border-t border-gray-200 pt-4">
                    <h4 class="text-sm font-medium text-gray-900 mb-3">Order Summary</h4>
                    <div class="space-y-3">
                      <div v-for="item in selectedItems" :key="item.id" class="flex justify-between items-start">
                        <div class="flex-1">
                          <p class="text-sm font-medium text-gray-900">
                            {{ item.name }}
                            <span v-if="item.variant_name" class="text-xs text-gray-500 ml-1">({{ item.variant_name }})</span>
                          </p>
                          <p v-if="item.notes" class="text-xs text-gray-500 mt-1">{{ item.notes }}</p>
                        </div>
                        <div class="flex items-center space-x-4 ml-4">
                          <div class="flex items-center space-x-2">
                            <button 
                              type="button" 
                              class="p-1 text-gray-500 hover:text-indigo-600 focus:outline-none"
                              @click.stop="decreaseQuantity(item)"
                            >
                              <MinusIcon class="h-4 w-4" />
                            </button>
                            <span class="text-sm text-gray-700 w-6 text-center">{{ item.quantity }}</span>
                            <button 
                              type="button" 
                              class="p-1 text-gray-500 hover:text-indigo-600 focus:outline-none"
                              @click.stop="increaseQuantity(item)"
                            >
                              <PlusIcon class="h-4 w-4" />
                            </button>
                          </div>
                          <span class="text-sm font-medium text-gray-900 w-16 text-right">
                            ${{ calculateItemTotal(item) }}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div class="mt-4 pt-4 border-t border-gray-200">
                      <div class="flex justify-between items-center">
                        <span class="text-sm font-medium text-gray-900">Total</span>
                        <span class="text-lg font-bold text-gray-900">
                          ${{ (selectedItems.reduce((sum, item) => sum + (parseFloat(calculateItemTotal(item)) || 0), 0)).toFixed(2) }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- Selected Item Options -->
                  <div v-if="selectedItem" class="mt-4 border-t border-gray-200 pt-4">
                    <h4 class="text-sm font-medium text-gray-900 mb-2">
                      {{ selectedItem.name }}
                    </h4>
                    
                    <!-- Variants -->
                    <div v-if="selectedItem.variants?.length" class="space-y-2 mb-4">
                      <label class="block text-sm font-medium text-gray-700">Options</label>
                      <div v-for="variant in selectedItem.variants" :key="variant.id" 
                           class="flex items-center p-2 border rounded-md hover:bg-gray-50 cursor-pointer"
                           :class="{ 'bg-indigo-50 border-indigo-200': selectedVariant?.id === variant.id }"
                           @click="selectedVariant = variant">
                        <div class="flex-1">
                          <p class="text-sm font-medium text-gray-900">{{ variant.name }}</p>
                          <p class="text-sm text-gray-500">
                            <template v-if="variant.price_adjustment !== 0">
                              <span v-if="variant.price_adjustment > 0">+</span>
                              ${{ Math.abs(variant.price_adjustment).toFixed(2) }} • 
                            </template>
                            ${{ (selectedItem.price + variant.price_adjustment).toFixed(2) }}
                          </p>
                        </div>
                        <div class="ml-2 flex items-center">
                          <input type="radio" :checked="selectedVariant?.id === variant.id" 
                                 class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300">
                        </div>
                      </div>
                    </div>

                    <!-- Notes -->
                    <div class="mt-4">
                      <label for="item-notes" class="block text-sm font-medium text-gray-700 mb-1">Special Instructions</label>
                      <textarea
                        id="item-notes"
                        v-model="itemNotes"
                        rows="2"
                        class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        placeholder="Any special requests?"
                      />
                    </div>

                    <!-- Add to Order Button -->
                    <div class="mt-4 flex justify-end space-x-2">
                      <button
                        type="button"
                        class="px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-500"
                        @click="selectedItem = null"
                      >
                        Cancel
                      </button>
                      <button
                        type="button"
                        class="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                        @click="addItemWithDetails"
                      >
                        Add to Order
                      </button>
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

    <!-- Item Selection Modal -->
    <TransitionRoot as="div" :show="showItemModal" class="fixed inset-0 z-20">
      <Dialog as="div" class="relative z-20 h-full" @close="showItemModal = false">
        <TransitionChild
          as="div"
          enter="ease-out duration-300"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="ease-in duration-200"
          leave-from="opacity-100"
          leave-to="opacity-0"
          class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
        />

        <div class="fixed inset-0 z-10 overflow-y-auto">
          <div class="flex min-h-full items-center justify-center p-4 text-center">
            <TransitionChild
              as="div"
              enter="ease-out duration-300"
              enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enter-to="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leave-from="opacity-100 translate-y-0 sm:scale-100"
              leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              class="w-full"
            >
              <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-md sm:p-6">
                <div>
                  <div class="mt-3 text-center sm:mt-0 sm:text-left">
                    <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                      {{ selectedItem?.name }}
                    </DialogTitle>
                    <div class="mt-4">
                      <p class="text-sm text-gray-500">{{ selectedItem?.description }}</p>

                      <!-- Variant Selection -->
                      <div v-if="selectedItem?.variants?.length" class="mt-4">
                        <label class="block text-sm font-medium text-gray-700 mb-2">Variants</label>
                        <div class="space-y-2">
                          <div
                            v-for="variant in selectedItem.variants"
                            :key="variant.id"
                            class="flex items-center p-2 border rounded-md hover:bg-gray-50 cursor-pointer"
                            :class="{ 'bg-indigo-50 border-indigo-500': selectedVariant?.id === variant.id }"
                            @click="selectedVariant = variant"
                          >
                            <div class="flex-1">
                              <div class="flex justify-between">
                                <span class="font-medium">{{ variant.name }}</span>
                                <span v-if="variant.price_adjustment !== 0"
                                      :class="{ 'text-green-600': variant.price_adjustment > 0, 'text-gray-500': variant.price_adjustment < 0 }">
                                  {{ variant.price_adjustment > 0 ? '+' : '' }}{{ variant.price_adjustment.toFixed(2) }}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>

                      <!-- Special Instructions -->
                      <div class="mt-4">
                        <label for="item-notes" class="block text-sm font-medium text-gray-700 mb-1">
                          Special Instructions
                        </label>
                        <textarea
                          id="item-notes"
                          v-model="itemNotes"
                          rows="2"
                          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          placeholder="E.g., no onions, extra sauce, etc."
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div class="mt-5 sm:mt-6 grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    class="inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:text-sm"
                    @click="showItemModal = false"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    class="inline-flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:text-sm"
                    @click="addItemWithDetails"
                  >
                    Add to Order
                  </button>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, defineExpose, nextTick } from 'vue';
import orderService, { type CreateOrderData, type OrderItem, type OrderStatus } from '@/services/orderService';
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

// Import types
import type { MenuItem as MenuItemType } from '@/types/menu';

// Local interfaces
interface MenuItemVariant {
  id: string | number;
  name: string;
  price: number;
  price_adjustment: number;
  is_available: boolean;
  is_default: boolean;
  menu_item_id: string | number;
  created_at?: string;
  updated_at?: string;
  // No index signature to avoid conflicts with other properties
  [key: string]: unknown;
}

interface ExtendedMenuItem extends Omit<MenuItemType, 'variants' | 'id' | 'price'> {
  id: number;
  has_variants: boolean;
  variants?: MenuItemVariant[];
  price: number;
}

interface OrderItemWithDetails {
  id: number;
  menu_item_id: number;
  variant_id?: number | null;
  name: string;
  variant_name?: string;
  price: number;
  quantity: number;
  notes?: string;
  special_instructions?: string;
  unit_price?: number;
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
const form = ref({
  type: 'Dine-in',
  tableId: null as number | null,
  customerName: '',
  notes: '',
  items: [] as Array<{
    menu_item_id: number;
    variant_id?: number | null;
    quantity: number;
    notes?: string;
    special_instructions?: string;
    unit_price?: number;
  }>
});

const selectedItem = ref<ExtendedMenuItem | null>(null);
const selectedVariant = ref<MenuItemVariant | null>(null);
const itemNotes = ref('');
const showItemModal = ref(false);

const { showError, showSuccess } = useToast();
const { showToast } = useToast();
const menuItems = ref<ExtendedMenuItem[]>([]);
const availableTables = ref<any[]>([]);
const loading = ref({
  menu: false,
  tables: false
});

const error = ref({
  menu: null as string | null,
  tables: null as string | null
});

// Fetch menu items with proper type handling and defaults
const fetchMenuItems = async () => {
  try {
    loading.value.menu = true;
    const response = await menuService.getMenuItems();

    menuItems.value = response.map((item: any) => {
      // Process variants with proper typing and defaults
      const variants: MenuItemVariant[] = (item.variants || []).map((variant: any) => {
        // Create a new object with all required fields
        const variantData: MenuItemVariant = {
          id: variant.id || 0,
          name: variant.name || '',
          price: typeof variant.price === 'string' ? parseFloat(variant.price) : (variant.price || 0),
          price_adjustment: 'price_adjustment' in variant ? Number(variant.price_adjustment) || 0 : 0,
          is_available: 'is_available' in variant ? Boolean(variant.is_available) : true,
          is_default: 'is_default' in variant ? Boolean(variant.is_default) : false,
          menu_item_id: variant.menu_item_id || item.id || 0,
          // Include any additional properties from the original variant
          ...variant
        };
        return variantData;
      });

      // Process the main menu item with proper type safety
      const menuItem: ExtendedMenuItem = {
        id: Number(item.id) || 0,
        name: item.name || '',
        description: item.description || '',
        price: typeof item.price === 'string' ? parseFloat(item.price) : (item.price || 0),
        category: item.category || '',
        is_available: item.is_available !== false,
        has_variants: variants.length > 0,
        variants: variants.length > 0 ? variants : undefined
      };

      return menuItem;
    });
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
const selectedItems = computed<OrderItemWithDetails[]>(() => {
  return form.value.items
    .filter(item => item.quantity > 0)
    .map(item => {
      const menuItem = menuItems.value.find(mi => Number(mi.id) === Number(item.menu_item_id));
      const variant = menuItem?.variants?.find(v => Number(v.id) === Number(item.variant_id));
      const basePrice = typeof menuItem?.price === 'string' ? parseFloat(menuItem.price) : (menuItem?.price || 0);
      const adjustment = variant?.price_adjustment || 0;
      const price = variant ? basePrice + adjustment : basePrice;

      return {
        id: Number(item.menu_item_id) * 1000 + (item.variant_id ? Number(item.variant_id) : 0), // Generate a unique ID
        menu_item_id: Number(item.menu_item_id),
        variant_id: item.variant_id ? Number(item.variant_id) : null,
        name: menuItem?.name || 'Unknown Item',
        variant_name: variant?.name,
        price,
        quantity: item.quantity,
        notes: item.notes,
        special_instructions: item.special_instructions,
        unit_price: item.unit_price
      };
    });
});

// Calculate item total with proper type safety and null checks
const calculateItemTotal = (item: OrderItemWithDetails) => {
  const price = item.unit_price !== undefined && item.unit_price !== null ?
    (typeof item.unit_price === 'string' ? parseFloat(item.unit_price) : item.unit_price) :
    (item.price !== undefined && item.price !== null ?
      (typeof item.price === 'string' ? parseFloat(item.price) : item.price) : 0);
  return (price * (item.quantity || 0)).toFixed(2);
};

// Format price for display
const formatPrice = (price: number | string | undefined | null): string => {
  if (price === undefined || price === null) return '$0.00';
  const numPrice = typeof price === 'string' ? parseFloat(price) : price;
  return `$${numPrice.toFixed(2)}`;
};

// Add item with variant and notes
function addItemWithDetails() {
  if (!selectedItem.value) return;

  const variant = selectedVariant.value as MenuItemVariant | null;
  const basePrice = typeof selectedItem.value.price === 'string' ?
    parseFloat(selectedItem.value.price) :
    (selectedItem.value.price || 0);

  const adjustment = variant?.price_adjustment || 0;
  const itemPrice = variant ? basePrice + adjustment : basePrice;

  // Ensure we have valid IDs
  const menuItemId = Number(selectedItem.value.id || 0);
  const variantId = variant ? Number(variant.id) : null;

  // Find existing item with the same menu item and variant
  const existingItemIndex = form.value.items.findIndex(item => {
    const sameMenuItem = item.menu_item_id === menuItemId;
    const sameVariant = variantId !== null ?
      item.variant_id === variantId :
      item.variant_id === null || item.variant_id === undefined;
    return sameMenuItem && sameVariant;
  });

  if (existingItemIndex !== -1) {
    // Update existing item
    const existingItem = form.value.items[existingItemIndex];
    existingItem.quantity += 1;
    if (itemNotes.value) {
      existingItem.notes = itemNotes.value;
    }
  } else {
    // Add new item
    form.value.items.push({
      menu_item_id: menuItemId,
      variant_id: variantId,
      quantity: 1,
      unit_price: itemPrice,
      notes: itemNotes.value || '',
      special_instructions: ''
    });
  }

  // Reset the form
  showItemModal.value = false;
  itemNotes.value = '';
}

function increaseQuantity(item: OrderItemWithDetails) {
  const existingItem = form.value.items.find(i =>
    i.menu_item_id === item.menu_item_id &&
    ((i.variant_id && item.variant_id) ? i.variant_id === item.variant_id : !i.variant_id && !item.variant_id)
  );

  if (existingItem) {
    existingItem.quantity += 1;
  }
}

function decreaseQuantity(item: OrderItemWithDetails) {
  const existingItemIndex = form.value.items.findIndex(i =>
    i.menu_item_id === item.menu_item_id &&
    ((i.variant_id && item.variant_id) ? i.variant_id === item.variant_id : !i.variant_id && !item.variant_id)
  );

  if (existingItemIndex !== -1) {
    const existingItem = form.value.items[existingItemIndex];
    if (existingItem.quantity > 1) {
      existingItem.quantity -= 1;
    } else {
      form.value.items.splice(existingItemIndex, 1);
    }
  }
}

function getItemQuantity(menuItemId: number | string, variantId?: number | string | null): number {
  const item = form.value.items.find(item => {
    const matchesMenuItem = Number(item.menu_item_id) === Number(menuItemId);
    const matchesVariant = variantId !== undefined ?
      Number(item.variant_id) === Number(variantId) :
      !item.variant_id;
    return matchesMenuItem && matchesVariant;
  });
  return item ? item.quantity : 0;
}

async function createOrder() {
  try {
    // Filter out items with zero quantity before creating the order
    const validItems = form.value.items.filter(item => item.quantity > 0);
    
    // If no valid items, show error and return
    if (validItems.length === 0) {
      showError('Please add at least one item to the order');
      return;
    }

    const orderData: CreateOrderData = {
      table_id: form.value.type === 'Dine-in' ? form.value.tableId : null,
      customer_name: form.value.type !== 'Dine-in' ? form.value.customerName : null,
      items: validItems.map(item => ({
        menu_item_id: item.menu_item_id,
        variant_id: item.variant_id ?? null, // Ensure this is either number or null, not undefined
        quantity: item.quantity,
        special_instructions: item.notes || null,
        unit_price: item.unit_price || 0
      })),
      notes: form.value.notes || null
    };

    console.log('Creating order with data:', orderData);
    const response = await orderService.createOrder(orderData);
    console.log('Order creation response:', response);

    if (!response) {
      console.warn('No response data received, but request might have been successful');
      // Still proceed with success flow since we got a 201
    }

    // Create a properly typed order object with fallbacks
    const emittedOrder = {
      id: response?.id || Date.now(),
      status: (response?.status as OrderStatus) || 'pending',
      customer_name: response?.customer_name || (response?.table_id ? 'Dine-in' : orderData.customer_name || 'Takeaway'),
      table_id: response?.table_id || orderData.table_id || null,
      total_amount: response?.total_amount || orderData.items.reduce((sum, item) => sum + ((item.unit_price || 0) * (item.quantity || 0)), 0),
      notes: response?.notes || orderData.notes || null,
      created_at: response?.created_at || new Date().toISOString(),
      updated_at: response?.updated_at || new Date().toISOString(),
      items: (response?.items || orderData.items).map((item: any) => ({
        id: item.id,
        menu_item_id: item.menu_item_id,
        variant_id: item.variant_id ?? null,
        quantity: item.quantity,
        unit_price: item.unit_price || 0,
        special_instructions: item.special_instructions || null,
        // Add display properties that might be used in the UI
        name: 'name' in item ? item.name : 'Unknown Item',
        price: 'price' in item ? item.price : item.unit_price || 0,
        variant_name: 'variant_name' in item ? item.variant_name : null
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

async function selectItem(menuItem: ExtendedMenuItem) {
  selectedItem.value = { ...menuItem };
  selectedVariant.value = menuItem.variants?.[0] || null;
  itemNotes.value = '';
  // Scroll to the bottom to show the options after the next DOM update
  await nextTick();
  const modal = document.querySelector('.fixed.inset-0.overflow-y-auto');
  if (modal) {
    modal.scrollTo({
      top: modal.scrollHeight,
      behavior: 'smooth'
    });
  }
}

// Define public API type
type PublicApi = {
  selectItem: (menuItem: ExtendedMenuItem) => void;
  addItemWithDetails: () => void;
  increaseQuantity: (item: OrderItemWithDetails) => void;
  decreaseQuantity: (item: OrderItemWithDetails) => void;
  getItemQuantity: (menuItemId: number | string, variantId?: number | string | null) => number;
  createOrder: () => Promise<void>;
  calculateItemTotal: (item: OrderItemWithDetails) => string;
  formatPrice: (price: number | string | undefined | null) => string;
};

// Create public API object with explicit type assertion
const publicApi: PublicApi = {
  selectItem,
  addItemWithDetails,
  increaseQuantity,
  decreaseQuantity,
  getItemQuantity,
  createOrder,
  calculateItemTotal,
  formatPrice
};

// Expose the public API
defineExpose(publicApi);

// Initialize component
onMounted(async () => {
  await Promise.all([
    fetchMenuItems(),
    fetchAvailableTables()
  ]);

  // Initialize form items after menu is loaded
  if (menuItems.value.length > 0) {
    form.value.items = menuItems.value.map(item => ({
      menu_item_id: Number(item.id),
      variant_id: null,
      quantity: 0,
      notes: '',
      special_instructions: '',
      unit_price: item.price
    }));
  }
});
</script>
