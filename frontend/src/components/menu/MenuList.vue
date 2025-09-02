<script setup lang="ts">
import { XCircleIcon } from '@heroicons/vue/20/solid';
import type { MenuItem, MenuItemVariant } from '@/types/menu';

interface Props {
  menuItems: MenuItem[];
  loading: boolean;
  error: string | null;
}

interface Emits {
  (e: 'add-item'): void;
  (e: 'edit-item', item: MenuItem): void;
  (e: 'delete-item', item: MenuItem): void;
  (e: 'toggle-availability', item: MenuItem): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

// Helper function to get the correct image URL (handles both camelCase and snake_case)
function getImageUrl(item: MenuItem): string | undefined {
  return item.imageUrl || item.image_url;
}

// Helper function to check availability (handles both camelCase and snake_case)
function isItemAvailable(item: MenuItem): boolean {
  return item.isAvailable ?? item.is_available ?? true;
}
</script>

<template>
  <div class="px-4 sm:px-6 lg:px-8">
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-base font-semibold leading-6 text-gray-900">Menu Items</h1>
        <p class="mt-2 text-sm text-gray-700">
          A list of all menu items in the system.
        </p>
      </div>
      <div class="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
        <button
          type="button"
          @click="$emit('add-item')"
          class="block rounded-md bg-indigo-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
        >
          Add menu item
        </button>
      </div>
    </div>
    <div class="mt-8 flow-root">
      <div class="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
        <div class="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
          <div v-if="loading" class="text-center py-4">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
          </div>
          <div v-else-if="error" class="rounded-md bg-red-50 p-4 mb-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <XCircleIcon class="h-5 w-5 text-red-400" aria-hidden="true" />
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800">Error loading menu items</h3>
                <div class="mt-2 text-sm text-red-700">
                  <p>{{ error }}</p>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
            <table class="min-w-full divide-y divide-gray-300">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Name</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Category</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Price</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Status</th>
                  <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
                    <span class="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 bg-white">
                <tr v-for="item in menuItems" :key="item.id">
                  <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                    <div class="flex items-center">
                      <div v-if="getImageUrl(item)" class="h-10 w-10 flex-shrink-0">
                        <img class="h-10 w-10 rounded-full object-cover" :src="getImageUrl(item)" :alt="item.name" />
                      </div>
                      <div :class="{ 'ml-4': getImageUrl(item) }">
                        {{ item.name }}
                        <div v-if="item.variants && item.variants.length > 0" class="text-xs text-gray-500">
                          {{ item.variants.length }} variants
                        </div>
                      </div>
                    </div>
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                    <span 
                      v-if="item.category"
                      class="inline-flex items-center rounded-md bg-blue-50 px-2 py-1 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10"
                    >
                      {{ typeof item.category === 'string' ? item.category : item.category.name }}
                    </span>
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                    <template v-if="item.variants && item.variants.length > 0">
                      <div v-for="variant in item.variants" :key="variant.id" class="flex justify-between">
                        <span class="text-gray-700">{{ variant.name }}:</span>
                        <span class="font-medium">${{ variant.price.toFixed(2) }}</span>
                      </div>
                    </template>
                    <template v-else>
                      ${{ item.price?.toFixed(2) || '0.00' }}
                    </template>
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm">
                    <span 
                      :class="{
                        'bg-green-100 text-green-800': isItemAvailable(item),
                        'bg-red-100 text-red-800': !isItemAvailable(item)
                      }"
                      class="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ring-green-600/20"
                    >
                      {{ isItemAvailable(item) ? 'Available' : 'Unavailable' }}
                    </span>
                  </td>
                  <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                    <div class="flex justify-end space-x-2">
                      <button 
                        type="button" 
                        @click="$emit('edit-item', item)"
                        class="text-indigo-600 hover:text-indigo-900"
                      >
                        Edit<span class="sr-only">, {{ item.name }}</span>
                      </button>
                      <button 
                        type="button" 
                        @click="$emit('toggle-availability', item)"
                        class="text-gray-600 hover:text-gray-900"
                      >
                        {{ item.is_available ? 'Disable' : 'Enable' }}<span class="sr-only">, {{ item.name }}</span>
                      </button>
                      <button 
                        type="button" 
                        @click="$emit('delete-item', item)"
                        class="text-red-600 hover:text-red-900"
                      >
                        Delete<span class="sr-only">, {{ item.name }}</span>
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="menuItems.length === 0">
                  <td colspan="5" class="px-3 py-4 text-sm text-gray-500 text-center">
                    No menu items found. Add your first menu item to get started.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
