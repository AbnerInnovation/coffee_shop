<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { SparklesIcon, XMarkIcon } from '@heroicons/vue/24/outline';
import { useI18n } from 'vue-i18n';
import type { MenuItemIngredients } from '../menu/IngredientsManager.vue';

export interface SpecialNoteSelection {
  optionSelections: Record<string, string>; // option name -> selected choice
  removedIngredients: string[];
  customNote: string;
}

const props = defineProps<{
  ingredients: MenuItemIngredients | null;
  modelValue: string; // The final special note text
  topNotes?: string[]; // Top 3 most used notes from API
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
}>();

const { t } = useI18n();

// Local state
const selections = ref<SpecialNoteSelection>({
  optionSelections: {},
  removedIngredients: [],
  customNote: ''
});

// Initialize selections with defaults
onMounted(() => {
  if (props.ingredients?.options) {
    const defaultSelections: Record<string, string> = {};
    props.ingredients.options.forEach(option => {
      defaultSelections[option.name] = option.default;
    });
    selections.value.optionSelections = defaultSelections;
  }
});

// Build the special note text from selections
const buildSpecialNote = () => {
  const parts: string[] = [];

  // Add option selections (only if different from default)
  if (props.ingredients?.options) {
    props.ingredients.options.forEach(option => {
      const selected = selections.value.optionSelections[option.name];
      if (selected && selected !== option.default) {
        parts.push(`${option.name}: ${selected}`);
      }
    });
  }

  // Add removed ingredients
  if (selections.value.removedIngredients.length > 0) {
    const removed = selections.value.removedIngredients.map(item => `Sin ${item}`).join(', ');
    parts.push(removed);
  }

  // Add custom note
  if (selections.value.customNote.trim()) {
    parts.push(selections.value.customNote.trim());
  }

  const finalNote = parts.join(' | ');
  emit('update:modelValue', finalNote);
};

// Toggle removable ingredient
const toggleRemovable = (ingredient: string) => {
  const index = selections.value.removedIngredients.indexOf(ingredient);
  if (index > -1) {
    selections.value.removedIngredients.splice(index, 1);
  } else {
    selections.value.removedIngredients.push(ingredient);
  }
  buildSpecialNote();
};

// Update option selection
const updateOption = (optionName: string, choice: string) => {
  selections.value.optionSelections[optionName] = choice;
  buildSpecialNote();
};

// Update custom note
const updateCustomNote = () => {
  buildSpecialNote();
};

// Use a top note
const useTopNote = (note: string) => {
  selections.value.customNote = note;
  buildSpecialNote();
};

// Clear all selections
const clearAll = () => {
  // Reset to defaults
  if (props.ingredients?.options) {
    const defaultSelections: Record<string, string> = {};
    props.ingredients.options.forEach(option => {
      defaultSelections[option.name] = option.default;
    });
    selections.value.optionSelections = defaultSelections;
  }
  selections.value.removedIngredients = [];
  selections.value.customNote = '';
  emit('update:modelValue', '');
};

// Check if ingredient is selected for removal
const isRemoved = (ingredient: string) => {
  return selections.value.removedIngredients.includes(ingredient);
};
</script>

<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <SparklesIcon class="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
        <h3 class="text-sm font-medium text-gray-900 dark:text-gray-100">
          {{ t('app.views.orders.special_notes.title') }}
        </h3>
      </div>
      <button
        v-if="modelValue"
        @click="clearAll"
        type="button"
        class="text-xs text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
      >
        {{ t('app.views.orders.special_notes.clear') }}
      </button>
    </div>

    <!-- Top Notes (if available) -->
    <div v-if="topNotes && topNotes.length > 0" class="space-y-2">
      <p class="text-xs text-gray-600 dark:text-gray-400">
        {{ t('app.views.orders.special_notes.popular') }}:
      </p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="(note, index) in topNotes"
          :key="index"
          @click="useTopNote(note)"
          type="button"
          class="px-3 py-1 text-xs font-medium text-indigo-600 bg-indigo-50 rounded-full hover:bg-indigo-100 transition-colors dark:text-indigo-300 dark:bg-indigo-900/30 dark:hover:bg-indigo-900/50"
        >
          {{ note }}
        </button>
      </div>
    </div>

    <!-- Ingredient Options -->
    <div v-if="ingredients?.options && ingredients.options.length > 0" class="space-y-3">
      <p class="text-xs font-medium text-gray-700 dark:text-gray-300">
        {{ t('app.views.orders.special_notes.customize') }}:
      </p>
      <div
        v-for="option in ingredients.options"
        :key="option.name"
        class="space-y-2"
      >
        <label class="text-xs text-gray-600 dark:text-gray-400">{{ option.name }}</label>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="choice in option.choices"
            :key="choice"
            @click="updateOption(option.name, choice)"
            type="button"
            :class="[
              'px-3 py-1.5 text-xs font-medium rounded-md transition-colors',
              selections.optionSelections[option.name] === choice
                ? 'bg-indigo-600 text-white dark:bg-indigo-500'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600'
            ]"
          >
            {{ choice }}
          </button>
        </div>
      </div>
    </div>

    <!-- Removable Ingredients -->
    <div v-if="ingredients?.removable && ingredients.removable.length > 0" class="space-y-2">
      <p class="text-xs font-medium text-gray-700 dark:text-gray-300">
        {{ t('app.views.orders.special_notes.remove') }}:
      </p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="ingredient in ingredients.removable"
          :key="ingredient"
          @click="toggleRemovable(ingredient)"
          type="button"
          :class="[
            'px-3 py-1.5 text-xs font-medium rounded-md transition-colors',
            isRemoved(ingredient)
              ? 'bg-red-100 text-red-700 line-through dark:bg-red-900/30 dark:text-red-300'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600'
          ]"
        >
          {{ ingredient }}
        </button>
      </div>
    </div>

    <!-- Custom Note -->
    <div class="space-y-2">
      <label class="text-xs font-medium text-gray-700 dark:text-gray-300">
        {{ t('app.views.orders.special_notes.custom') }}:
      </label>
      <textarea
        v-model="selections.customNote"
        @input="updateCustomNote"
        rows="2"
        :placeholder="t('app.views.orders.special_notes.custom_placeholder')"
        class="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100 dark:placeholder-gray-400"
      />
    </div>

    <!-- Preview -->
    <div v-if="modelValue" class="p-3 bg-indigo-50 border border-indigo-200 rounded-lg dark:bg-indigo-900/20 dark:border-indigo-800">
      <p class="text-xs font-medium text-indigo-900 mb-1 dark:text-indigo-200">
        {{ t('app.views.orders.special_notes.preview') }}:
      </p>
      <p class="text-sm text-indigo-700 dark:text-indigo-300">{{ modelValue }}</p>
    </div>

    <!-- Empty State -->
    <div v-else class="p-3 bg-gray-50 border border-gray-200 rounded-lg dark:bg-gray-800 dark:border-gray-700">
      <p class="text-xs text-gray-500 text-center dark:text-gray-400">
        {{ t('app.views.orders.special_notes.empty') }}
      </p>
    </div>
  </div>
</template>
