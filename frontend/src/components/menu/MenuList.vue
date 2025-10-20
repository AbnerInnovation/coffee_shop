<script setup lang="ts">
import { ref } from 'vue';
import { XCircleIcon } from '@heroicons/vue/20/solid';
import { FunnelIcon, PencilIcon, TrashIcon, CheckCircleIcon, XCircleIcon as XCircleIconOutline } from '@heroicons/vue/24/outline';
import type { MenuItem, MenuItemVariant, MenuCategory } from '@/types/menu';
import { useI18n } from 'vue-i18n';
import { usePermissions } from '@/composables/usePermissions';
import PageHeader from '@/components/layout/PageHeader.vue';
import DropdownMenu from '@/components/ui/DropdownMenu.vue';
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue';
import DropdownMenuDivider from '@/components/ui/DropdownMenuDivider.vue';

interface Props {
  menuItems: MenuItem[];
  loading: boolean;
  error: string | null;
  categories: MenuCategory[];
  selectedCategoryId: number | null;
}

interface Emits {
  (e: 'add-item'): void;
  (e: 'edit-item', item: MenuItem): void;
  (e: 'delete-item', item: MenuItem): void;
  (e: 'toggle-availability', item: MenuItem): void;
  (e: 'filter-category', categoryId: number | null): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();
const { t } = useI18n();
const { canEditMenu } = usePermissions();

// Menu states for dropdowns
const menuStates = ref<Record<string | number, boolean>>({});

// Helper to ensure menu state exists
const ensureMenuState = (itemId: number | string | undefined) => {
  if (itemId !== undefined && !(itemId in menuStates.value)) {
    menuStates.value[itemId] = false;
  }
};

// Helper to close menu and execute action
const closeMenuAndExecute = (itemId: number | string | undefined, action: () => void) => {
  if (itemId !== undefined) {
    menuStates.value[itemId] = false;
  }
  action();
};

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
  <div>
    <PageHeader
      :title="t('app.views.menu.list.title')"
      :subtitle="t('app.views.menu.list.subtitle')"
    >
      <template #actions>
        <button
          v-if="canEditMenu"
          type="button"
          @click="$emit('add-item')"
          class="block rounded-md bg-indigo-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
        >
          {{ t('app.views.menu.list.add') }}
        </button>
      </template>
    </PageHeader>
    
    <!-- Category Filter -->
    <div class="mt-4 flex flex-col sm:flex-row sm:items-center gap-3">
      <div class="flex items-center gap-2">
        <FunnelIcon class="h-5 w-5 text-gray-400 dark:text-gray-500" />
        <label for="category-filter" class="text-sm font-medium text-gray-700 dark:text-gray-300">
          {{ t('app.views.menu.list.filter_by_category') }}
        </label>
      </div>
      <select
        id="category-filter"
        :value="selectedCategoryId || ''"
        @change="$emit('filter-category', ($event.target as HTMLSelectElement).value ? Number(($event.target as HTMLSelectElement).value) : null)"
        class="flex-1 sm:flex-initial rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
      >
        <option value="">{{ t('app.views.menu.list.all_categories') }}</option>
        <option v-for="category in categories" :key="category.id" :value="category.id">
          {{ category.name }}
        </option>
      </select>
    </div>
    <div class="mt-8 flow-root">
      <div class="overflow-x-auto">
        <div class="inline-block min-w-full py-2 align-middle">
          <div v-if="loading" class="text-center py-4">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
          </div>
          <div v-else-if="error" class="rounded-md bg-red-50 p-4 mb-4 dark:bg-red-950">
            <div class="flex">
              <div class="flex-shrink-0">
                <XCircleIcon class="h-5 w-5 text-red-400" aria-hidden="true" />
              </div>
              <div class="ml-3">
                <h3 class="text-sm font-medium text-red-800">{{ t('app.views.menu.list.error_title') }}</h3>
                <div class="mt-2 text-sm text-red-700">
                  <p>{{ error }}</p>
                </div>
              </div>
            </div>
          </div>
          <div v-else>
          <!-- Mobile Card View -->
          <div class="block md:hidden">
            <div v-if="menuItems.length === 0" class="text-center py-8 text-sm text-gray-500 dark:text-gray-400">
              {{ t('app.views.menu.list.empty') }}
            </div>
            <div v-else class="space-y-4">
              <div 
                v-for="item in menuItems" 
                :key="item.id"
                :data-dropdown-container="`menu-item-${item.id}`"
                class="bg-white dark:bg-gray-900 rounded-lg shadow border border-gray-200 dark:border-gray-800 p-4 relative"
              >
                <!-- Three Dots Menu (only for admin/sysadmin) -->
                <div v-if="item.id && canEditMenu" class="absolute top-3 right-3 z-30" @click.stop>
                  <DropdownMenu
                    :id="`menu-item-${item.id}`"
                    button-label="Menu item actions"
                    width="md"
                  >
                    <DropdownMenuItem
                      :icon="PencilIcon"
                      variant="default"
                      @click="closeMenuAndExecute(item.id, () => $emit('edit-item', item))"
                    >
                      {{ t('app.views.menu.list.edit') }}
                    </DropdownMenuItem>
                    
