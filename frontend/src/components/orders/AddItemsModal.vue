<template>
  <TransitionRoot as="div" :show="open" class="fixed inset-0 z-[10001]">
    <Dialog as="div" class="relative z-[10001] h-full" @close="$emit('close')">
      <TransitionChild as="div" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100"
        leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0"
        class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />

      <div class="fixed inset-0 z-10 overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild as="div" enter="ease-out duration-300"
            enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel
              class="relative transform overflow-hidden bg-white mt-10 dark:bg-gray-900 px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-20 w-screen max-w-screen sm:max-w-4xl sm:w-full sm:p-6 mx-0 sm:mx-0 rounded-none sm:rounded-lg border border-gray-200 dark:border-gray-800">
              <div class="flex items-center justify-between">
                <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900 dark:text-gray-100">
                  {{ $t('app.views.orders.add_items_modal.title', { tableNumber: tableNumber, orderId: orderId }) }}
                </DialogTitle>
                <button type="button"
                  class="rounded-md bg-white dark:bg-transparent text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                  @click="$emit('close')">
                  <span class="sr-only">{{ $t('app.actions.close') }}</span>
                  <XMarkIcon class="h-6 w-6" aria-hidden="true" />
                </button>
              </div>

              <!-- Info Banner -->
              <div class="mt-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md p-3">
                <div class="flex">
                  <InformationCircleIcon class="h-5 w-5 text-blue-400" aria-hidden="true" />
                  <div class="ml-3">
                    <p class="text-sm text-blue-700 dark:text-blue-300">
                      {{ $t('app.views.orders.add_items_modal.info') }}
                    </p>
                  </div>
                </div>
              </div>

              <div class="mt-6">
                <!-- Menu Items Selection -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    {{ $t('app.views.orders.add_items_modal.select_items') }}
                  </label>
                  <div v-if="loading.menu" class="text-center py-8">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto"></div>
                    <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">{{ $t('app.views.orders.modals.new_order.loading_menu') }}</p>
                  </div>
                  <div v-else-if="error.menu" class="text-center py-8 text-red-600">
                    <p>{{ $t('app.views.orders.modals.new_order.error_menu') }}</p>
                  </div>
                  <div v-else class="space-y-3 max-h-[50vh] overflow-y-auto pr-1 -mr-1">
                    <!-- Category sections -->
                    <div v-for="category in categoryNames" :key="category" class="border-b border-gray-200 dark:border-gray-700 pb-3 mb-3 last:border-b-0 last:pb-0 last:mb-0">
                      <!-- Category Header -->
                      <button
                        @click="toggleCategory(category)"
                        class="flex items-center justify-between w-full p-2 text-left hover:bg-gray-50 dark:hover:bg-gray-700 rounded-md transition-colors"
                        :class="{ 'bg-indigo-50 dark:bg-indigo-900/20': isCategoryExpanded(category) }"
                      >
                        <h3 class="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {{ category }}
                          <span class="text-xs text-gray-500 ml-2">({{ menuItemsByCategory[category].length }})</span>
                        </h3>
                        <ChevronDownIcon
                          class="h-4 w-4 text-gray-500 transition-transform"
                          :class="{ 'rotate-180': !isCategoryExpanded(category) }"
                        />
                      </button>

                      <!-- Category Items -->
                      <div v-if="isCategoryExpanded(category)" class="mt-2 space-y-2 pl-2">
                        <div v-for="item in menuItemsByCategory[category]" :key="item.id"
                          class="flex items-center justify-between p-2 border rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                          @click="() => selectItem(item)">
                          <div class="flex-1 min-w-0">
                            <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                              {{ item.name }}
                              <span v-if="item.has_variants" class="text-xs text-gray-500 ml-1">{{ $t('app.views.orders.modals.new_order.select_options_hint') }}</span>
                            </h4>
                            <div class="flex items-center gap-2">
                              <p 
                                v-if="item.discount_price && item.discount_price > 0"
                                class="text-sm text-gray-500 dark:text-gray-400 line-through"
                              >
                                ${{ (item.price || 0).toFixed(2) }}
                              </p>
                              <p 
                                class="text-sm font-medium"
                                :class="item.discount_price && item.discount_price > 0 ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'"
                              >
                                ${{ getEffectivePrice(item.price || 0, item.discount_price).toFixed(2) }}
                              </p>
                              <span 
                                v-if="item.discount_price && item.discount_price > 0"
                                class="inline-flex items-center rounded-full bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 text-xs font-medium text-green-800 dark:text-green-200"
                              >
                                {{ $t('app.forms.sale_badge') }}
                              </span>
                            </div>
                          </div>
                          <div class="flex items-center space-x-2">
                            <span class="text-sm text-gray-900 dark:text-gray-200">
                              {{ getItemQuantity(item.id) > 0 ? $t('app.views.orders.modals.new_order.in_order', { count: getItemQuantity(item.id) }) : $t('app.views.orders.modals.new_order.add') }}
                            </span>
                            <button type="button"
                              class="p-1 rounded-full text-indigo-600 hover:bg-indigo-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                              @click.stop="selectItem(item)">
                              <PlusIcon class="h-5 w-5" />
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Selected Items Summary -->
                <div v-if="selectedItems.length > 0" class="mt-6 border-t border-gray-200 dark:border-gray-700 pt-4">
                  <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">
                    {{ $t('app.views.orders.add_items_modal.items_to_add') }} ({{ selectedItems.length }})
                  </h4>
                  <div class="space-y-2 max-h-40 overflow-y-auto">
                    <div v-for="(item, index) in selectedItems" :key="index"
                      class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded-md">
                      <div class="flex-1">
                        <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ item.name }}</p>
                        <p v-if="item.variant" class="text-xs text-gray-500 dark:text-gray-400">{{ item.variant.name }}</p>
                        <p v-if="item.special_instructions" class="text-xs text-gray-500 dark:text-gray-400 italic">{{ item.special_instructions }}</p>
                      </div>
                      <div class="flex items-center space-x-3">
                        <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {{ item.quantity }}x ${{ item.unit_price.toFixed(2) }}
                        </span>
                        <button type="button"
                          class="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
                          @click="removeItem(index)">
                          <XMarkIcon class="h-5 w-5" />
                        </button>
                      </div>
                    </div>
                  </div>
                  <div class="mt-3 flex items-center justify-between border-t border-gray-200 dark:border-gray-700 pt-3">
                    <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ $t('app.views.orders.add_items_modal.total') }}:</span>
                    <span class="text-lg font-bold text-gray-900 dark:text-gray-100">${{ totalAmount.toFixed(2) }}</span>
                  </div>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="mt-6 flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-3 space-y-3 space-y-reverse sm:space-y-0">
                <button type="button"
                  class="inline-flex w-full justify-center rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2 text-base font-medium text-gray-700 dark:text-gray-300 shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto sm:text-sm"
                  @click="$emit('close')">
                  {{ $t('app.actions.cancel') }}
                </button>
                <button type="button"
                  class="inline-flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                  :disabled="selectedItems.length === 0 || submitting"
                  @click="handleSubmit">
                  <span v-if="submitting" class="flex items-center">
                    <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ $t('app.actions.adding') }}
                  </span>
                  <span v-else>{{ $t('app.views.orders.add_items_modal.add_items_button') }}</span>
                </button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>

    <!-- Item Selection Modal (for variants and special instructions) -->
    <TransitionRoot as="div" :show="showItemModal" class="fixed inset-0 z-[10002]">
      <Dialog as="div" class="relative z-[10002] h-full" @close="showItemModal = false">
        <TransitionChild as="div" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100"
          leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0"
          class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />

        <div class="fixed inset-0 z-10 overflow-y-auto">
          <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <TransitionChild as="div" enter="ease-out duration-300"
              enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200"
              leave-from="opacity-100 translate-y-0 sm:scale-100"
              leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
              <DialogPanel
                class="relative transform overflow-hidden rounded-lg bg-white dark:bg-gray-900 px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                <div>
                  <div class="mt-3 text-center sm:mt-5">
                    <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900 dark:text-gray-100">
                      {{ selectedMenuItem?.name }}
                    </DialogTitle>
                    <div class="mt-4 space-y-4">
                      <!-- Variants -->
                      <div v-if="selectedMenuItem?.has_variants && selectedMenuItem?.variants?.length">
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 text-left mb-2">
                          {{ t('app.views.orders.modals.new_order.variants') }}
                        </label>
                        <select v-model="selectedVariantId"
                          class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm">
                          <option :value="null">{{ t('app.views.orders.modals.new_order.base_item') }}</option>
                          <option v-for="variant in selectedMenuItem.variants" :key="variant.id" :value="variant.id">
                            {{ variant.name }} - ${{ variant.price.toFixed(2) }}
                          </option>
                        </select>
                      </div>

                      <!-- Quantity -->
                      <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 text-left mb-2">
                          {{ t('app.forms.quantity') || 'Cantidad' }}
                        </label>
                        <input v-model.number="itemQuantity" type="number" min="1"
                          class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2" />
                      </div>

                      <!-- Special Instructions -->
                      <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 text-left mb-2">
                          {{ t('app.views.orders.modals.new_order.special_instructions') }}
                        </label>
                        <textarea v-model="itemSpecialInstructions" rows="3"
                          class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          :placeholder="t('app.views.orders.modals.new_order.special_requests_placeholder')"></textarea>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="mt-5 sm:mt-6 grid grid-cols-2 gap-3">
                  <button type="button"
                    class="inline-flex w-full justify-center rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2 text-base font-medium text-gray-700 dark:text-gray-300 shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:text-sm"
                    @click="showItemModal = false">
                    {{ t('app.actions.cancel') }}
                  </button>
                  <button type="button"
                    class="inline-flex w-full justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:text-sm"
                    @click="confirmAddItem">
                    {{ t('app.views.orders.modals.new_order.add_to_order') }}
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
import { ref, computed, onMounted } from 'vue';
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue';
import { XMarkIcon, PlusIcon, ChevronDownIcon, InformationCircleIcon } from '@heroicons/vue/24/outline';
import { useI18n } from 'vue-i18n';
import orderService, { type MenuItem as BaseMenuItem, type CreateOrderItemData as BaseCreateOrderItemData } from '@/services/orderService';
import SpecialNotesBuilder from './SpecialNotesBuilder.vue';

