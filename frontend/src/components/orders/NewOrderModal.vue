<template>
  <TransitionRoot as="div" :show="open" class="fixed inset-0 z-[10001]">
    <Dialog as="div" class="relative z-[10001] h-full" :open="open" @close="handleModalClose">
      <TransitionChild as="div" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100"
        leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0"
        class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />

      <div class="fixed inset-0 z-10 overflow-y-auto">
        <div class="flex h-full sm:min-h-full items-stretch sm:items-center justify-center p-0 sm:p-4 text-center">
          <TransitionChild as="div" enter="ease-out duration-300"
            enter-from="opacity-0 translate-y-full sm:translate-y-0 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-full sm:translate-y-0 sm:scale-95"
            class="w-full h-full sm:w-auto sm:h-auto">
            <DialogPanel
              class="relative flex flex-col transform overflow-hidden bg-white dark:bg-gray-900 text-left shadow-xl transition-all w-full h-full sm:h-auto sm:max-h-[90vh] sm:my-8 sm:max-w-4xl rounded-none sm:rounded-lg border-0 sm:border border-gray-200 dark:border-gray-800">
              <!-- FIXED HEADER -->
              <div class="flex-shrink-0 px-4 pt-4 sm:px-6 sm:pt-5">
                <div class="flex items-center justify-between">
                  <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900 dark:text-gray-100">
                    {{ isEditMode ? $t('app.views.orders.modals.new_order.title_edit_order', {
                      id:
                        orderToEdit?.order_number
                    }) : $t('app.views.orders.modals.new_order.title') }}
                  </DialogTitle>
                  <button type="button"
                    class="rounded-md bg-white dark:bg-transparent text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                    @click="$emit('close')">
                    <span class="sr-only">{{ $t('app.views.orders.modals.new_order.close') }}</span>
                    <XMarkIcon class="h-6 w-6" aria-hidden="true" />
                  </button>
                </div>
              </div>

              <!-- TAB NAVIGATION -->
              <div class="flex-shrink-0 px-4 sm:px-6 mt-4">
                <TabNavigation
                  :tabs="[$t('app.views.orders.modals.new_order.tabs.order_info'), $t('app.views.orders.modals.new_order.tabs.menu_items'), $t('app.views.orders.modals.new_order.tabs.summary')]"
                  :active-tab="activeTab" @change="activeTab = $event" />
              </div>

              <!-- SCROLLABLE CONTENT -->
              <div class="flex-1 overflow-y-auto overflow-x-hidden px-4 sm:px-6 pb-6">
                <!-- Mobile: Item Options View (replaces menu) -->
                <ItemOptionsInline v-if="isMobile && showingItemOptions && selectedItem" :item="selectedItem"
                  :top-notes="topNotes"
                  :get-variant-price="(variant) => selectedItem ? getVariantPrice(selectedItem, variant) : 0"
                  @back="showingItemOptions = false; selectedItem = null"
                  @add="handleAddItemFromModal" />

                <!-- TAB 1: Order Info -->
                <div v-else-if="activeTab === 0" class="mt-6">
                  <OrderTypeSelector v-model="form" :tables="availableTables" :loading="loading.tables"
                    :error="error.tables" />
                </div>

                <!-- TAB 2: Menu Items & Diners -->
                <div v-else-if="activeTab === 1" class="mt-6 space-y-4">
                  <!-- Persons Manager at the top -->
                  <PersonsManager :order-type="form.type" :persons="persons"
                    :active-person-index="activePersonIndex"
                    :disabled="isEditMode"
                    @update:active-person-index="activePersonIndex = $event" @add-person="addPerson"
                    @remove-person="removePersonWithConfirm" @update-person-name="updatePersonName" />

                  <!-- Active Diner Items Summary -->
                  <DinerItemsSummary v-if="persons[activePersonIndex]"
                    :title="persons[activePersonIndex].name || $t('app.views.orders.modals.new_order.persons.person_label', { position: persons[activePersonIndex].position })"
                    :items="persons[activePersonIndex].items" 
                    :get-menu-item-name="getMenuItemName"
                    :get-menu-item-category="getMenuItemCategory"
                    :empty-message="$t('app.views.orders.modals.new_order.persons.no_items')"
                    @remove-group="removeGroupFromPerson" />

                  <!-- Menu Items Selector - Buttons View -->
                  <MenuItemsSelectorButtons :loading="loading.menu" :error="error.menu"
                    :category-names="categoryNames" :menu-items-by-category="menuItemsByCategory"
                    :get-item-quantity="getItemQuantity" @select-item="selectItem" />
                </div>

                <!-- TAB 3: Summary & Payment -->
                <div v-else-if="activeTab === 2" class="mt-6 space-y-6">
                  <!-- Order Summary -->
                  <OrderSummary 
                    :use-multiple-diners="true" 
                    :persons="persons"
                    :selectedItems="selectedItems" 
                    :getMenuItemName="getMenuItemName"
                    :getMenuItemCategory="getMenuItemCategory"
                    :calculateItemTotal="calculateItemTotal" 
                    :isItemLocked="isItemLocked"
                    @removeItem="removeItemFromPerson" 
                    @decreaseQuantity="decreaseQuantity"
                    @increaseQuantity="increaseQuantity" 
                  />

                  <!-- Payment Section in Tab 3 -->
                  <PaymentSection :is-edit-mode="isEditMode" :can-process-payments="canProcessPayments"
                    :order-total="orderTotal" v-model:mark-as-paid="markAsPaid"
                    v-model:selected-payment-method="selectedPaymentMethod"
                    v-model:cash-received="cashReceived" />
                </div>
              </div>

              <!-- FOOTER - Only show create button on Tab 3 -->
              <div v-if="activeTab === 2"
                class="flex-shrink-0 px-4 pt-4 pb-4 sm:px-6 sm:pt-6 sm:pb-6 border-t border-gray-200 dark:border-gray-700">
                <button type="button"
                  class="w-full inline-flex justify-center rounded-lg bg-indigo-600 px-4 py-3 text-base font-semibold text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  :disabled="!hasItems || (form.type === 'Dine-in' && !form.tableId) || (form.type !== 'Dine-in' && !form.customerName)"
                  @click="createOrder">
                  {{ isEditMode ? $t('app.views.orders.modals.new_order.update_order') :
                    $t('app.views.orders.modals.new_order.create_order') }}
                </button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>

  <!-- Item Options Modal (teleported to body) -->
  <Teleport to="body">
    <ItemOptionsModal :is-open="showItemOptionsModal" :item="selectedItem" :top-notes="topNotes"
      @close="showItemOptionsModal = false" @add="handleAddItemFromModal" />
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, defineExpose, nextTick, watch } from 'vue';
import orderService, { type CreateOrderData, type OrderItem, type Order as OrderType } from '@/services/orderService';
import menuService from '@/services/menuService';
import tableService from '@/services/tableService';
import specialNotesService from '@/services/specialNotesService';
import { useToast } from '@/composables/useToast';
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  TransitionChild,
  TransitionRoot
} from '@headlessui/vue';
import { XMarkIcon, PlusIcon, MinusIcon, ChevronDownIcon } from '@heroicons/vue/24/outline';
import { useI18n } from 'vue-i18n';
import SpecialNotesBuilder from './SpecialNotesBuilder.vue';
import ExtrasSelector from './ExtrasSelector.vue';
import type { MenuItemIngredients } from '../menu/IngredientsManager.vue';
import type { Extra } from './ExtrasSelector.vue';
import { usePermissions } from '@/composables/usePermissions';

