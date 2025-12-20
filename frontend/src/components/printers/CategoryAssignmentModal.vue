<template>
  <div class="fixed inset-0 z-50 overflow-y-auto" @click.self="$emit('close')">
    <div class="flex min-h-screen items-center justify-center p-4">
      <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"></div>
      
      <div class="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ t('app.views.printers.assign_categories_title') }}
          </h2>
          <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
            {{ t('app.views.printers.assign_categories_description', { name: printer?.name }) }}
          </p>
        </div>

        <!-- Content -->
        <div class="px-6 py-4">
          <!-- Selection Summary -->
          <div class="mb-4 p-3 bg-indigo-50 dark:bg-indigo-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
            <div class="flex items-center justify-between">
              <span class="text-sm font-medium text-indigo-900 dark:text-indigo-200">
                {{ selectedCategories.length }} {{ selectedCategories.length === 1 ? 'categoría seleccionada' : 'categorías seleccionadas' }}
              </span>
              <button
                v-if="selectedCategories.length > 0"
                @click="selectedCategories = []"
                class="text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 font-medium"
              >
                Limpiar todo
              </button>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="mb-4 flex gap-2">
            <button
              @click="selectAll"
              class="px-3 py-1.5 text-xs font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              Seleccionar todas
            </button>
            <button
              @click="selectedCategories = []"
              class="px-3 py-1.5 text-xs font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              Deseleccionar todas
            </button>
          </div>

          <!-- Categories Grid -->
          <div class="grid grid-cols-2 gap-2 max-h-96 overflow-y-auto pr-2">
            <label
              v-for="category in categories"
              :key="category.id"
              :class="[
                'flex items-center p-3 rounded-lg cursor-pointer transition-all border-2',
                selectedCategories.includes(Number(category.id))
                  ? 'bg-indigo-50 dark:bg-indigo-900/20 border-indigo-500 dark:border-indigo-600'
                  : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              ]"
            >
              <input
                v-model="selectedCategories"
                :value="Number(category.id)"
                type="checkbox"
                class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 h-4 w-4"
              />
              <span 
                :class="[
                  'ml-3 text-sm font-medium',
                  selectedCategories.includes(Number(category.id))
                    ? 'text-indigo-900 dark:text-indigo-200'
                    : 'text-gray-900 dark:text-white'
                ]"
              >
                {{ category.name }}
              </span>
            </label>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 bg-gray-50 dark:bg-gray-900/50 border-t border-gray-200 dark:border-gray-700 flex justify-end space-x-3">
          <button
            type="button"
            @click="$emit('close')"
            class="px-5 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600 transition-colors"
          >
            {{ t('app.actions.cancel') }}
          </button>
          <button
            type="button"
            @click="handleSave"
            class="px-5 py-2.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors shadow-sm"
          >
            {{ t('app.actions.save') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import type { Printer } from '@/services/printerService';
import type { Category } from '@/services/menuService';

const { t } = useI18n();

const props = defineProps<{
  printer?: Printer | null;
  categories: Category[];
}>();

const emit = defineEmits<{
  close: [];
  save: [categoryIds: number[]];
}>();

const selectedCategories = ref<number[]>([]);

watch(() => props.printer, (printer) => {
  if (printer) {
    selectedCategories.value = [...printer.category_ids];
  }
}, { immediate: true });

const selectAll = () => {
  selectedCategories.value = props.categories.map(c => Number(c.id));
};

const handleSave = () => {
  emit('save', selectedCategories.value);
};
</script>
