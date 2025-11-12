<template>
  <div
    class="bg-white dark:bg-gray-900 dark:border-gray-700 border-gray-200 border-2 rounded-lg shadow-md overflow-hidden">
    <!-- Order Header -->
    <div class="p-2 sm:p-3 border-b border-gray-200 dark:border-gray-700">
      <div class="flex justify-between items-start gap-2">
        <div class="flex-1 min-w-0">
          <h3 class="text-lg sm:text-xl font-bold text-gray-900 dark:text-white truncate">
            {{ t('app.views.kitchen.order', { id: order.order_number || order.id }) }}
          </h3>
          <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">
            {{ formatTime(order.created_at) }}
            <span v-if="order.table_number" class="ml-1 sm:ml-2">
              • {{ t('app.views.kitchen.table', { number: order.table_number }) }}
            </span>
          </p>
        </div>
        <span class="flex-shrink-0 px-2 py-0.5 text-xs font-semibold rounded-full"
          :class="getStatusBadgeClass(order.status)">
          {{ t(`app.status.${order.status}`) }}
        </span>
      </div>
      <div v-if="order.notes"
        class="mt-1.5 p-2 bg-yellow-50 dark:bg-yellow-900/20 text-sm sm:text-base text-yellow-700 dark:text-yellow-300 rounded font-medium">
        {{ order.notes }}
      </div>
    </div>

    <!-- Items grouped by person -->
    <template v-if="order.persons && order.persons.length > 0">
      <div v-for="person in order.persons" :key="person.id"
        class="pl-2 py-2 border-t border-gray-200 dark:border-gray-700 border-l-4 border-l-indigo-500">
        <h5 class="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-1.5 flex items-center gap-1">
          <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          {{ person.name || t('app.views.orders.modals.new_order.persons.person_label', { position: person.position })
          }}
        </h5>

        <div class="space-y-1.5">
          <KitchenItemCard v-for="item in person.items" :key="item.id" :item="item"
            @start-preparing="$emit('start-preparing', order, item)" @mark-ready="$emit('mark-ready', order, item)" />
        </div>
      </div>
    </template>

    <!-- Legacy view: items without grouping -->
    <template v-else>
      <KitchenItemCard v-for="item in visibleItems" :key="item.id" :item="item"
        class="border-t border-gray-200 dark:border-gray-700" @start-preparing="$emit('start-preparing', order, item)"
        @mark-ready="$emit('mark-ready', order, item)" />
    </template>

    <!-- Bulk Actions -->
    <div class="p-2 sm:p-3 bg-gray-50 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 space-y-1.5">
      <button v-if="hasPendingItems(order)" @click="$emit('start-preparing-all', order)"
        class="w-full bg-indigo-600 text-white py-2 sm:py-2.5 px-3 rounded-md hover:bg-indigo-700 active:bg-indigo-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 font-bold text-sm sm:text-base touch-manipulation">
        {{ t('app.views.kitchen.actions.start_preparing_all') }}
      </button>
      <button v-if="hasPreparingItems(order)" @click="$emit('mark-all-ready', order)"
        class="w-full bg-green-600 text-white py-2 sm:py-2.5 px-3 rounded-md hover:bg-green-700 active:bg-green-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 font-bold text-sm sm:text-base touch-manipulation">
        {{ t('app.views.kitchen.actions.all_items_ready') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import type { Order, OrderItem } from '@/services/orderService';
import { formatTime } from '@/utils/dateHelpers';
import { getStatusBadgeClass, getKitchenVisibleItems, hasPendingItems, hasPreparingItems } from '@/utils/kitchenHelpers';
import KitchenItemCard from './KitchenItemCard.vue';

interface Props {
  order: Order;
}

const props = defineProps<Props>();

defineEmits<{
  'start-preparing': [order: Order, item: OrderItem];
  'mark-ready': [order: Order, item: OrderItem];
  'start-preparing-all': [order: Order];
  'mark-all-ready': [order: Order];
}>();

const { t } = useI18n();

const visibleItems = computed(() => getKitchenVisibleItems(props.order));
</script>