// Import new components
import OrderTypeSelector from './OrderTypeSelector.vue';
import PersonsManager from './PersonsManager.vue';
import PaymentSection from './PaymentSection.vue';
import ItemOptionsModal from './ItemOptionsModal.vue';
import MenuItemsSelector from './MenuItemsSelector.vue';
import MenuItemsSelectorButtons from './MenuItemsSelectorButtons.vue';
import OrderSummary from './OrderSummary.vue';
import ItemOptionsInline from './ItemOptionsInline.vue';
import TabNavigation from '../ui/TabNavigation.vue';
import DinerItemsSummary from './DinerItemsSummary.vue';
import GroupedItemsList from './GroupedItemsList.vue';

// Import types
import type { ExtendedMenuItem, MenuItemVariant, OrderItemWithDetails } from '@/types/order';
import { useMenuCategories } from '@/composables/useMenuCategories';
import { useOrderItems } from '@/composables/useOrderItems';
import { useItemSelection } from '@/composables/useItemSelection';
import { useMultipleDiners } from '@/composables/useMultipleDiners';
import { useOrderCreation } from '@/composables/useOrderCreation';
import { useDataFetching } from '@/composables/useDataFetching';
import { useItemGrouping } from '@/composables/useItemGrouping';
import { getEffectivePrice, getVariantPrice, getMenuItemName as getMenuItemNameUtil, getMenuItemCategory as getMenuItemCategoryUtil } from '@/utils/priceHelpers';
import {
  transformMenuItemFromAPI,
  transformTableFromAPI,
  transformToOrderItemWithDetails,
  mapOrderTypeToFrontend,
  mapOrderTypeToBackend,
  createInitialFormItem,
  validateOrderForm
} from '@/utils/orderFormHelpers';

