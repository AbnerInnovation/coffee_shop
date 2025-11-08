<template>
  <TransitionRoot appear :show="isOpen" as="template">
    <Dialog as="div" @close="$emit('close')" class="relative z-[99999]" :initial-focus="addButtonRef">
      <TransitionChild
        as="template"
        enter="duration-300 ease-out"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="duration-200 ease-in"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black bg-opacity-25 z-[99999]" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto z-[99999]">
        <div class="flex min-h-full items-center justify-center p-4 text-center">
          <TransitionChild
            as="template"
            enter="duration-300 ease-out"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="duration-200 ease-in"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white dark:bg-gray-900 p-6 text-left align-middle shadow-xl transition-all">
              <!-- Header -->
              <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900 dark:text-gray-100 mb-4">
                {{ item?.name }}
              </DialogTitle>

              <!-- Description -->
              <p v-if="item?.description" class="text-sm text-gray-500 dark:text-gray-400 mb-4">
                {{ item.description }}
              </p>

              <!-- Variants / Options -->
              <div v-if="item?.variants?.length" class="space-y-2 mb-4">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {{ $t('app.views.orders.modals.new_order.options') }}
                </label>
                
                <!-- Base item option - only show if base price > 0 -->
                <div 
                  v-if="item.price && item.price > 0"
                  class="flex items-center p-3 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition-colors"
                  :class="{ 'bg-indigo-50 dark:bg-indigo-900/20 border-indigo-500': !selectedVariant }"
                  @click="selectedVariant = null"
                >
                  <div class="flex-1">
                    <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {{ $t('app.views.orders.modals.new_order.base_item') || 'Artículo base' }}
                    </p>
                    <div class="flex items-center gap-2 mt-1">
                      <!-- Show original price if there's a discount -->
                      <p v-if="item.discount_price && item.discount_price > 0" class="text-sm text-gray-500 dark:text-gray-400 line-through">
                        ${{ (item.price || 0).toFixed(2) }}
                      </p>
                      <!-- Show effective price (with discount if applicable) -->
                      <p class="text-sm font-medium" :class="item.discount_price && item.discount_price > 0 ? 'text-green-600 dark:text-green-400' : 'text-gray-700 dark:text-gray-300'">
                        ${{ getEffectivePrice(item.price || 0, item.discount_price).toFixed(2) }}
                      </p>
                      <!-- Show discount badge -->
                      <span v-if="item.discount_price && item.discount_price > 0" class="inline-flex items-center rounded-full bg-green-100 dark:bg-green-900/30 px-2 py-0.5 text-xs font-medium text-green-800 dark:text-green-200">
                        {{ $t('app.forms.sale_badge') || 'Oferta' }}
                      </span>
                    </div>
                  </div>
                  <div class="ml-3">
                    <div class="w-5 h-5 rounded-full border-2 flex items-center justify-center"
                      :class="!selectedVariant ? 'border-indigo-600 bg-indigo-600' : 'border-gray-300 dark:border-gray-600'">
                      <div v-if="!selectedVariant" class="w-2 h-2 rounded-full bg-white"></div>
                    </div>
                  </div>
                </div>

                <!-- Variant options -->
                <div 
                  v-for="variant in item.variants" 
                  :key="variant.id"
                  class="flex items-center p-3 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition-colors"
                  :class="{ 'bg-indigo-50 dark:bg-indigo-900/20 border-indigo-500': selectedVariant?.id === variant.id }"
                  @click="selectedVariant = variant"
                >
                  <div class="flex-1">
                    <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ variant.name }}</p>
                    <div class="flex items-center gap-2 mt-1">
                      <!-- Show original price if there's a discount -->
                      <p v-if="hasVariantDiscount(variant)" class="text-sm text-gray-500 dark:text-gray-400 line-through">
                        ${{ getVariantOriginalPrice(item, variant).toFixed(2) }}
                      </p>
                      <!-- Show effective price (with discount if applicable) -->
                      <p class="text-sm font-medium" :class="hasVariantDiscount(variant) ? 'text-green-600 dark:text-green-400' : 'text-gray-700 dark:text-gray-300'">
                        ${{ getVariantPrice(item, variant).toFixed(2) }}
                      </p>
                      <!-- Show discount badge -->
                      <span v-if="hasVariantDiscount(variant)" class="inline-flex items-center rounded-full bg-green-100 dark:bg-green-900/30 px-2 py-0.5 text-xs font-medium text-green-800 dark:text-green-200">
                        {{ $t('app.forms.sale_badge') || 'Oferta' }}
                      </span>
                    </div>
                  </div>
                  <div class="ml-3">
                    <div class="w-5 h-5 rounded-full border-2 flex items-center justify-center"
                      :class="selectedVariant?.id === variant.id ? 'border-indigo-600 bg-indigo-600' : 'border-gray-300 dark:border-gray-600'">
                      <div v-if="selectedVariant?.id === variant.id" class="w-2 h-2 rounded-full bg-white"></div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Special Notes Builder -->
              <div v-if="item" class="mb-4">
                <SpecialNotesBuilder
                  :ingredients="(item as any).ingredients || null"
                  v-model="specialNote"
                  :top-notes="topNotes"
                />
              </div>

              <!-- Additional Notes (fallback) -->
              <div v-if="!item || !(item as any).ingredients" class="mb-4">
                <label for="item-notes" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {{ $t('app.views.orders.modals.new_order.special_instructions') }}
                </label>
                <textarea 
                  id="item-notes" 
                  v-model="notes" 
                  rows="3"
                  class="w-full rounded-lg border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  :placeholder="$t('app.views.orders.modals.new_order.special_requests_placeholder')"
                />
              </div>

              <!-- Quantity Selector -->
              <div class="mb-6">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Cantidad
                </label>
                <div class="flex items-center gap-3">
                  <button
                    type="button"
                    @click="decrementQuantity"
                    class="w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 flex items-center justify-center transition-colors"
                    :disabled="quantity <= 1"
                  >
                    <span class="text-xl font-semibold text-gray-700 dark:text-gray-200">−</span>
                  </button>
                  <span class="text-2xl font-semibold text-gray-900 dark:text-gray-100 min-w-[3rem] text-center">
                    {{ quantity }}
                  </span>
                  <button
                    type="button"
                    @click="incrementQuantity"
                    class="w-10 h-10 rounded-full bg-indigo-600 hover:bg-indigo-700 flex items-center justify-center transition-colors"
                  >
                    <span class="text-xl font-semibold text-white">+</span>
                  </button>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex gap-3">
                <button
                  type="button"
                  class="flex-1 inline-flex justify-center rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors"
                  @click="$emit('close')"
                >
                  {{ $t('app.views.orders.modals.new_order.cancel') }}
                </button>
                <button
                  ref="addButtonRef"
                  type="button"
                  class="flex-1 inline-flex justify-center rounded-lg border border-transparent bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors"
                  @click="addToOrder"
                >
                  Agregar • ${{ totalPrice.toFixed(2) }}
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
import { ref, computed, watch } from 'vue';
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue';
import SpecialNotesBuilder from './SpecialNotesBuilder.vue';

