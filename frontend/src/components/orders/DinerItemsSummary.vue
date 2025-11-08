<template>
  <div v-if="items.length > 0" class="bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800 rounded-lg p-3">
    <div class="flex items-center justify-between mb-2">
      <h4 class="text-sm font-medium text-indigo-900 dark:text-indigo-100">
        {{ title }}
      </h4>
      <span class="text-xs text-indigo-600 dark:text-indigo-400">
        {{ items.length }} {{ items.length === 1 ? 'item' : 'items' }}
      </span>
    </div>
    <div class="space-y-1.5">
      <div 
        v-for="(item, index) in items" 
        :key="index"
        class="flex items-center justify-between text-sm bg-white dark:bg-gray-800 rounded px-2 py-1.5"
      >
        <div class="flex-1 min-w-0">
          <span class="text-gray-900 dark:text-gray-100 font-medium">
            {{ getMenuItemName(item.menu_item_id) }}
          </span>
          <span v-if="item.notes" class="text-xs text-gray-500 dark:text-gray-400 ml-1">
            ({{ item.notes }})
          </span>
        </div>
        <div class="flex items-center gap-2 ml-2">
          <span class="text-gray-600 dark:text-gray-300 text-xs">
            {{ item.quantity }}x
          </span>
          <span class="text-gray-900 dark:text-gray-100 font-medium text-xs">
            ${{ ((item.unit_price || 0) * item.quantity).toFixed(2) }}
          </span>
        </div>
      </div>
    </div>
    <div class="mt-2 pt-2 border-t border-indigo-200 dark:border-indigo-800 flex justify-between items-center">
      <span class="text-xs font-medium text-indigo-700 dark:text-indigo-300">
        Subtotal:
      </span>
      <span class="text-sm font-bold text-indigo-900 dark:text-indigo-100">
        ${{ calculateSubtotal().toFixed(2) }}
      </span>
    </div>
  </div>
  <div v-else class="bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3 text-center">
    <p class="text-sm text-gray-500 dark:text-gray-400">
      {{ emptyMessage }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Item {
  menu_item_id: number;
  quantity: number;
  notes?: string;
  unit_price?: number;
}

interface Props {
  title: string;
  items: Item[];
  getMenuItemName: (itemId: number) => string;
  emptyMessage?: string;
}

const props = withDefaults(defineProps<Props>(), {
  emptyMessage: 'Sin items agregados aún'
});

const calculateSubtotal = () => {
  return props.items.reduce((total, item) => {
    return total + ((item.unit_price || 0) * item.quantity);
  }, 0);
};
</script>