// Props and Emits
const props = defineProps<{
  open: boolean;
  tableId?: number | null;
  mode?: 'create' | 'edit';
  orderToEdit?: OrderType | null;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'order-created', order: any): void;
  (e: 'order-updated', order: any): void;
}>();

// Form data
const form = ref({
  type: 'Dine-in',
  tableId: null as number | string | null,
  customerName: '',
  notes: '',
  items: [] as Array<{
    menu_item_id: number;
    variant_id?: number | null;
    quantity: number;
    notes?: string;
    special_instructions?: string;
    unit_price?: number;
    extras?: Extra[];
  }>
});

const topNotes = ref<string[]>([]);
const isEditMode = computed(() => {
  return (props.mode || 'create') === 'edit' && !!props.orderToEdit
});

// Tab navigation
const activeTab = ref(0);

// Detect if we're on mobile
const isMobile = ref(false);
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768;
};
onMounted(() => {
  checkMobile();
  window.addEventListener('resize', checkMobile);
});

// Use multiple diners composable (always enabled)
const multipleDinersComposable = useMultipleDiners();
const {
  persons,
  activePersonIndex,
  addPerson,
  removePerson,
  updatePersonName,
  removeItemFromPerson: removeItemFromPersonComposable
} = multipleDinersComposable;

const { showError, showSuccess, showWarning, showToast } = useToast();
const { canProcessPayments } = usePermissions();
const { t } = useI18n();

// Use data fetching composable
const dataFetching = useDataFetching();
const { menuItems, availableTables, loading, error } = dataFetching;

// Payment state
const markAsPaid = ref(false);
const selectedPaymentMethod = ref<'cash' | 'card' | 'digital' | 'other'>('cash');
const cashReceived = ref<number>(0);

// Use composables
const {
  expandedCategories,
  menuItemsByCategory,
  categoryNames,
  toggleCategory,
  isCategoryExpanded,
  collapseAllCategories
} = useMenuCategories(menuItems);

const {
  increaseQuantity,
  decreaseQuantity,
  getItemQuantity,
  calculateItemTotal,
  isItemLocked
} = useOrderItems(computed(() => form.value.items));

const {
  selectedItem,
  selectedVariant,
  itemNotes,
  itemSpecialNote,
  itemExtras,
  showItemModal,
  showItemOptionsModal,
  showingItemOptions,
  resetItemSelection,
  selectItem: selectItemFromComposable
} = useItemSelection();

// Calculate order total (always from persons)
const orderTotal = computed(() => {
  return persons.value.reduce((sum, person) => {
    return sum + person.items.reduce((itemSum, item) => {
      return itemSum + ((item.unit_price || 0) * item.quantity);
    }, 0);
  }, 0);
});

// Use order creation composable
const orderCreationComposable = useOrderCreation();

// Helper to initialize a fresh form state
function getInitialForm() {
  return {
    type: 'Dine-in',
    tableId: null as number | string | null,
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
  };
}

// Reset all local state of the modal
function resetForm() {
  // Reset base fields
  form.value = getInitialForm();
  selectedItem.value = null;
  selectedVariant.value = null;
  itemNotes.value = '';
  showItemModal.value = false;

  // Rebuild zero-quantity items list from current menu cache if available
  if (menuItems.value.length > 0) {
    form.value.items = menuItems.value.map(item => createInitialFormItem(item));
  }

  // Reset multiple diners state
  multipleDinersComposable.reset();
}

