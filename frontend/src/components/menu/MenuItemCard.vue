<script setup lang="ts">
import { PhotoIcon, PencilIcon, TrashIcon } from '@heroicons/vue/24/outline';

export interface MenuItem {
  id: string | number;
  name: string;
  category: string;
  description?: string;
  price: number;
  discount_price?: number;
  isAvailable: boolean;
  imageUrl?: string;
  variants?: Array<{
    id: string | number;
    name: string;
    price: number;
    discount_price?: number;
    isAvailable: boolean;
  }>;
}

interface Props {
  item: MenuItem;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  (e: 'edit', item: MenuItem): void;
  (e: 'delete', item: MenuItem): void;
}>();
</script>

<template>
  <div class="relative rounded-lg border border-gray-200 bg-white shadow-sm">
    <!-- Status Badge -->
    <div class="absolute right-2 top-2">
      <span
        class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
        :class="item.isAvailable ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
      >
        {{ item.isAvailable ? 'Available' : 'Unavailable' }}
      </span>
    </div>

    <!-- Item Image -->
    <div class="aspect-w-3 aspect-h-2 overflow-hidden rounded-t-lg bg-gray-100">
      <img
        v-if="item.imageUrl"
        :src="item.imageUrl"
        :alt="item.name"
        class="h-full w-full object-cover object-center"
      />
      <div v-else class="flex h-full items-center justify-center bg-gray-200">
        <PhotoIcon class="h-12 w-12 text-gray-400" />
      </div>
    </div>

    <!-- Item Details -->
    <div class="p-4">
      <div class="flex items-start justify-between">
        <div class="flex-1">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white">{{ item.name }}</h3>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">{{ item.category }}</p>
        </div>
        <div class="text-right ml-4">
          <div v-if="item.discount_price && item.discount_price > 0" class="flex flex-col items-end">
            <p class="text-sm text-gray-500 dark:text-gray-400 line-through">${{ item.price.toFixed(2) }}</p>
            <p class="text-lg font-bold text-green-600 dark:text-green-400">${{ item.discount_price.toFixed(2) }}</p>
            <span class="inline-flex items-center rounded-full bg-green-100 dark:bg-green-900/30 px-2 py-0.5 text-xs font-medium text-green-800 dark:text-green-200">
              {{ $t('app.forms.save_badge', { amount: `$${(item.price - item.discount_price).toFixed(2)}` }) }}
            </span>
          </div>
          <p v-else class="text-lg font-medium text-gray-900 dark:text-white">${{ item.price.toFixed(2) }}</p>
        </div>
      </div>

      <p v-if="item.description" class="mt-2 text-sm text-gray-600 line-clamp-2">
        {{ item.description }}
      </p>

      <!-- Actions -->
      <div class="mt-4 flex justify-end space-x-2">
        <button
          type="button"
          @click="$emit('edit', item)"
          class="inline-flex items-center rounded-md bg-white px-2.5 py-1.5 text-sm font-medium text-indigo-600 shadow-sm hover:bg-indigo-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
        >
          <PencilIcon class="-ml-0.5 mr-1 h-4 w-4" />
          Edit
        </button>
        <button
          type="button"
          @click="$emit('delete', item)"
          class="inline-flex items-center rounded-md bg-white px-2.5 py-1.5 text-sm font-medium text-red-600 shadow-sm hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
        >
          <TrashIcon class="-ml-0.5 mr-1 h-4 w-4" />
          Delete
        </button>
      </div>
    </div>
  </div>
</template>
