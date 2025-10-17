<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { PlusIcon, XMarkIcon, TrashIcon, PencilIcon, DocumentDuplicateIcon } from '@heroicons/vue/24/outline';
import { useI18n } from 'vue-i18n';
import { useMenuStore } from '@/stores/menu';
import DropdownMenu from '@/components/ui/DropdownMenu.vue';
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue';

export interface IngredientOption {
  name: string;
  choices: string[];
  default: string;
}

export interface MenuItemIngredients {
  options: IngredientOption[];
  removable: string[];
}

const props = defineProps<{
  modelValue: MenuItemIngredients | null;
  categoryId?: number | string;
  currentItemId?: number | string;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: MenuItemIngredients | null): void;
}>();

const { t } = useI18n();
const menuStore = useMenuStore();

// Local state for editing
const newOptionName = ref('');
const newOptionChoices = ref('');
const newOptionDefault = ref('');
const newRemovable = ref('');
const editingOptionIndex = ref<number | null>(null);

// Dropdown menu state
const openMenus = ref<Record<string, boolean>>({});

// State for copying from other products
const availableProducts = ref<Array<{ id: number | string; name: string; ingredients: MenuItemIngredients | null }>>([]);
const loadingProducts = ref(false);
const selectedProductId = ref<string>('');

// Computed for local ingredients
const localIngredients = computed({
  get: () => props.modelValue || { options: [], removable: [] },
  set: (value) => emit('update:modelValue', value)
});

// Edit existing option
const editOption = (index: number) => {
  const option = localIngredients.value.options[index];
  newOptionName.value = option.name;
  newOptionChoices.value = option.choices.join(', ');
  newOptionDefault.value = option.default;
  editingOptionIndex.value = index;
};

// Cancel editing
const cancelEdit = () => {
  newOptionName.value = '';
  newOptionChoices.value = '';
  newOptionDefault.value = '';
  editingOptionIndex.value = null;
};

// Add or update ingredient option
const addOption = () => {
  if (!newOptionName.value.trim() || !newOptionChoices.value.trim()) {
    return;
  }

  const choices = newOptionChoices.value
    .split(',')
    .map(c => c.trim())
    .filter(c => c.length > 0);

  if (choices.length < 2) {
    return;
  }

  const defaultChoice = newOptionDefault.value.trim() || choices[0];

  const newOption: IngredientOption = {
    name: newOptionName.value.trim(),
    choices,
    default: defaultChoice
  };

  let updated;
  if (editingOptionIndex.value !== null) {
    // Update existing option
    const updatedOptions = [...localIngredients.value.options];
    updatedOptions[editingOptionIndex.value] = newOption;
    updated = {
      ...localIngredients.value,
      options: updatedOptions
    };
  } else {
    // Add new option
    updated = {
      ...localIngredients.value,
      options: [...localIngredients.value.options, newOption]
    };
  }

  emit('update:modelValue', updated);
  cancelEdit();
};

// Remove ingredient option
const removeOption = (index: number) => {
  const updated = {
    ...localIngredients.value,
    options: localIngredients.value.options.filter((_, i) => i !== index)
  };
  emit('update:modelValue', updated);
};

// Add removable ingredient
const addRemovable = () => {
  if (!newRemovable.value.trim()) {
    return;
  }

  const ingredient = newRemovable.value.trim();
  
  if (localIngredients.value.removable.includes(ingredient)) {
    return;
  }

  const updated = {
    ...localIngredients.value,
    removable: [...localIngredients.value.removable, ingredient]
  };

  emit('update:modelValue', updated);
  newRemovable.value = '';
};

// Remove removable ingredient
const removeRemovable = (index: number) => {
  const updated = {
    ...localIngredients.value,
    removable: localIngredients.value.removable.filter((_, i) => i !== index)
  };
  emit('update:modelValue', updated);
};

// Clear all ingredients
const clearAll = () => {
  emit('update:modelValue', null);
};