// Fetch menu items using composable
const fetchMenuItems = async () => {
  await dataFetching.fetchMenuItems(
    () => collapseAllCategories(), // onSuccess
    (errorMsg) => showError(t('app.views.orders.modals.new_order.error_menu')) // onError
  );
};

// Fetch available tables using composable
const fetchAvailableTables = async () => {
  await dataFetching.fetchAvailableTables(
    props.tableId,
    (tableId) => {
      // onTableSelected callback
      form.value.type = 'Dine-in';
      form.value.tableId = tableId;
    },
    (errorMsg) => showError(t('app.views.orders.modals.new_order.error_tables')) // onError
  );
};

// Hydrate form from existing order in edit mode
function loadOrderIntoForm(order: OrderType) {
  // Use helper to map order type
  const backendOrderType = (order as any).order_type || 'dine_in';
  form.value.type = mapOrderTypeToFrontend(backendOrderType);

  form.value.tableId = order.table_id ?? null;
  form.value.customerName = order.customer_name || '';
  form.value.notes = order.notes || '';

  // Load items into persons (always multiple diners mode)
  // Group items by person_id if available, otherwise put all in first person
  const itemsByPerson = new Map<number | null, any[]>();
  
  (order.items || []).forEach((it) => {
    const personId = it.person_id ?? null;
    if (!itemsByPerson.has(personId)) {
      itemsByPerson.set(personId, []);
    }
    itemsByPerson.get(personId)!.push({
      menu_item_id: it.menu_item_id,
      variant_id: it.variant_id ?? null,
      quantity: it.quantity,
      notes: it.special_instructions || undefined,
      special_instructions: it.special_instructions || undefined,
      unit_price: it.unit_price || it.menu_item?.price || 0,
      status: it.status || 'pending',
      person_id: personId,  // Preserve original person_id
    });
  });

  // If we have items grouped by person_id, create persons accordingly
  if (itemsByPerson.size > 0) {
    // Clear existing persons
    persons.value = [];
    
    // Sort person_ids to ensure consistent order (null first, then by numeric value)
    const sortedPersonIds = Array.from(itemsByPerson.keys()).sort((a, b) => {
      if (a === null) return -1;
      if (b === null) return 1;
      return a - b;
    });
    
    // Create a person for each group in sorted order
    let position = 1;
    sortedPersonIds.forEach((personId) => {
      const items = itemsByPerson.get(personId)!;
      persons.value.push({
        id: personId ?? undefined,  // Preserve original person_id from backend
        position,
        name: '',
        items
      });
      position++;
    });
    
    // Ensure at least one person exists
    if (persons.value.length === 0) {
      persons.value.push({
        position: 1,
        name: '',
        items: []
      });
    }
    
    // Always start with first person
    activePersonIndex.value = 0;
  }
}

// Computed properties
const selectedItems = computed<OrderItemWithDetails[]>(() => {
  return form.value.items
    .filter(item => item.quantity > 0)
    .map(item => transformToOrderItemWithDetails(item, menuItems.value));
});

// Convert selectedItems to OrderItem format for grouping composable
const selectedItemsAsOrderItems = computed(() => {
  return selectedItems.value.map((item, index) => ({
    id: item.id || index,
    menu_item_id: item.menu_item_id,
    variant_id: item.variant_id || null,
    quantity: item.quantity || 1,
    special_instructions: item.special_instructions || item.notes || null,
    status: (item as any).status || 'pending',
    order_id: 0,
    person_id: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    unit_price: item.unit_price || item.price || 0,
    variant: item.variant_name ? {
      id: item.variant_id || 0,
      name: item.variant_name,
      price: item.unit_price || 0,
      description: null
    } : null,
    menu_item: {
      id: item.menu_item_id,
      name: item.name || '',
      description: '',
      price: item.price || item.unit_price || 0,
      category: item.category || '',
      category_visible_in_kitchen: true,
      image_url: '',
      is_available: true
    },
    extras: []
  }));
});

