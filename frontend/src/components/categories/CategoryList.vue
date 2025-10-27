<template>
  <div class="mt-8 flow-root">
    <div class="overflow-x-auto">
      <div class="inline-block min-w-full py-2 align-middle">
        <!-- Loading State -->
        <div v-if="loading" class="text-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
        </div>
        
        <!-- Categories List -->
        <div v-else class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg dark:bg-gray-950">
          <!-- Empty State -->
          <div v-if="categories.length === 0" class="text-center py-12 text-sm text-gray-500 dark:text-gray-400">
            {{ emptyMessage }}
          </div>
          
          <!-- Categories -->
          <ul v-else class="divide-y divide-gray-200 dark:divide-gray-700 bg-white dark:bg-gray-900">
            <li 
              v-for="category in categories" 
              :key="category.id" 
              :data-dropdown-container="`category-${category.id}`" 
              class="px-4 py-4 sm:px-6 relative hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
            >
              <div class="flex items-center justify-between">
                <div class="flex-1 min-w-0 pr-12">
                  <div class="flex items-center gap-2">
                    <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {{ category.name }}
                    </p>
                    <!-- Kitchen Visibility Badge -->
                    <span 
                      v-if="(category as any).visible_in_kitchen === false"
                      class="inline-flex items-center rounded-full bg-amber-100 dark:bg-amber-900/30 px-2 py-0.5 text-xs font-medium text-amber-800 dark:text-amber-300"
                      :title="$t('app.forms.visible_in_kitchen_help')"
                    >
                      <svg class="mr-1 h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                      </svg>
                      Oculto en cocina
                    </span>
                  </div>
                  <p v-if="category.description" class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    {{ category.description }}
                  </p>
                </div>
                
                <!-- Actions Dropdown -->
                <div v-if="category.id && canEdit" class="absolute top-4 right-4" @click.stop>
                  <DropdownMenu
                    :id="`category-${category.id}`"
                    button-label="Category actions"
                    width="md"
                  >
                    <DropdownMenuItem
                      :icon="PencilIcon"
                      variant="default"
                      @click="$emit('edit', category)"
                    >
                      {{ $t('app.actions.edit') }}
                    </DropdownMenuItem>
                    
                    <DropdownMenuDivider />
                    
                    <DropdownMenuItem
                      :icon="TrashIcon"
                      variant="danger"
                      @click="$emit('delete', category)"
                    >
                      {{ $t('app.actions.delete') }}
                    </DropdownMenuItem>
                  </DropdownMenu>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import DropdownMenu from '@/components/ui/DropdownMenu.vue';
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue';
import DropdownMenuDivider from '@/components/ui/DropdownMenuDivider.vue';
import { PencilIcon, TrashIcon } from '@heroicons/vue/24/outline';
import type { MenuCategory } from '@/types/menu';

defineProps<{
  categories: MenuCategory[];
  loading: boolean;
  canEdit: boolean;
  emptyMessage: string;
}>();

defineEmits<{
  edit: [category: MenuCategory];
  delete: [category: MenuCategory];
}>();
</script>