// Load products with ingredients for copying
const loadProductsForCopying = async () => {
  if (!props.categoryId) {
    return;
  }
  
  loadingProducts.value = true;
  try {
    const items = await menuStore.fetchMenuItems(Number(props.categoryId));
    
    availableProducts.value = items
      .filter(item => {
        // Exclude current item and items without ingredients
        const hasIngredients = item.ingredients && (item.ingredients.options.length > 0 || item.ingredients.removable.length > 0);
        const isDifferent = item.id !== props.currentItemId;
        return isDifferent && hasIngredients;
      })
      .map(item => ({
        id: item.id!,
        name: item.name,
        ingredients: item.ingredients || null
      }));
  } catch (error) {
    console.error('Error loading products:', error);
  } finally {
    loadingProducts.value = false;
  }
};

// Copy ingredients from another product
const copyFromProduct = (productId: number | string) => {
  if (!productId || productId === '') {
    return;
  }
  
  const product = availableProducts.value.find(p => String(p.id) === String(productId));
  
  if (product && product.ingredients) {
    // Deep clone to avoid reference issues
    const copiedIngredients: MenuItemIngredients = {
      options: product.ingredients.options.map(opt => ({
        name: opt.name,
        choices: [...opt.choices],
        default: opt.default
      })),
      removable: [...product.ingredients.removable]
    };
    emit('update:modelValue', copiedIngredients);
    
    // Reset selection after copying
    selectedProductId.value = '';
  }
};

// Computed for products with ingredients
const productsWithIngredients = computed(() => {
  return availableProducts.value.filter(p => 
    p.ingredients && (p.ingredients.options.length > 0 || p.ingredients.removable.length > 0)
  );
});

// Load products on mount if categoryId is provided
onMounted(() => {
  if (props.categoryId) {
    loadProductsForCopying();
  }
});