// Use item grouping composable for simple mode
const { 
  groupedItems, 
  totalItemCount, 
  groupCount, 
  totalPrice: groupedTotalPrice,
  getFormattedInstructions 
} = useItemGrouping(selectedItemsAsOrderItems);

// Check if there are any items in the order
const hasItems = computed(() => {
  return persons.value.some(person => person.items.length > 0);
});

// Add item with variant and notes
function addItemWithDetails() {
  if (!selectedItem.value) return;

  const variant = selectedVariant.value as MenuItemVariant | null;

  // Determine the correct unit price: prefer variant.price if present
  const itemPrice = getVariantPrice(selectedItem.value, variant);

  // Ensure we have valid IDs
  const menuItemId = Number(selectedItem.value.id || 0);
  const variantId = variant ? Number(variant.id) : null;

  // Use itemSpecialNote if available, otherwise fallback to itemNotes
  const finalNote = itemSpecialNote.value || itemNotes.value;

  const newItem = {
    menu_item_id: menuItemId,
    variant_id: variantId,
    quantity: 1,
    unit_price: itemPrice,
    notes: finalNote || '',
    special_instructions: '',
    extras: itemExtras.value.length > 0 ? [...itemExtras.value] : []
  };

  // Agregar a la persona activa
  persons.value[activePersonIndex.value].items.push(newItem);

  // Reset the form
  showItemModal.value = false;
  itemNotes.value = '';
  itemSpecialNote.value = '';
  itemExtras.value = [];
}

// Multi-diner functions - Wrapped to add confirmation
function removePersonWithConfirm(index: number) {
  if (confirm(t('app.views.orders.modals.new_order.persons.confirm_remove'))) {
    removePerson(index);
  }
}

function removeItemFromPerson(personIndex: number, itemIndex: number) {
  removeItemFromPersonComposable(personIndex, itemIndex);
}

// Remove all items in a group from the active person
function removeGroupFromPerson(group: any) {
  const person = persons.value[activePersonIndex.value];
  if (!person) return;

  // Filter out all items that match this group's fingerprint
  // We need to remove items that have the same menu_item_id, variant_id, and special_instructions
  person.items = person.items.filter(item => {
    const itemMatches = 
      item.menu_item_id === group.menu_item_id &&
      (item.variant_id || null) === (group.variant_id || null) &&
      (item.special_instructions || null) === (group.special_instructions || null);
    return !itemMatches;
  });
}

async function createOrder() {
  try {
    // Collect all items from all persons (multiple diners mode)
    const validItems: any[] = [];
    persons.value.forEach(person => {
      person.items.forEach(item => {
        if (item.quantity > 0) {
          validItems.push(item);
        }
      });
    });

    // Validate items using composable
    const hasItems = orderCreationComposable.validateHasItems(
      true, // Always multiple diners mode
      persons.value,
      validItems
    );

    if (!hasItems) {
      showError(t('app.views.orders.modals.new_order.errors.add_one_item'));
      return;
    }

    if (isEditMode.value && props.orderToEdit) {
      // Update existing order using composable
      const updated = await orderCreationComposable.updateExistingOrder(
        props.orderToEdit.id,
        form.value,
        props.orderToEdit,
        validItems
      );

      emit('order-updated', updated);
      emit('close');
    } else {
      // Validate form using helper
      const validation = validateOrderForm(form.value, hasItems);
      if (!validation.isValid) {
        validation.errors.forEach(error => showError(error));
        return;
      }

      // Create new order using composable
      const { order, paymentSuccess } = await orderCreationComposable.createNewOrder(
        form.value,
        true, // Always multiple diners mode
        persons.value,
        validItems,
        markAsPaid.value,
        selectedPaymentMethod.value,
        cashReceived.value,
        orderTotal.value,
        t,
        showSuccess,
        showWarning,
        showError
      );

      // Always emit and close, regardless of payment success
      // If payment failed, the user already saw a warning message explaining what happened
      emit('order-created', order);
      emit('close');
    }
  } catch (error: any) {
    console.error('Error creating order:', error);
    // Don't show generic error if it's a validation error (user already saw specific message)
    if (error.message !== 'VALIDATION_ERROR') {
      showError(t('app.views.orders.modals.new_order.errors.create_failed'));
    }
  }
}

