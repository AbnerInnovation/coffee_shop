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
                  <div class="flex items-center gap-2 flex-wrap">
                    <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {{ category.name }}
                    </p>
                    <!-- Kitchen Visibility Badge - Always show -->
                    <span 
                      v-if="getCategoryVisibility(category) === false"
                      class="inline-flex items-center gap-1 rounded-full bg-orange-100 dark:bg-orange-900/30 px-2 py-0.5 text-xs font-medium text-orange-700 dark:text-orange-300"
                      :title="$t('app.forms.visible_in_kitchen_help')"
                    >
                      <EyeSlashIcon class="h-3 w-3" />
                      <span class="hidden sm:inline">{{ $t('app.views.menu.categories.not_in_kitchen') }}</span>
                    </span>
                    <span 
                      v-else
                      class="inline-flex items-center gap-1 rounded-full bg-green-100 dark:bg-green-900/30 px-2 py-0.5 text-xs font-medium text-green-700 dark:text-green-300"
                      :title="$t('app.forms.visible_in_kitchen')"
                    >
                      <EyeIcon class="h-3 w-3" />
                      <span class="hidden sm:inline">{{ $t('app.views.menu.categories.in_kitchen') }}</span>
                    </span>
                  </div>
                  <p v-if="category.description" class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    {{ category.description }}
                  </p>
                  <p v-if="category.created_at" class="text-xs text-gray-400 dark:text-gray-500 mt-1">
                    {{ $t('app.common.created_at') }}: {{ formatDate(category.created_at) }}
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
import { PencilIcon, TrashIcon, EyeIcon, EyeSlashIcon } from '@heroicons/vue/24/outline';
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

// Helper function to safely get category visibility
const getCategoryVisibility = (category: MenuCategory): boolean => {
  // Return the value, defaulting to true if undefined
  return category.visible_in_kitchen ?? true;
};

// Format date helper
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('es-MX', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};
</script>