// Watch for categoryId changes
watch(() => props.categoryId, (newCategoryId) => {
  if (newCategoryId) {
    loadProductsForCopying();
  }
});
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
        {{ t('app.views.menu.ingredients.title') }}
      </h3>
      <div class="flex items-center gap-2">
        <button
          v-if="localIngredients.options.length > 0 || localIngredients.removable.length > 0"
          @click="clearAll"
          type="button"
          class="text-sm text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
        >
          {{ t('app.views.menu.ingredients.clear_all') }}
        </button>
      </div>
    </div>

    <!-- Copy from Product Section -->
    <div v-if="productsWithIngredients.length > 0" class="p-3 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg">
      <div class="flex items-start gap-3">
        <DocumentDuplicateIcon class="h-5 w-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
            {{ t('app.views.menu.ingredients.copy_from_product') }}
          </p>
          <select
            v-model="selectedProductId"
            @change="copyFromProduct(selectedProductId)"
            class="w-full px-3 py-2 text-sm border border-blue-300 dark:border-blue-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">{{ t('app.views.menu.ingredients.select_product') }}</option>
            <option 
              v-for="product in productsWithIngredients" 
              :key="product.id"
              :value="product.id"
            >
              {{ product.name }}
            </option>
          </select>
          <p class="text-xs text-blue-700 dark:text-blue-300 mt-1">
            {{ t('app.views.menu.ingredients.copy_hint') }}
          </p>
        </div>
      </div>
    </div>

    <!-- Ingredient Options Section -->
    <div class="space-y-4">
      <div>
        <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {{ t('app.views.menu.ingredients.options_title') }}
        </h4>
        <p class="text-xs text-gray-500 dark:text-gray-400 mb-3">
          {{ t('app.views.menu.ingredients.options_description') }}
        </p>

        <!-- Existing Options -->
        <div v-if="localIngredients.options.length > 0" class="space-y-2 mb-3">
          <div
            v-for="(option, index) in localIngredients.options"
            :key="index"
            class="flex items-start gap-2 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
          >
            <div class="flex-1 min-w-0">
              <div class="font-medium text-sm text-gray-900 dark:text-gray-100">{{ option.name }}</div>
              <div class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                {{ t('app.views.menu.ingredients.choices') }}: {{ option.choices.join(', ') }}
              </div>
              <div class="text-xs text-indigo-600 dark:text-indigo-400 mt-1">
                {{ t('app.views.menu.ingredients.default') }}: {{ option.default }}
              </div>
            </div>
            <div class="flex-shrink-0">
              <DropdownMenu v-model="openMenus[`option-${index}`]" width="sm">
                <DropdownMenuItem 
                  :icon="PencilIcon" 
                  variant="primary"
                  @click="editOption(index)"
                >
                  {{ t('app.actions.edit') }}
                </DropdownMenuItem>
                
                <DropdownMenuItem 
                  :icon="TrashIcon" 
                  variant="danger"
                  @click="removeOption(index)"
                >
                  {{ t('app.actions.delete') }}
                </DropdownMenuItem>
              </DropdownMenu>
            </div>
          </div>
        </div>

        <!-- Add/Edit Option Form -->
        <div class="space-y-2 p-3 border border-gray-200 dark:border-gray-700 rounded-lg" :class="editingOptionIndex !== null ? 'border-indigo-500 dark:border-indigo-400' : ''">
          <div v-if="editingOptionIndex !== null" class="flex items-center justify-between mb-2">
            <span class="text-sm font-medium text-indigo-600 dark:text-indigo-400">{{ t('app.actions.edit') }}</span>
            <button
              @click="cancelEdit"
              type="button"
              class="text-sm text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
            >
              {{ t('app.actions.cancel') }}
            </button>
          </div>
          <input
            v-model="newOptionName"
            type="text"
            :placeholder="t('app.views.menu.ingredients.option_name_placeholder')"
            @keydown.enter.prevent="addOption"
            class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <input
            v-model="newOptionChoices"
            type="text"
            :placeholder="t('app.views.menu.ingredients.choices_placeholder')"
            @keydown.enter.prevent="addOption"
            class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <input
            v-model="newOptionDefault"
            type="text"
            :placeholder="t('app.views.menu.ingredients.default_placeholder')"
            @keydown.enter.prevent="addOption"
            class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            @click="addOption"
            type="button"
            class="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/30 rounded-md hover:bg-indigo-100 dark:hover:bg-indigo-900/50"
          >
            <PlusIcon v-if="editingOptionIndex === null" class="h-4 w-4" />
            <PencilIcon v-else class="h-4 w-4" />
            {{ editingOptionIndex !== null ? t('app.actions.update') : t('app.views.menu.ingredients.add_option') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Removable Ingredients Section -->
    <div class="space-y-4">
      <div>
        <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {{ t('app.views.menu.ingredients.removable_title') }}
        </h4>
        <p class="text-xs text-gray-500 dark:text-gray-400 mb-3">
          {{ t('app.views.menu.ingredients.removable_description') }}
        </p>

        <!-- Existing Removable -->
        <div v-if="localIngredients.removable.length > 0" class="flex flex-wrap gap-2 mb-3">
          <div
            v-for="(item, index) in localIngredients.removable"
            :key="index"
            class="inline-flex items-center gap-1 px-3 py-1 bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 text-sm rounded-full"
          >
            <span>{{ item }}</span>
            <button
              @click="removeRemovable(index)"
              type="button"
              class="hover:text-amber-900 dark:hover:text-amber-100"
            >
              <XMarkIcon class="h-3 w-3" />
            </button>
          </div>
        </div>

        <!-- Add New Removable Form -->
        <div class="flex gap-2">
          <input
            v-model="newRemovable"
            type="text"
            :placeholder="t('app.views.menu.ingredients.removable_placeholder')"
            @keydown.enter.prevent="addRemovable"
            class="flex-1 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            @click="addRemovable"
            type="button"
            class="flex-shrink-0 flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-white bg-indigo-600 dark:bg-indigo-500 rounded-md hover:bg-indigo-700 dark:hover:bg-indigo-600"
          >
            <PlusIcon class="h-4 w-4" />
            {{ t('app.views.menu.ingredients.add') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Info Box -->
    <div class="p-3 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg">
      <p class="text-xs text-blue-800 dark:text-blue-200">
        <strong>{{ t('app.views.menu.ingredients.info_title') }}:</strong>
        {{ t('app.views.menu.ingredients.info_text') }}
      </p>
    </div>
  </div>
</template>