async function selectItem(menuItem: ExtendedMenuItem) {
  selectItemFromComposable(menuItem, isMobile.value);
}

// Handle adding item from modal or inline view
function handleAddItemFromModal(data: {
  item: any;
  variant: any | null;
  quantity: number;
  notes: string;
}) {
  const { item, variant, quantity, notes } = data;

  // Calculate price
  let price = 0;
  if (variant) {
    // If variant has absolute price, use it; otherwise use base + adjustment
    if (variant.price && variant.price > 0) {
      price = getEffectivePrice(variant.price, variant.discount_price);
    } else {
      const basePrice = item.price || 0;
      const adjustment = variant.price_adjustment || 0;
      const variantPrice = basePrice + adjustment;
      price = getEffectivePrice(variantPrice, variant.discount_price);
    }
  } else {
    price = getEffectivePrice(item.price || 0, item.discount_price);
  }

  // Always add to active person (multiple diners mode)
  const activePerson = persons.value[activePersonIndex.value];
  if (activePerson) {
    // Add individual items (quantity times)
    for (let i = 0; i < quantity; i++) {
      activePerson.items.push({
        menu_item_id: Number(item.id),
        variant_id: variant ? Number(variant.id) : null,
        variant: variant ? {
          id: Number(variant.id),
          name: variant.name,
          price: variant.price,
          price_adjustment: variant.price_adjustment,
          discount_price: variant.discount_price
        } : null,
        quantity: 1, // Always 1 for individual items
        special_instructions: notes || '',
        unit_price: price,
        extras: [],
        person_id: activePerson.id ?? null  // Assign person_id from active person
      });
    }
  }

  // Reset
  selectedItem.value = null;
  showItemOptionsModal.value = false;
}

// Handle modal close - only close if ItemOptionsModal is not open
function handleModalClose() {
  // Don't close if ItemOptionsModal is open
  if (showItemOptionsModal.value) {
    return;
  }
  // Otherwise, close normally
  emit('close');
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
};

// Create public API object with explicit type assertion
const publicApi: PublicApi = {
  selectItem,
  addItemWithDetails,
  increaseQuantity,
  decreaseQuantity,
  getItemQuantity,
  createOrder,
  calculateItemTotal
};

// Expose the public API
defineExpose(publicApi);



// Initialize component
onMounted(async () => {
  await Promise.all([
    fetchMenuItems(),
    fetchAvailableTables(),
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

  // If opened directly in edit mode with an order, hydrate immediately so items/totals render


  if (isEditMode.value && props.orderToEdit) {
    loadOrderIntoForm(props.orderToEdit);
  }
});

// If the full order data arrives after the modal is already open, hydrate then
watch(() => props.orderToEdit, (newOrder) => {


  if (isEditMode.value && newOrder && props.open) {
    loadOrderIntoForm(newOrder);
  }
});

// Keep modal state clean when toggling open prop
watch(() => props.open, (isOpen, wasOpen) => {
  if (!isOpen && wasOpen) {
    // Modal just closed -> ensure everything is reset
    resetForm();
  } else if (isOpen && !wasOpen) {
    // Modal just opened -> if items empty but menu loaded, initialize items
    if (form.value.items.length === 0 && menuItems.value.length > 0) {
      form.value.items = menuItems.value.map(item => ({
        menu_item_id: Number(item.id),
        variant_id: null,
        quantity: 0,
        notes: '',
        special_instructions: '',
        unit_price: item.price
      }));
    }
    // After tables list is already loaded, select the matching table id from the card
    if (props.tableId) {
      form.value.type = 'Dine-in';
      form.value.tableId = props.tableId;
    }
    if (isEditMode.value && props.orderToEdit) {
      loadOrderIntoForm(props.orderToEdit);
    }
  }
});

// Helper function to get menu item name
function getMenuItemName(menuItemId: number): string {
  return getMenuItemNameUtil(menuItems.value, menuItemId);
}

// Helper function to get menu item category
function getMenuItemCategory(menuItemId: number): string {
  return getMenuItemCategoryUtil(menuItems.value, menuItemId);
}

</script>
