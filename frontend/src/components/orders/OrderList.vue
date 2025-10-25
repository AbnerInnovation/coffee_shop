<template>
  <div class="bg-white dark:bg-gray-900 shadow overflow-hidden rounded-lg sm:rounded-md">
    <!-- Empty State -->
    <div v-if="orders.length === 0" class="text-center py-12 px-4">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-gray-100">
        {{ $t('app.views.orders.no_orders') }}
      </h3>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        {{ $t('app.views.orders.no_orders_description') }}
      </p>
      <div class="mt-6">
        <button 
          type="button" 
          @click="$emit('new-order')" 
          class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <PlusIcon class="-ml-1 mr-2 h-5 w-5" />
          {{ $t('app.views.orders.new_order') }}
        </button>
      </div>
    </div>
    
    <!-- Orders List -->
    <ul v-else role="list" class="divide-y divide-gray-200 dark:divide-gray-700">
      <OrderListItem
        v-for="order in orders"
        :key="order.id"
        :order="order"
        @view="$emit('view', $event)"
        @edit="$emit('edit', $event)"
        @complete="$emit('complete', $event)"
        @cancel="$emit('cancel', $event)"
      />
    </ul>
  </div>
</template>

<script setup lang="ts">
import { PlusIcon } from '@heroicons/vue/24/outline';
import OrderListItem from './OrderListItem.vue';
import type { OrderWithLocalFields } from '@/utils/orderHelpers';

defineProps<{
  orders: OrderWithLocalFields[];
}>();

defineEmits<{
  'new-order': [];
  view: [order: OrderWithLocalFields];
  edit: [order: OrderWithLocalFields];
  complete: [orderId: number];
  cancel: [orderId: number];
}>();
</script>