const { t } = useI18n();

// Extended interfaces for local use
interface MenuItem extends BaseMenuItem {
  discount_price?: number | null;
}

interface CreateOrderItemData extends BaseCreateOrderItemData {
  name?: string;
  variant?: { id: number; name: string; price: number } | null;
}

interface Props {
  open: boolean;
  orderId: number;
  tableNumber: number;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'success'): void;
}>();

// State
const menuItems = ref<MenuItem[]>([]);
const selectedItems = ref<CreateOrderItemData[]>([]);
const loading = ref({ menu: false });
const error = ref({ menu: '' });
const submitting = ref(false);
const showItemModal = ref(false);
const selectedMenuItem = ref<MenuItem | null>(null);
const selectedVariantId = ref<number | null>(null);
const itemQuantity = ref(1);
const itemSpecialInstructions = ref('');
const expandedCategories = ref<Set<string>>(new Set());

// Computed
const menuItemsByCategory = computed(() => {
  const grouped: Record<string, MenuItem[]> = {};
  menuItems.value.forEach(item => {
    // Extract category name from category object or use string directly
    let categoryName = t('app.views.orders.modals.new_order.uncategorized');
    
    if (item.category) {
      if (typeof item.category === 'object' && item.category !== null && 'name' in item.category) {
        categoryName = (item.category as any).name;
      } else if (typeof item.category === 'string') {
        categoryName = item.category;
      }
    }
    
    if (!grouped[categoryName]) {
      grouped[categoryName] = [];
    }
    grouped[categoryName].push(item);
  });
  return grouped;
});

