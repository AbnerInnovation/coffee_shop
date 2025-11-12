<template>
  <div class="p-2 sm:p-3 rounded-md flex flex-col gap-1.5" :class="itemBackgroundClass">
    <!-- Item Info -->
    <div class="flex items-center flex-wrap gap-1.5">
      <span class="font-bold text-xl sm:text-2xl text-gray-900 dark:text-white">{{ item.quantity }}x</span>
      <span class="text-base sm:text-lg font-semibold text-gray-900 dark:text-white">{{ item.menu_item.name }}</span>
      <span v-if="item.variant" class="text-sm sm:text-base text-gray-600 dark:text-gray-400">({{ item.variant.name
        }})</span>

      <span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold"
        :class="getItemStatusBadgeClass(item.status)">
        {{ t(`app.status.${item.status}`) }}
      </span>

      <span class="text-xs sm:text-sm text-gray-500 dark:text-gray-400 font-semibold ml-auto">
        {{ getTimeElapsed(item.created_at, t) }}
      </span>
    </div>

    <!-- Category and Action Button -->
    <div class="flex items-center justify-between gap-2">
      <span v-if="item.menu_item.category"
        class="inline-flex items-center rounded-full bg-gray-100 dark:bg-gray-700 px-2 py-0.5 text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase">
        {{ item.menu_item.category }}
      </span>

      <!-- Action Buttons -->
      <button v-if="item.status === 'pending'" @click="$emit('start-preparing', item)"
        class="text-xs sm:text-sm font-semibold px-3 py-1.5 rounded-md bg-indigo-600 text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 flex-shrink-0">
        {{ t('app.views.kitchen.actions.start_preparing') }}
      </button>
      <button v-if="item.status === 'preparing'" @click="$emit('mark-ready', item)"
        class="text-xs sm:text-sm font-semibold px-3 py-1.5 rounded-md bg-green-600 text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 flex-shrink-0">
        {{ t('app.views.kitchen.actions.item_ready') }}
      </button>
    </div>

    <!-- Special Instructions -->
    <div v-if="item.special_instructions"
      class="p-2 bg-blue-50 dark:bg-blue-900/20 rounded text-sm sm:text-base font-semibold text-blue-700 dark:text-blue-300">
      {{ item.special_instructions }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import type { OrderItem } from '@/services/orderService';
import { getItemStatusBadgeClass, getTimeElapsed } from '@/utils/kitchenHelpers';

interface Props {
  item: OrderItem;
}

const props = defineProps<Props>();

defineEmits<{
  'start-preparing': [item: OrderItem];
  'mark-ready': [item: OrderItem];
}>();

const { t } = useI18n();

const itemBackgroundClass = computed(() => {
  return {
    'bg-yellow-50 dark:bg-yellow-900/20': props.item.status === 'pending',
    'bg-blue-50 dark:bg-blue-900/20': props.item.status === 'preparing',
    'bg-green-50 dark:bg-green-900/20': props.item.status === 'ready'
  };
});
</script>
