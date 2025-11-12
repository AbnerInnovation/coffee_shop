<template>
  <div class="mt-4">
    <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">Resumen de Orden</h4>

    <!-- Multiple Diners View -->
    <div v-if="useMultipleDiners">
      <div v-for="(personData, pIndex) in personsWithGrouping" :key="pIndex" class="mb-4">
        <div class="flex items-center justify-between mb-2 bg-indigo-50 dark:bg-indigo-900/20 px-3 py-2 rounded-md">
          <h5 class="text-sm font-semibold text-indigo-900 dark:text-indigo-100">
            {{ personData.name || `Persona ${personData.position}` }}
          </h5>
          <span class="text-xs text-indigo-600 dark:text-indigo-400">
            {{ personData.totalItemCount }} {{ personData.totalItemCount === 1 ? 'item' : 'items' }}
            <span v-if="personData.groupCount !== personData.totalItemCount" class="text-indigo-500">
              ({{ personData.groupCount }} {{ personData.groupCount === 1 ? 'grupo' : 'grupos' }})
            </span>
          </span>
        </div>
        <div v-if="personData.groupedItems.length > 0" class="space-y-2 ml-2">
          <div v-for="(group, gIndex) in personData.groupedItems" :key="gIndex"
            class="flex justify-between items-start text-sm py-2 border-b border-gray-100 dark:border-gray-800 last:border-0">
            <div class="flex-1">
              <p class="font-medium text-gray-900 dark:text-gray-100">
                {{ group.name }}
                <span v-if="group.variant_name" class="text-xs text-gray-500 ml-1">({{ group.variant_name }})</span>
              </p>
              <div v-if="group.category" class="mt-1">
                <span
                  class="inline-flex items-center rounded-full bg-gray-100 dark:bg-gray-700 px-2 py-0.5 text-xs font-medium text-gray-600 dark:text-gray-300">
                  {{ group.category }}
                </span>
              </div>
              <!-- Special Instructions -->
              <div v-if="group.special_instructions" class="mt-1 space-y-0.5">
                <p v-for="(instruction, idx) in personData.getFormattedInstructions(group)" :key="idx" 
                  class="text-xs text-gray-500 dark:text-gray-400">
                  {{ instruction }}
                </p>
              </div>
            </div>

            <div class="flex items-center space-x-3">
              <span class="text-gray-700 dark:text-gray-200 text-xs font-medium">{{ group.quantity }}x</span>
              <span class="font-medium text-gray-900 dark:text-gray-100 min-w-[60px] text-right">
                ${{ (group.price * group.quantity).toFixed(2) }}
              </span>
            </div>
          </div>
        </div>
        <div v-else class="ml-2 py-3 text-sm text-gray-500 dark:text-gray-400 italic">
          Sin items agregados
        </div>
      </div>
    </div>

    <!-- Simple order view -->
    <div v-else class="space-y-3">
      <div v-for="item in selectedItems" :key="item.id" class="flex justify-between items-start">
        <div class="flex-1">
          <div class="flex items-center gap-2">
            <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
              {{ item.name }}
              <span v-if="item.variant_name" class="text-xs text-gray-500 ml-1">({{ item.variant_name }})</span>
            </p>
            <span v-if="isItemLocked(item)"
              class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium" :class="{
                'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200': item.status === 'preparing',
                'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200': item.status === 'ready'
              }">
              {{ $t(`app.status.${item.status}`) }}
            </span>
          </div>
          <div v-if="item.category" class="mt-1">
            <span
              class="inline-flex items-center rounded-full bg-gray-100 dark:bg-gray-700 px-2 py-0.5 text-xs font-medium text-gray-600 dark:text-gray-300">
              {{ item.category }}
            </span>
          </div>
          <p v-if="item.notes" class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ item.notes }}</p>
          <div v-if="item.extras && item.extras.length > 0" class="mt-1 space-y-0.5">
            <p v-for="(extra, idx) in item.extras" :key="idx" class="text-xs text-indigo-600 dark:text-indigo-400">
              + {{ extra.name }} ({{ extra.quantity }}x ${{ extra.price.toFixed(2) }})
            </p>
          </div>
          <p v-if="isItemLocked(item)" class="text-xs text-orange-600 dark:text-orange-400 mt-1">
            {{ $t('app.views.orders.modals.new_order.item_locked') }}
          </p>
        </div>
        <div class="flex items-center space-x-4 ml-4">
          <div class="flex items-center space-x-2">
            <button type="button"
              class="p-1 text-gray-500 hover:text-indigo-600 focus:outline-none disabled:opacity-30 disabled:cursor-not-allowed"
              :disabled="isItemLocked(item)" @click.stop="$emit('decrease-quantity', item)">
              <MinusIcon class="h-4 w-4" />
            </button>
            <span class="text-sm text-gray-700 dark:text-gray-200 w-6 text-center">{{ item.quantity }}</span>
            <button type="button"
              class="p-1 text-gray-500 hover:text-indigo-600 focus:outline-none disabled:opacity-30 disabled:cursor-not-allowed"
              :disabled="isItemLocked(item)" @click.stop="$emit('increase-quantity', item)">
              <PlusIcon class="h-4 w-4" />
            </button>
          </div>
          <span class="text-sm font-medium text-gray-900 dark:text-gray-100 w-16 text-right">
            ${{ calculateItemTotal(item) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Total Section -->
    <div class="mt-4 pt-4 border-t border-gray-200">
      <div class="flex justify-between items-center">
        <span class="text-sm font-medium text-gray-900 dark:text-gray-100">
          {{ $t('app.views.orders.modals.new_order.total') }}
        </span>
        <span class="text-lg font-bold text-gray-900 dark:text-white">
          <template v-if="useMultipleDiners">
            ${{persons.reduce((sum, person) => sum + person.items.reduce((itemSum, item) => itemSum +
              ((item.unit_price || 0) * item.quantity), 0), 0).toFixed(2)}}
          </template>
          <template v-else>
            ${{(selectedItems.reduce((sum, item) => sum + (parseFloat(calculateItemTotal(item)) || 0),
              0)).toFixed(2)}}
          </template>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useItemGrouping } from '@/composables/useItemGrouping';
import type { OrderItem } from '@/services/orderService';
import { MinusIcon, PlusIcon } from '@heroicons/vue/24/outline';

// Local interface for display items (different from OrderItem)
interface DisplayOrderItem {
  id?: number;
  menu_item_id: number;
  variant_id?: number | null;
  name: string;
  variant_name?: string;
  category?: string;
  quantity: number;
  unit_price?: number;
  price?: number;
  notes?: string;
  special_instructions?: string;
  status?: string;
  extras?: Array<{ name: string; quantity: number; price: number }>;
}

interface Person {
  name: string;
  position: number;
  items: Array<{
    menu_item_id: number;
    variant_id?: number | null;
    quantity: number;
    notes?: string;
    special_instructions?: string;
    unit_price?: number;
  }>;
}

interface Props {
  useMultipleDiners: boolean;
  persons: Person[];
  selectedItems: DisplayOrderItem[];
  getMenuItemName: (itemId: number) => string;
  getMenuItemCategory?: (itemId: number) => string;
  calculateItemTotal: (item: DisplayOrderItem) => string;
  isItemLocked: (item: DisplayOrderItem) => boolean;
}

const props = defineProps<Props>();

defineEmits<{
  (e: 'remove-item', personIndex: number, itemIndex: number): void;
  (e: 'decrease-quantity', item: DisplayOrderItem): void;
  (e: 'increase-quantity', item: DisplayOrderItem): void;
}>();

// Helper function to convert person items to OrderItem format for grouping
function convertPersonItemsToOrderItems(personItems: Person['items'], menuItems: any): OrderItem[] {
  return personItems.map((item, index) => ({
    id: index,
    menu_item_id: item.menu_item_id,
    variant_id: item.variant_id || null,
    quantity: item.quantity || 1,
    special_instructions: item.special_instructions || item.notes || null,
    status: 'pending',
    order_id: 0,
    person_id: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    unit_price: item.unit_price || 0,
    variant: null,
    menu_item: {
      id: item.menu_item_id,
      name: props.getMenuItemName(item.menu_item_id),
      description: '',
      price: item.unit_price || 0,
      category: props.getMenuItemCategory ? props.getMenuItemCategory(item.menu_item_id) : '',
      category_visible_in_kitchen: true,
      image_url: '',
      is_available: true
    },
    extras: []
  }));
}

// Create grouped items for each person
const personsWithGrouping = computed(() => {
  return props.persons.map(person => {
    const orderItems = computed(() => convertPersonItemsToOrderItems(person.items, null));
    const grouping = useItemGrouping(orderItems);
    return {
      ...person,
      groupedItems: grouping.groupedItems.value,
      totalItemCount: grouping.totalItemCount.value,
      groupCount: grouping.groupCount.value,
      getFormattedInstructions: grouping.getFormattedInstructions
    };
  });
});
</script>