const categoryNames = computed(() => Object.keys(menuItemsByCategory.value).sort());

const totalAmount = computed(() => {
  return selectedItems.value.reduce((sum, item) => sum + (item.unit_price * item.quantity), 0);
});

// Methods
const toggleCategory = (category: string) => {
  if (expandedCategories.value.has(category)) {
    expandedCategories.value.delete(category);
  } else {
    expandedCategories.value.add(category);
  }
};

const isCategoryExpanded = (category: string) => {
  return expandedCategories.value.has(category);
};

const getEffectivePrice = (price: number, discountPrice: number | null | undefined): number => {
  if (discountPrice && discountPrice > 0) {
    return discountPrice;
  }
  return price;
};

const getItemQuantity = (menuItemId: number): number => {
  return selectedItems.value
    .filter(item => item.menu_item_id === menuItemId)
    .reduce((sum, item) => sum + item.quantity, 0);
};

const selectItem = (item: MenuItem) => {
  selectedMenuItem.value = item;
  selectedVariantId.value = null;
  itemQuantity.value = 1;
  itemSpecialInstructions.value = '';
  showItemModal.value = true;
};

const confirmAddItem = () => {
  if (!selectedMenuItem.value) return;

  const variant = selectedMenuItem.value.variants?.find(v => v.id === selectedVariantId.value);
  // Use variant price if selected, otherwise use item price (with discount if available)
  const effectivePrice = variant 
    ? variant.price
    : getEffectivePrice(selectedMenuItem.value.price, selectedMenuItem.value.discount_price);

  selectedItems.value.push({
    menu_item_id: selectedMenuItem.value.id,
    variant_id: selectedVariantId.value,
    quantity: itemQuantity.value,
    special_instructions: itemSpecialInstructions.value || null,
    unit_price: effectivePrice,
    // Display fields (not sent to backend)
    name: selectedMenuItem.value.name,
    variant: variant ? {
      id: variant.id,
      name: variant.name,
      price: variant.price
    } : null,
  });

  // Reset and close
  showItemModal.value = false;
  selectedMenuItem.value = null;
  selectedVariantId.value = null;
  itemQuantity.value = 1;
  itemSpecialInstructions.value = '';
};