                    <DropdownMenuItem
                      :icon="isItemAvailable(item) ? XCircleIconOutline : CheckCircleIcon"
                      :variant="isItemAvailable(item) ? 'warning' : 'success'"
                      @click="closeMenuAndExecute(item.id, () => $emit('toggle-availability', item))"
                    >
                      {{ isItemAvailable(item) ? t('app.views.menu.list.disable') : t('app.views.menu.list.enable') }}
                    </DropdownMenuItem>
                    
                    <DropdownMenuDivider />
                    
                    <DropdownMenuItem
                      :icon="TrashIcon"
                      variant="danger"
                      @click="closeMenuAndExecute(item.id, () => $emit('delete-item', item))"
                    >
                      {{ t('app.views.menu.list.delete') }}
                    </DropdownMenuItem>
                  </DropdownMenu>
                </div>
                
                <!-- Item Header -->
                <div class="flex items-start gap-3 mb-3">
                  <div v-if="getImageUrl(item)" class="flex-shrink-0">
                    <img class="h-16 w-16 rounded-lg object-cover" :src="getImageUrl(item)" :alt="item.name" />
                  </div>
                  <div class="flex-1 min-w-0 pr-8">
                    <h3 class="text-base font-semibold text-gray-900 dark:text-gray-100">{{ item.name }}</h3>
                    <div class="mt-1 flex items-center gap-2 flex-wrap">
                      <span 
                        v-if="item.category"
                        class="inline-flex items-center rounded-md bg-blue-50 dark:bg-blue-950 px-2 py-0.5 text-xs font-medium text-blue-700 dark:text-blue-100"
                      >
                        {{ typeof item.category === 'string' ? item.category : item.category.name }}
                      </span>
                      <span 
                        :class="{
                          'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200': isItemAvailable(item),
                          'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200': !isItemAvailable(item)
                        }"
                        class="inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium"
                      >
                        {{ isItemAvailable(item) ? t('app.views.menu.list.available') : t('app.views.menu.list.unavailable') }}
                      </span>
                    </div>
                  </div>
                </div>

                <!-- Pricing -->
                <div class="mb-3 space-y-1">
                  <template v-if="item.variants && item.variants.length > 0">
                    <div v-if="item.price" class="flex justify-between items-center text-sm">
                      <span class="text-gray-600 dark:text-gray-400">Base:</span>
                      <div class="flex items-center gap-2">
                        <span v-if="item.discount_price && item.discount_price > 0" class="text-gray-500 dark:text-gray-400 line-through text-xs">
                          ${{ item.price.toFixed(2) }}
                        </span>
                        <span class="font-semibold" :class="item.discount_price && item.discount_price > 0 ? 'text-green-600 dark:text-green-400' : 'text-gray-900 dark:text-white'">
                          ${{ (item.discount_price && item.discount_price > 0 ? item.discount_price : item.price).toFixed(2) }}
                        </span>
                        <span v-if="item.discount_price && item.discount_price > 0" class="inline-flex items-center rounded-full bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 text-xs font-medium text-green-800 dark:text-green-200">
                          {{ t('app.forms.sale_badge') }}
                        </span>
                      </div>
                    </div>
                    <div v-for="variant in item.variants" :key="variant.id" class="flex justify-between items-center text-sm">
                      <span class="text-gray-600 dark:text-gray-400">{{ variant.name }}:</span>
                      <div class="flex items-center gap-2">
                        <span v-if="variant.discount_price && variant.discount_price > 0" class="text-gray-500 dark:text-gray-400 line-through text-xs">
                          ${{ variant.price.toFixed(2) }}
                        </span>
                        <span class="font-semibold" :class="variant.discount_price && variant.discount_price > 0 ? 'text-green-600 dark:text-green-400' : 'text-gray-900 dark:text-white'">
                          ${{ (variant.discount_price && variant.discount_price > 0 ? variant.discount_price : variant.price).toFixed(2) }}
                        </span>
                        <span v-if="variant.discount_price && variant.discount_price > 0" class="inline-flex items-center rounded-full bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 text-xs font-medium text-green-800 dark:text-green-200">
                          {{ t('app.forms.sale_badge') }}
                        </span>
                      </div>
                    </div>
                  </template>
                  <template v-else>
                    <div class="flex justify-between items-center">
                      <span class="text-sm text-gray-600 dark:text-gray-400">{{ t('app.views.menu.list.table.price') }}:</span>
                      <div class="flex items-center gap-2">
                        <span v-if="item.discount_price && item.discount_price > 0" class="text-gray-500 dark:text-gray-400 line-through text-sm">
                          ${{ item.price?.toFixed(2) || '0.00' }}
                        </span>
                        <span class="text-lg font-semibold" :class="item.discount_price && item.discount_price > 0 ? 'text-green-600 dark:text-green-400' : 'text-gray-900 dark:text-white'">
                          ${{ (item.discount_price && item.discount_price > 0 ? item.discount_price : item.price)?.toFixed(2) || '0.00' }}
                        </span>
                        <span v-if="item.discount_price && item.discount_price > 0" class="inline-flex items-center rounded-full bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 text-xs font-medium text-green-800 dark:text-green-200">
                          {{ t('app.forms.sale_badge') }}
                        </span>
                      </div>
                    </div>
                  </template>
                </div>

                <!-- Actions removed - now in dropdown menu -->
              </div>
            </div>
          </div>

          <!-- Desktop Table View -->
          <div class="hidden md:block overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg dark:bg-gray-950">
            <table class="min-w-full divide-y divide-gray-300 dark:divide-gray-700">
              <thead class="bg-gray-50 dark:bg-gray-900">
                <tr>
                  <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 dark:text-gray-100 sm:pl-6">{{ t('app.views.menu.list.table.name') }}</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">{{ t('app.views.menu.list.table.category') }}</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">{{ t('app.views.menu.list.table.price') }}</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 dark:text-gray-100">{{ t('app.views.menu.list.table.status') }}</th>
                  <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
                    <span class="sr-only">{{ t('app.views.menu.list.table.actions') }}</span>
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-700 bg-white dark:bg-gray-900">
                <tr v-for="item in menuItems" :key="item.id" :data-dropdown-container="`menu-item-desktop-${item.id}`" class="relative">
                  <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6 dark:text-gray-100">
                    <div class="flex items-center">
                      <div v-if="getImageUrl(item)" class="h-10 w-10 flex-shrink-0">
                        <img class="h-10 w-10 rounded-full object-cover" :src="getImageUrl(item)" :alt="item.name" />
                      </div>
                      <div :class="{ 'ml-4': getImageUrl(item) }">
                        {{ item.name }}
                        <div v-if="item.variants && item.variants.length > 0" class="text-xs text-gray-500">
                          {{ t('app.views.menu.list.variants', { count: item.variants.length }) }}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500 dark:text-gray-400">
                    <span 
                      v-if="item.category"
                      class="inline-flex items-center rounded-md bg-blue-50 dark:bg-blue-950 px-2 py-1 text-xs font-medium text-blue-700 dark:text-blue-100 ring-1 ring-inset ring-blue-700/10"
                    >
                      {{ typeof item.category === 'string' ? item.category : item.category.name }}
                    </span>
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm dark:text-gray-300 text-gray-700">
                    <template v-if="item.variants && item.variants.length > 0">
                      <div v-if="item.price" class="flex justify-between items-center gap-2">
                        <span class="dark:text-gray-400 text-gray-700">Base:</span>
                        <div class="flex items-center gap-2">
                          <span v-if="item.discount_price && item.discount_price > 0" class="text-gray-500 dark:text-gray-400 line-through text-xs">
                            ${{ item.price.toFixed(2) }}
                          </span>
                          <span class="font-medium" :class="item.discount_price && item.discount_price > 0 ? 'text-green-600 dark:text-green-400' : ''">
                            ${{ (item.discount_price && item.discount_price > 0 ? item.discount_price : item.price).toFixed(2) }}
                          </span>
                          <span v-if="item.discount_price && item.discount_price > 0" class="inline-flex items-center rounded-full bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 text-xs font-medium text-green-800 dark:text-green-200">
                            {{ t('app.forms.sale_badge') }}
                          </span>
                        </div>
                      </div>
                      <div v-for="variant in item.variants" :key="variant.id" class="flex justify-between items-center gap-2">
                        <span class="dark:text-gray-400 text-gray-700">{{ variant.name }}:</span>
                        <div class="flex items-center gap-2">
                          <span v-if="variant.discount_price && variant.discount_price > 0" class="text-gray-500 dark:text-gray-400 line-through text-xs">
                            ${{ variant.price.toFixed(2) }}
                          </span>
                          <span class="font-medium" :class="variant.discount_price && variant.discount_price > 0 ? 'text-green-600 dark:text-green-400' : ''">
                            ${{ (variant.discount_price && variant.discount_price > 0 ? variant.discount_price : variant.price).toFixed(2) }}
                          </span>
                          <span v-if="variant.discount_price && variant.discount_price > 0" class="inline-flex items-center rounded-full bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 text-xs font-medium text-green-800 dark:text-green-200">
                            {{ t('app.forms.sale_badge') }}
                          </span>
                        </div>
                      </div>
                    </template>
                    <template v-else>
                      <div class="flex items-center gap-2">
                        <span v-if="item.discount_price && item.discount_price > 0" class="text-gray-500 dark:text-gray-400 line-through">
                          ${{ item.price?.toFixed(2) || '0.00' }}
                        </span>
                        <span class="font-medium" :class="item.discount_price && item.discount_price > 0 ? 'text-green-600 dark:text-green-400' : ''">
                          ${{ (item.discount_price && item.discount_price > 0 ? item.discount_price : item.price)?.toFixed(2) || '0.00' }}
                        </span>
                        <span v-if="item.discount_price && item.discount_price > 0" class="inline-flex items-center rounded-full bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 text-xs font-medium text-green-800 dark:text-green-200">
                          {{ t('app.forms.sale_badge') }}
                        </span>
                      </div>
                    </template>
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm dark:text-gray-400">
                    <span 
                      :class="{
                        'bg-green-100 text-green-800': isItemAvailable(item),
                        'bg-red-100 text-red-800': !isItemAvailable(item)
                      }"
                      class="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ring-green-600/20 dark:bg-green-950 dark:text-green-100"
                    >
                      {{ isItemAvailable(item) ? t('app.views.menu.list.available') : t('app.views.menu.list.unavailable') }}
                    </span>
                  </td>
                  <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6 dark:text-gray-400">
                    <div v-if="item.id && canEditMenu" class="flex justify-end" @click.stop>
                      <DropdownMenu
                        :id="`menu-item-desktop-${item.id}`"
                        button-label="Menu item actions"
                        width="md"
                      >
                        <DropdownMenuItem
                          :icon="PencilIcon"
                          variant="default"
                          @click="closeMenuAndExecute(item.id, () => $emit('edit-item', item))"
                        >
                          {{ t('app.views.menu.list.edit') }}
                        </DropdownMenuItem>
                        
                        <DropdownMenuItem
                          :icon="isItemAvailable(item) ? XCircleIconOutline : CheckCircleIcon"
                          :variant="isItemAvailable(item) ? 'warning' : 'success'"
                          @click="closeMenuAndExecute(item.id, () => $emit('toggle-availability', item))"
                        >
                          {{ isItemAvailable(item) ? t('app.views.menu.list.disable') : t('app.views.menu.list.enable') }}
                        </DropdownMenuItem>
                        
                        <DropdownMenuDivider />
                        
                        <DropdownMenuItem
                          :icon="TrashIcon"
                          variant="danger"
                          @click="closeMenuAndExecute(item.id, () => $emit('delete-item', item))"
                        >
                          {{ t('app.views.menu.list.delete') }}
                        </DropdownMenuItem>
                      </DropdownMenu>
                    </div>
                  </td>
                </tr>
                <tr v-if="menuItems.length === 0">
                  <td colspan="5" class="px-3 py-4 text-sm text-gray-500 text-center">
                    {{ t('app.views.menu.list.empty') }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          </div> <!-- Close v-else wrapper -->
        </div> <!-- Close align-middle wrapper -->
      </div> <!-- Close overflow-x-auto wrapper -->
    </div> <!-- Close flow-root wrapper -->
  </div> <!-- Close main container -->
</template>
