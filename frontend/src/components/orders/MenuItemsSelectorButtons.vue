<template>
  <div class="space-y-4">
    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error && categoryNames.length === 0" class="text-center py-4 text-red-600">
      <p>{{ $t('app.views.orders.modals.new_order.error_menu') }}</p>
    </div>

    <!-- Category Buttons -->
    <div v-else class="space-y-4">
      <!-- Category Pills -->
      <div class="flex flex-wrap gap-2">
        <button
          v-for="categoryName in categoryNames"
          :key="categoryName"
          type="button"
          @click="selectCategory(categoryName)"
          class="px-4 py-2 rounded-full text-sm font-medium transition-all"
          :class="selectedCategory === categoryName
            ? 'bg-indigo-600 text-white shadow-md'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'"
        >
          {{ categoryName }}
          <span class="ml-1 text-xs opacity-75">
            ({{ menuItemsByCategory[categoryName]?.length || 0 }})
          </span>
        </button>
      </div>

      <!-- Selected Category Items -->
      <div v-if="selectedCategory && menuItemsByCategory[selectedCategory]" class="space-y-2">
        <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 px-2">
          {{ selectedCategory }}
        </h3>
        <div class="grid grid-cols-1 gap-2">
          <button
            v-for="item in menuItemsByCategory[selectedCategory]"
            :key="item.id"
            type="button"
            @click="$emit('select-item', item)"
            class="flex items-center justify-between p-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-indigo-500 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-all group"
          >
            <div class="flex-1 text-left">
              <div class="flex items-center gap-2">
                <p class="font-medium text-gray-900 dark:text-gray-100">
                  {{ item.name }}
                </p>
                <span v-if="item.has_variants" class="text-xs text-indigo-600 dark:text-indigo-400">
                  {{ $t('app.views.orders.modals.new_order.select_options_hint') }}
                </span>
              </div>
              <div class="flex items-center gap-2 mt-1">
                <!-- Price with discount -->
                <p v-if="item.discount_price && item.discount_price > 0" class="text-xs text-gray-500 dark:text-gray-400 line-through">
                  ${{ (item.price || 0).toFixed(2) }}
                </p>
                <p class="text-sm font-semibold" :class="item.discount_price && item.discount_price > 0 ? 'text-green-600 dark:text-green-400' : 'text-gray-700 dark:text-gray-300'">
                  ${{ (item.discount_price && item.discount_price > 0 ? item.discount_price : item.price || 0).toFixed(2) }}
                </p>
                <span v-if="item.discount_price && item.discount_price > 0" class="inline-flex items-center rounded-full bg-green-100 dark:bg-green-900/30 px-1.5 py-0.5 text-xs font-medium text-green-800 dark:text-green-200">
                  Oferta
                </span>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <!-- Quantity badge -->
              <span v-if="getItemQuantity(item.id) > 0" class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-indigo-600 text-white text-xs font-bold">
                {{ getItemQuantity(item.id) }}
              </span>
              <!-- Add icon -->
              <svg class="w-5 h-5 text-gray-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
            </div>
          </button>
        </div>
      </div>

      <!-- Empty state when no category selected -->
      <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
        <svg class="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <p class="text-sm">Selecciona una categoría para ver los artículos</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';

interface Props {
  loading: boolean | string;
  error: boolean | string | null;
  categoryNames: string[];
  menuItemsByCategory: Record<string, any[]>;
  getItemQuantity: (itemId: number | string) => number;
}

const props = defineProps<Props>();

defineEmits<{
  (e: 'select-item', item: any): void;
}>();

const selectedCategory = ref<string | null>(null);

function selectCategory(categoryName: string) {
  selectedCategory.value = categoryName;
}

// Auto-select first category if only one exists
function autoSelectSingleCategory() {
  if (props.categoryNames.length === 1 && !selectedCategory.value) {
    selectedCategory.value = props.categoryNames[0];
  }
}

// Watch for changes in categoryNames to auto-select
watch(() => props.categoryNames, () => {
  autoSelectSingleCategory();
}, { immediate: true });

// Also check on mount
onMounted(() => {
  autoSelectSingleCategory();
});
</script>