const removeItem = (index: number) => {
  selectedItems.value.splice(index, 1);
};

const handleSubmit = async () => {
  if (selectedItems.value.length === 0) return;

  submitting.value = true;
  try {
    // Extract only the fields needed for the API
    const itemsToSend = selectedItems.value.map(item => ({
      menu_item_id: item.menu_item_id,
      variant_id: item.variant_id,
      quantity: item.quantity,
      special_instructions: item.special_instructions,
      unit_price: item.unit_price,
    }));
    
    await orderService.addMultipleItemsToOrder(props.orderId, itemsToSend);
    emit('success');
    emit('close');
  } catch (err: any) {
    console.error('Error adding items to order:', err);
    error.value.menu = err.message || t('app.views.orders.add_items_modal.error_adding');
  } finally {
    submitting.value = false;
  }
};

const loadMenuItems = async () => {
  loading.value.menu = true;
  error.value.menu = '';
  try {
    menuItems.value = await orderService.getMenuItems();
    // Expand first category by default
    if (categoryNames.value.length > 0) {
      expandedCategories.value.add(categoryNames.value[0]);
    }
  } catch (err: any) {
    console.error('Error loading menu items:', err);
    error.value.menu = err.message || t('app.views.orders.modals.new_order.error_menu');
  } finally {
    loading.value.menu = false;
  }
};

onMounted(() => {
  loadMenuItems();
});
</script>
