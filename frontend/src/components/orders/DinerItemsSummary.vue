<template>
  <div class="bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800 rounded-lg p-3">
    <div class="flex items-center justify-between mb-3">
      <h4 class="text-sm font-medium text-indigo-900 dark:text-indigo-100">
        {{ title }}
      </h4>
      <span class="text-xs text-indigo-600 dark:text-indigo-400">
        {{ totalItemCount }} {{ totalItemCount === 1 ? 'item' : 'items' }}
        <span v-if="groupCount !== totalItemCount" class="opacity-75">
          ({{ groupCount }} {{ groupCount === 1 ? 'grupo' : 'grupos' }})
        </span>
      </span>
    </div>

    <!-- Empty State -->
    <div v-if="groupedItems.length === 0" 
      class="bg-white dark:bg-gray-800 rounded-lg p-3 text-center">
      <p class="text-sm text-gray-500 dark:text-gray-400">
        {{ emptyMessage }}
      </p>
    </div>

    <!-- Grouped Items -->
    <div v-else class="space-y-2">
      <div 
        v-for="group in groupedItems" 
        :key="group.fingerprint"
        class="bg-white dark:bg-gray-800 rounded-lg px-3 py-2"
      >
        <div class="flex items-start justify-between gap-2">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-1.5">
              <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
                {{ group.name }}
              </span>
              <span v-if="group.variant_name" 
                class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                {{ group.variant_name }}
              </span>
            </div>
            <p v-if="group.category" class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
              {{ group.category }}
            </p>
            <!-- Special Instructions -->
            <div v-if="group.hasCustomizations" class="mt-1 space-y-0.5">
              <p 
                v-for="(line, index) in getFormattedInstructions(group)" 
                :key="index"
                class="text-xs text-amber-600 dark:text-amber-400 flex items-start gap-1"
              >
                <span class="opacity-50">•</span>
                <span>{{ line }}</span>
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <div class="flex flex-col items-end gap-0.5">
              <span class="text-xs text-gray-600 dark:text-gray-400">
                {{ group.quantity }}x
              </span>
              <span class="text-sm font-semibold text-gray-900 dark:text-gray-100">
                ${{ (group.price * group.quantity).toFixed(2) }}
              </span>
            </div>
            <!-- Delete Button -->
            <button
              type="button"
              @click="$emit('remove-group', group)"
              class="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 p-1 rounded hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
              :title="'Eliminar ' + group.quantity + 'x ' + group.name"
            >
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Subtotal -->
    <div v-if="groupedItems.length > 0" 
      class="mt-3 pt-2 border-t border-indigo-200 dark:border-indigo-800 flex justify-between items-center">
      <span class="text-xs font-medium text-indigo-700 dark:text-indigo-300">
        Subtotal:
      </span>
      <span class="text-sm font-bold text-indigo-900 dark:text-indigo-100">
        ${{ totalPrice.toFixed(2) }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useItemGrouping } from '@/composables/useItemGrouping';
import type { OrderItem } from '@/services/orderService';

interface Props {
  title: string;
  items: OrderItem[];
  getMenuItemName: (itemId: number) => string;
  getMenuItemCategory: (itemId: number) => string;
  emptyMessage?: string;
}

const props = withDefaults(defineProps<Props>(), {
  emptyMessage: 'Sin items agregados aún'
});

// Define emits
defineEmits<{
  (e: 'remove-group', group: any): void;
}>();

// Enrich items with menu information before grouping
const enrichedItems = computed(() => {
  return props.items.map((item, index) => ({
    id: item.id || index,
    menu_item_id: item.menu_item_id,
    variant_id: item.variant_id || null,
    quantity: item.quantity || 1,
    special_instructions: item.special_instructions || null,
    status: item.status || 'pending',
    order_id: item.order_id || 0,
    person_id: item.person_id || null,
    created_at: item.created_at || new Date().toISOString(),
    updated_at: item.updated_at || new Date().toISOString(),
    unit_price: item.unit_price || 0,
    variant: item.variant || null,
    menu_item: item.menu_item || {
      id: item.menu_item_id,
      name: props.getMenuItemName(item.menu_item_id),
      description: '',
      price: item.unit_price || 0,
      category: props.getMenuItemCategory(item.menu_item_id),
      category_visible_in_kitchen: true,
      image_url: '',
      is_available: true
    },
    extras: item.extras || []
  }));
});

// Use grouping composable with enriched items
const { 
  groupedItems, 
  totalItemCount, 
  groupCount, 
  totalPrice,
  getFormattedInstructions 
} = useItemGrouping(enrichedItems);
</script>