interface MenuItem {
  id: number;
  name: string;
  description?: string;
  price: number;
  discount_price?: number;
  variants?: MenuItemVariant[];
  ingredients?: any[];
}

interface MenuItemVariant {
  id: number;
  name: string;
  price: number;
  price_adjustment: number;
  discount_price?: number;
}

interface Props {
  isOpen: boolean;
  item: MenuItem | null;
  topNotes?: string[];
}

interface Emits {
  (e: 'close'): void;
  (e: 'add', data: {
    item: MenuItem;
    variant: MenuItemVariant | null;
    quantity: number;
    notes: string;
  }): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const selectedVariant = ref<MenuItemVariant | null>(null);
const specialNote = ref('');
const notes = ref('');
const quantity = ref(1);

// Focus management
const addButtonRef = ref<HTMLElement | null>(null);

// Reset when item changes
watch(() => props.item, (newItem) => {
  if (newItem) {
    selectedVariant.value = null;
    // Don't reset specialNote here - let SpecialNotesBuilder handle it
    // specialNote.value = '';
    notes.value = '';
    quantity.value = 1;
  }
});

// Computed total price
const totalPrice = computed(() => {
  if (!props.item) return 0;
  
  let price = 0;
  if (selectedVariant.value) {
    const basePrice = props.item.price || 0;
    const adjustment = selectedVariant.value.price_adjustment || 0;
    const variantPrice = basePrice + adjustment;
    price = getEffectivePrice(variantPrice, selectedVariant.value.discount_price);
  } else {
    price = getEffectivePrice(props.item.price || 0, props.item.discount_price);
  }
  
  return price * quantity.value;
});

function getEffectivePrice(price: number, discount_price?: number): number {
  if (discount_price && discount_price > 0) {
    return discount_price;
  }
  return price;
}

function getVariantPrice(item: MenuItem, variant: MenuItemVariant): number {
  // If variant has an absolute price, use it
  if (variant.price && variant.price > 0) {
    return getEffectivePrice(variant.price, variant.discount_price);
  }
  // Otherwise, use base price + adjustment
  const basePrice = item.price || 0;
  const adjustment = variant.price_adjustment || 0;
  const variantPrice = basePrice + adjustment;
  return getEffectivePrice(variantPrice, variant.discount_price);
}

function getVariantOriginalPrice(item: MenuItem, variant: MenuItemVariant): number {
  // If variant has an absolute price, use it
  if (variant.price && variant.price > 0) {
    return variant.price;
  }
  // Otherwise, use base price + adjustment
  const basePrice = item.price || 0;
  const adjustment = variant.price_adjustment || 0;
  return basePrice + adjustment;
}

function hasVariantDiscount(variant: MenuItemVariant): boolean {
  return !!(variant.discount_price && variant.discount_price > 0);
}

function incrementQuantity() {
  quantity.value++;
}

function decrementQuantity() {
  if (quantity.value > 1) {
    quantity.value--;
  }
}

function addToOrder() {
  if (!props.item) return;
  
  const finalNotes = specialNote.value || notes.value;
  
  emit('add', {
    item: props.item,
    variant: selectedVariant.value,
    quantity: quantity.value,
    notes: finalNotes
  });
  
  // Reset after adding
  selectedVariant.value = null;
  specialNote.value = '';
  notes.value = '';
  quantity.value = 1;
  
  emit('close');
}
</script>
