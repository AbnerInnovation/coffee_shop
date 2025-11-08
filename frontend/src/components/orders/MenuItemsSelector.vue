<template>
  <div class="space-y-3 sm:space-y-4">
    <div>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        {{ $t('app.views.orders.modals.new_order.menu_items') }}
      </label>
      
      <div v-if="loading" class="text-center py-4">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto"></div>
        <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
          {{ $t('app.views.orders.modals.new_order.loading_menu') }}
        </p>
      </div>
      
      <div v-else-if="error && categoryNames.length === 0" class="text-center py-4 text-red-600">
        <p>{{ $t('app.views.orders.modals.new_order.error_menu') }}</p>
      </div>
      
      <div v-else class="space-y-3 max-h-[50vh] sm:max-h-none overflow-y-auto pr-1 -mr-1 sm:mr-0">
        <!-- Category sections -->
        <div v-for="category in categoryNames" :key="category"
          class="border-b border-gray-200 dark:border-gray-700 pb-3 mb-3 last:border-b-0 last:pb-0 last:mb-0">
          <!-- Category Header -->
          <button @click="$emit('toggle-category', category)"
            class="flex items-center justify-between w-full p-2 text-left hover:bg-gray-50 dark:hover:bg-gray-700 rounded-md transition-colors"
            :class="{ 'bg-indigo-50 dark:bg-indigo-900/20': isCategoryExpanded(category) }">
            <h3 class="text-sm font-medium text-gray-900 dark:text-gray-100">
              {{ category }}
              <span class="text-xs text-gray-500 ml-2">({{ menuItemsByCategory[category].length }})</span>
            </h3>
            <ChevronDownIcon class="h-4 w-4 text-gray-500 transition-transform"
              :class="{ 'rotate-180': !isCategoryExpanded(category) }" />
          </button>

          <!-- Category Items -->
          <div v-if="isCategoryExpanded(category)" class="mt-2 space-y-2 pl-2">
            <div v-for="item in menuItemsByCategory[category]" :key="item.id"
              class="flex items-center justify-between p-2 border rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
              @click="$emit('select-item', item)">
              <div class="flex-1 min-w-0">
                <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                  {{ item.name }}
                  <span v-if="item.has_variants" class="text-xs text-gray-500 ml-1">
                    {{ $t('app.views.orders.modals.new_order.select_options_hint') }}
                  </span>
                </h4>
                <div class="flex items-center gap-2">
                  <p v-if="item.discount_price && item.discount_price > 0"
                    class="text-sm text-gray-500 dark:text-gray-400 line-through">
                    ${{ (item.price || 0).toFixed(2) }}
                  </p>
                  <p class="text-sm font-medium"
                    :class="item.discount_price && item.discount_price > 0 ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'">
                    ${{ getEffectivePrice(item.price || 0, item.discount_price).toFixed(2) }}
                  </p>
                  <span v-if="item.discount_price && item.discount_price > 0"
                    class="inline-flex items-center rounded-full bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 text-xs font-medium text-green-800 dark:text-green-200">
                    {{ $t('app.forms.sale_badge') }}
                  </span>
                </div>
              </div>
              <div class="flex items-center space-x-2">
                <span class="text-sm text-gray-900 dark:text-gray-200">
                  {{ getItemQuantity(item.id) > 0 ? $t('app.views.orders.modals.new_order.in_order', {
                    count: getItemQuantity(item.id)
                  }) : $t('app.views.orders.modals.new_order.add') }}
                </span>
                <button type="button"
                  class="p-1 rounded-full text-indigo-600 hover:bg-indigo-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  @click.stop="$emit('select-item', item)">
                  <PlusIcon class="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ChevronDownIcon, PlusIcon } from '@heroicons/vue/24/outline';

interface MenuItem {
  id: number;
  name: string;
  price: number;
  discount_price?: number;
  has_variants: boolean;
}

interface Props {
  loading: boolean;
  error: boolean | string | null;
  categoryNames: string[];
  menuItemsByCategory: Record<string, MenuItem[]>;
  expandedCategories: Set<string>;
  getItemQuantity: (itemId: number) => number;
}

const props = defineProps<Props>();

defineEmits<{
  (e: 'toggle-category', category: string): void;
  (e: 'select-item', item: MenuItem): void;
}>();

function isCategoryExpanded(category: string): boolean {
  return props.expandedCategories.has(category);
}

function getEffectivePrice(price: number, discountPrice?: number): number {
  if (discountPrice && discountPrice > 0) {
    return discountPrice;
  }
  return price;
}
</script>
