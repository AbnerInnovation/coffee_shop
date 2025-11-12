<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue';
import { XMarkIcon, PlusIcon, ArrowPathIcon, TrashIcon, ExclamationTriangleIcon, PencilIcon } from '@heroicons/vue/24/outline';
import type { MenuItem, MenuItemVariant, CategoryForm } from '@/types/menu';
import { useMenuStore } from '@/stores/menu';
import IngredientsManager, { type MenuItemIngredients } from './IngredientsManager.vue';
import DropdownMenu from '@/components/ui/DropdownMenu.vue';
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue';
import * as menuService from '@/services/menuService';
import { useToast } from '@/composables/useToast';
import { useI18n } from 'vue-i18n';
import { subscriptionService } from '@/services/subscriptionService';

const props = defineProps<{
  menuItem?: MenuItem;
  loading?: boolean;
  errors?: Record<string, string>;
  isEditing?: boolean;
}>();

const emit = defineEmits<{
  (e: 'submit', formData: Omit<MenuItem, 'id'>): void;
  (e: 'cancel'): void;
  (e: 'delete', menuItemId: string | number): void;
  (e: 'close'): void;
}>();

const menuStore = useMenuStore();
const { showSuccess, showError } = useToast();
const loadingCategories = ref(false);
const showDeleteConfirm = ref(false);
const isDeleting = ref(false);
const isSavingVariant = ref(false);
const { t } = useI18n();

// Check if ingredients module is available
const hasIngredientsModule = ref(false);


// Check subscription features
const checkSubscriptionFeatures = async () => {
  try {
    const usage = await subscriptionService.getUsage();
    if (usage.has_subscription && usage.limits) {
      hasIngredientsModule.value = usage.limits.has_ingredients_module || false;
    }
  } catch (error) {
    console.error('Error checking subscription features:', error);
  }
};

// Initialize categories on component mount
onMounted(() => {
  checkSubscriptionFeatures();
  if (menuStore.categories.length === 0) {
    menuStore.getCategories().catch((err: unknown) => {
      console.error('Failed to load categories:', err);
      showError(t('app.messages.load_categories_failed'));
    });
  }
});

// Define form data type
type FormData = {
  name: string;
  description: string;
  price: number;
  discount_price?: number;
  category_id: number | null;
  is_available: boolean;
  image_url: string;
  ingredients: MenuItemIngredients | null;
  variants: Array<{
    id?: string | number;
    name: string;
    price: number;
    discount_price?: number;
    is_available: boolean;
  }>;
};

// Initialize form data with proper types
const formData = ref<FormData>({
  name: '',
  description: '',
  price: 0,
  discount_price: undefined,
  category_id: null,
  is_available: true,
  image_url: '',
  ingredients: null,
  variants: []
});

// Load initial data if editing
if (props.menuItem) {
  const menuItem = props.menuItem;
  formData.value = {
    name: menuItem.name || '',
    description: menuItem.description || '',
    price: menuItem.price || 0,
    discount_price: menuItem.discount_price,
    category_id: menuItem.category_id || (typeof menuItem.category === 'object' && menuItem.category?.id ? Number(menuItem.category.id) : null),
    is_available: menuItem.is_available ?? true,
    image_url: menuItem.image_url || '',
    ingredients: (menuItem as any).ingredients || null,
    variants: (menuItem.variants || []).map(variant => ({
      id: variant.id,
      name: variant.name,
      price: variant.price,
      discount_price: variant.discount_price,
      is_available: variant.is_available ?? true
    }))
  };
}

const showVariantForm = ref(false);
const editingVariantIndex = ref<number | null>(null);
const variantMenus = ref<Record<string, boolean>>({});
// Define variant form type
type VariantForm = {
  id?: string | number;
  name: string;
  price: number;
  discount_price?: number;
  is_available: boolean;
};

const variantForm = ref<VariantForm>({
  name: '',
  price: 0,
  discount_price: undefined,
  is_available: true
});

const formErrors = ref<Record<string, string>>({});

// Computed property to check if the form is valid
const isFormValid = computed(() => {
  return (
    formData.value.name.trim() !== '' &&
    formData.value.category_id !== null &&
    formData.value.price >= 0
  );
});

// Computed to get category ID for IngredientsManager
const categoryIdForIngredients = computed(() => formData.value.category_id || undefined);

// Load categories when component mounts
onMounted(async () => {
  try {
    // Load categories first
    const categories = await menuStore.getCategories();
    
    // If editing, load the menu item data
    if (props.menuItem?.id) {
      const item = await menuStore.getMenuItem(props.menuItem.id);
      
      // Extract category_id
      let categoryId: number | null = null;
      if (item.category_id) {
        categoryId = Number(item.category_id);
      } else if (typeof item.category === 'object' && item.category && 'id' in item.category) {
        categoryId = Number(item.category.id);
      }
      
      // Update form data with the menu item
      formData.value = {
        name: item.name || '',
        description: item.description || '',
        price: item.price || 0,
        discount_price: item.discount_price,
        category_id: categoryId,
        is_available: item.is_available ?? true,
        image_url: item.image_url || '',
        ingredients: item.ingredients || null,
        variants: (item.variants || []).map(v => ({
          id: v.id,
          name: v.name,
          price: v.price,
          discount_price: v.discount_price,
          is_available: v.is_available ?? true
        }))
      };
    } else if (menuStore.categoriesDetailed.length > 0) {
      // For new items, set the first category ID as default
      const firstCategory = menuStore.categoriesDetailed[0];
      if (firstCategory && firstCategory.id) {
        formData.value.category_id = Number(firstCategory.id);
      }
    }
  } catch (error: unknown) {
    console.error('Error initializing form:', error);
    showError(t('app.messages.init_form_failed'));
  } finally {
    loadingCategories.value = false;
  }
});

async function loadCategories() {
  try {
    loadingCategories.value = true;
    // Force refresh categories
    await menuStore.getCategories();
  } catch (error: unknown) {
    console.error('Error loading categories:', error);
    showError(t('app.messages.load_categories_failed'));
  } finally {
    loadingCategories.value = false;
  }
}

const handleDelete = async () => {
  if (!props.menuItem?.id) return;
  
  try {
    await menuStore.deleteMenuItem(props.menuItem.id);
    emit('delete', props.menuItem.id);
    emit('close');
    showSuccess(t('app.messages.delete_item_success'));
  } catch (error: unknown) {
    console.error('Error deleting menu item:', error);
    showError(t('app.messages.delete_item_failed'));
  } finally {
    showDeleteConfirm.value = false;
  }
};

function handleSubmit() {
  if (!isFormValid.value) {
    showError(t('app.messages.form_fill_required'));
  }

  // Basic validation
  if (!formData.value.name.trim()) {
    formErrors.value.name = t('validation.name_required');
    return;
  }
  
  if (!formData.value.category_id) {
    formErrors.value.category = t('validation.category_required');
    return;
  }
  
  if (formData.value.price < 0) {
    formErrors.value.price = t('validation.price_non_negative');
    return;
  }
  
  // Prepare data for submission
  const submitData = {
    ...formData.value,
    price: Number(formData.value.price),
    discount_price: formData.value.discount_price ? Number(formData.value.discount_price) : undefined,
    category_id: formData.value.category_id,
    is_available: formData.value.is_available,
    image_url: formData.value.image_url,
    variants: formData.value.variants.map(variant => ({
      ...variant,
      price: Number(variant.price),
      discount_price: variant.discount_price ? Number(variant.discount_price) : undefined,
      is_available: variant.is_available
    }))
  };
  
  try {
    emit('submit', submitData);
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
    showError(t('app.messages.submit_failed', { message: errorMessage }));
  }
}

function handleCancel() {
  emit('cancel');
}

const handleSaveVariant = (): void => {
  if (!variantForm.value || !formData.value) return;
  if (!variantForm.value.name || variantForm.value.price === undefined) {
    showError(t('app.messages.variant_required'));
    return;
  }

  const variantData = {
    id: variantForm.value.id,
    name: variantForm.value.name,
    price: Number(variantForm.value.price),
    discount_price: variantForm.value.discount_price ? Number(variantForm.value.discount_price) : undefined,
    is_available: variantForm.value.is_available ?? true
  };

  if (editingVariantIndex.value !== null) {
    // Update existing variant
    formData.value.variants[editingVariantIndex.value] = variantData;
  } else {
    // Add new variant
    formData.value.variants.push(variantData);
  }

  resetVariantForm();
};

const handleRemoveVariant = (index: number): void => {
  if (!formData.value) return;
  formData.value.variants = formData.value.variants.filter((_, i) => i !== index);
};

const handleAddVariant = () => {
  resetVariantForm();
  editingVariantIndex.value = null;
  showVariantForm.value = true;
};

const editVariant = (index: number): void => {
  const variant = formData.value.variants[index];
  variantForm.value = {
    id: variant.id,
    name: variant.name,
    price: typeof variant.price === 'string' ? parseFloat(variant.price) : variant.price,
    discount_price: variant.discount_price,
    is_available: variant.is_available ?? true
  };
  editingVariantIndex.value = index;
  showVariantForm.value = true;
};

const resetVariantForm = (): void => {
  if (!variantForm.value) return;
  
  variantForm.value = {
    name: '',
    price: 0,
    discount_price: undefined,
    is_available: true
  };
  editingVariantIndex.value = null;
  showVariantForm.value = false;
}

// Export the form data and methods for parent components
defineExpose({
  // Form data
  formData,
  // Methods
  handleSaveVariant,
  handleRemoveVariant,
  handleCancel,
  resetVariantForm,
  editVariant
});
</script>

<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <div class="space-y-4">
      <!-- Name -->
      <div>
        <label for="name" class="block text-sm font-medium text-gray-700 dark:text-white">
          {{ t('app.forms.name') }} <span class="text-red-500">*</span>
        </label>
        <input
          id="name"
          v-model="formData.name"
          type="text"
          class="mt-1 dark:bg-gray-900 dark:text-white block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
          :class="{ 'border-red-500': formErrors.name }"
          required
        />
        <p v-if="formErrors.name" class="mt-1 text-sm text-red-600">
          {{ formErrors.name }}
        </p>
      </div>

      <!-- Description -->
      <div>
        <label for="description" class="block text-sm font-medium text-gray-700 dark:text-white">
          {{ t('app.forms.description') }}
        </label>
        <textarea
          id="description"
          v-model="formData.description"
          rows="3"
          class="mt-1 block w-full dark:bg-gray-900 dark:text-white rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
          :class="{ 'border-red-500': formErrors.description }"
        />
        <p v-if="formErrors.description" class="mt-1 text-sm text-red-600">
          {{ formErrors.description }}
        </p>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <!-- Category -->
        <div>
          <div class="flex items-center justify-between dark:text-white">
            <label for="category" class="block text-sm font-medium text-gray-700 dark:text-white">
              {{ t('app.forms.category') }} <span class="text-red-500">*</span>
            </label>

          </div>
          <div class="mt-1 relative">
            <select
              id="category"
              v-model.number="formData.category_id"
              class="block dark:bg-gray-900 dark:text-white w-full rounded-md border border-gray-300 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
              :class="{ 
                'border-red-500': formErrors.category,
                'opacity-50': loadingCategories || menuStore.loading
              }"
              :disabled="loadingCategories || menuStore.loading"
              required
            >
              <option v-if="loadingCategories || menuStore.loading" :value="null" disabled>{{ t('app.forms.loading_categories') }}</option>
              <option v-else-if="!menuStore.categoriesDetailed || menuStore.categoriesDetailed.length === 0" :value="null" disabled>{{ t('app.forms.no_categories') }}</option>
              <option 
                v-else
                v-for="category in menuStore.categoriesDetailed" 
                :key="category.id" 
                :value="Number(category.id)"
              >
                {{ category.name }}
              </option>
            </select>
          </div>
          <p v-if="formErrors.category" class="mt-1 text-sm text-red-600">
            {{ formErrors.category }}
          </p>
        </div>

        <!-- Price -->
        <div>
          <label for="price" class="block text-sm font-medium text-gray-700 dark:text-white">
            {{ t('app.forms.price_base') }} <span class="text-red-500">*</span>
          </label>
          <div class="relative mt-1 rounded-md shadow-sm">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
              <span class="text-gray-500 sm:text-sm">{{ t('app.forms.price_symbol') }}</span>
            </div>
            <input
              id="price"
              v-model.number="formData.price"
              type="number"
              step="0.01"
              min="0"
              class="block w-full dark:bg-gray-900 dark:text-white rounded-md border border-gray-300 pl-7 pr-12 py-2 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
              :class="{ 'border-red-500': formErrors.price }"
              :placeholder="t('app.forms.placeholder_price')"
              required
            />
          </div>
          <p v-if="formErrors.price" class="mt-1 text-sm text-red-600">
            {{ formErrors.price }}
          </p>
        </div>
      </div>

      <!-- Discount Price (Promotional Price) -->
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label for="discount_price" class="block text-sm font-medium text-gray-700 dark:text-white">
            {{ t('app.forms.discount_price') }}
          </label>
          <div class="relative mt-1 rounded-md shadow-sm">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
              <span class="text-gray-500 sm:text-sm">{{ t('app.forms.price_symbol') }}</span>
            </div>
            <input
              id="discount_price"
              v-model.number="formData.discount_price"
              type="number"
              step="0.01"
              min="0"
              class="block w-full dark:bg-gray-900 dark:text-white rounded-md border border-gray-300 pl-7 pr-12 py-2 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
              :placeholder="t('app.forms.discount_placeholder')"
            />
          </div>
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            {{ t('app.forms.discount_price_help') }}
          </p>
        </div>
        <div v-if="formData.discount_price && formData.discount_price > 0" class="flex items-center">
          <div class="rounded-md bg-green-50 dark:bg-green-900/20 p-3">
            <div class="flex">
              <div class="ml-3">
                <p class="text-sm font-medium text-green-800 dark:text-green-200">
                  {{ t('app.forms.discount_active') }}
                </p>
                <p class="mt-1 text-sm text-green-700 dark:text-green-300">
                  {{ t('app.forms.customers_save', { amount: `$${(formData.price - formData.discount_price).toFixed(2)}` }) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Image URL -->
      <div>
        <label for="image_url" class="block text-sm font-medium text-gray-700 dark:text-white">
          {{ t('app.forms.image_url') }}
        </label>
        <input
          id="image_url"
          v-model="formData.image_url"
          type="url"
          class="mt-1 block w-full dark:bg-gray-900 dark:text-white rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
          :class="{ 'border-red-500': formErrors.image_url }"
          placeholder="https://example.com/image.jpg"
        />
        <p v-if="formErrors.image_url" class="mt-1 text-sm text-red-600">
          {{ formErrors.image_url }}
        </p>
      </div>

      <!-- Availability -->
      <div class="flex items-center">
        <input
          id="is_available"
          v-model="formData.is_available"
          type="checkbox"
          class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
        />
        <label for="is_available" class="ml-2 block text-sm text-gray-700 dark:text-white ">
          {{ t('app.forms.available_for_ordering') }}
        </label>
      </div>

      <!-- Ingredients Section (only if module is available) -->
      <div v-if="hasIngredientsModule" class="border-t border-gray-200 dark:border-gray-700 pt-6 mt-6">
        <IngredientsManager 
          v-model="formData.ingredients"
          :category-id="categoryIdForIngredients"
          :current-item-id="props.menuItem?.id"
        />
      </div>
      
      <!-- Ingredients Module Locked Message -->
      <div v-else class="border-t border-gray-200 dark:border-gray-700 pt-6 mt-6">
        <div class="bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <div class="ml-3 flex-1">
              <h3 class="text-sm font-medium text-gray-900 dark:text-white">
                {{ t('app.subscription.ingredients_module') }}
              </h3>
              <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">
                {{ t('app.subscription.module_locked_message') }}
              </p>
              <router-link 
                to="/subscription"
                class="mt-3 inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400 dark:hover:text-indigo-300"
              >
                {{ t('app.subscription.upgrade') }}
                <svg class="ml-1 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Variants Section -->
      <div class="border-t border-gray-200 dark:border-gray-700 pt-4 mt-6">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-medium text-gray-700 dark:text-gray-100">{{ t('app.forms.variants') }}</h3>
          <button @click="handleAddVariant" type="button" class="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            <PlusIcon class="-ml-0.5 mr-2 h-4 w-4" />
            {{ t('app.forms.add_variant') }}
          </button>
        </div>

        <!-- Variants List -->
        <div v-if="formData.variants && formData.variants.length > 0" class="mt-4 space-y-2">
          <div 
            v-for="(variant, index) in formData.variants" 
            :key="index"
            class="flex items-center justify-between rounded-md border border-gray-200 dark:border-gray-700 p-3"
          >
            <div>
              <p class="text-sm font-medium text-gray-900 dark:text-white">{{ variant.name }}</p>
              <div class="flex items-center gap-2">
                <p 
                  v-if="variant.discount_price && variant.discount_price > 0"
                  class="text-sm text-gray-500 dark:text-gray-400 line-through"
                >
                  ${{ typeof variant.price === 'number' ? variant.price.toFixed(2) : variant.price }}
                </p>
                <p 
                  class="text-sm font-medium"
                  :class="variant.discount_price && variant.discount_price > 0 ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'"
                >
                  ${{ variant.discount_price && variant.discount_price > 0 
                    ? (typeof variant.discount_price === 'number' ? variant.discount_price.toFixed(2) : variant.discount_price)
                    : (typeof variant.price === 'number' ? variant.price.toFixed(2) : variant.price) 
                  }}
                </p>
                <span 
                  v-if="variant.discount_price && variant.discount_price > 0"
                  class="inline-flex items-center rounded-full bg-green-100 dark:bg-green-900/30 px-2 py-0.5 text-xs font-medium text-green-800 dark:text-green-200"
                >
                  {{ t('app.forms.sale_badge') }}
                </span>
              </div>
              <span 
                v-if="!variant.is_available"
                class="inline-flex items-center rounded-full bg-red-100 dark:bg-red-900/30 px-2 py-0.5 text-xs font-medium text-red-800 dark:text-red-200"
              >
                {{ t('app.status.unavailable') }}
              </span>
            </div>
            <div class="flex-shrink-0">
              <DropdownMenu v-model="variantMenus[`variant-${index}`]" width="sm">
                <DropdownMenuItem 
                  :icon="PencilIcon" 
                  variant="primary"
                  @click="editVariant(index)"
                >
                  {{ t('app.actions.edit') }}
                </DropdownMenuItem>
                
                <DropdownMenuItem 
                  :icon="TrashIcon" 
                  variant="danger"
                  @click="handleRemoveVariant(index)"
                >
                  {{ t('app.actions.delete') }}
                </DropdownMenuItem>
              </DropdownMenu>
            </div>
          </div>
        </div>
        <p v-else class="mt-2 text-sm text-gray-500 dark:text-gray-400">
          {{ t('app.forms.no_variants') }}
        </p>

        <!-- Inline Variant Form (Mobile & Desktop) -->
        <div v-if="showVariantForm" class="mt-4 rounded-lg border border-indigo-200 dark:border-indigo-800 bg-indigo-50 dark:bg-indigo-900/20 p-4">
          <div class="flex items-center justify-between mb-4">
            <h4 class="text-sm font-medium text-gray-900 dark:text-gray-100">
              {{ editingVariantIndex !== null ? t('app.forms.variant.edit') : t('app.forms.variant.add') }}
            </h4>
            <button
              type="button"
              class="rounded-md text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 focus:outline-none"
              @click="resetVariantForm"
            >
              <XMarkIcon class="h-5 w-5" aria-hidden="true" />
            </button>
          </div>

          <div class="space-y-4">
            <!-- Variant name -->
            <div>
              <label
                for="variant-name-inline"
                class="block text-sm font-medium text-gray-700 dark:text-gray-200"
              >
                {{ t('app.forms.variant.name') }}
              </label>
              <input
                type="text"
                id="variant-name-inline"
                v-model="variantForm.name"
                class="mt-1 p-2 block w-full rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-800 dark:text-gray-100"
                placeholder="e.g., Small, Large, Iced"
              />
            </div>

            <!-- Variant price -->
            <div>
              <label
                for="variant-price-inline"
                class="block text-sm font-medium text-gray-700 dark:text-gray-200"
              >
                {{ t('app.forms.variant.price') }}
              </label>
              <div class="mt-1 relative rounded-md shadow-sm">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span class="text-gray-500 sm:text-sm">
                    {{ t('app.forms.price_symbol') }}
                  </span>
                </div>
                <input
                  type="number"
                  id="variant-price-inline"
                  v-model.number="variantForm.price"
                  step="0.01"
                  min="0"
                  class="block w-full pl-7 pr-12 py-2 rounded-md border-gray-300 dark:border-gray-600 focus:border-indigo-500 focus:ring-indigo-500 dark:bg-gray-800 dark:text-gray-100 sm:text-sm"
                  :placeholder="t('app.forms.placeholder_price')"
                />
              </div>
            </div>

            <!-- Variant discount price -->
            <div>
              <label
                for="variant-discount-price-inline"
                class="block text-sm font-medium text-gray-700 dark:text-gray-200"
              >
                {{ t('app.forms.variant.discount_price') }} ({{ t('app.forms.discount_placeholder').split(' ')[0] }})
              </label>
              <div class="mt-1 relative rounded-md shadow-sm">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span class="text-gray-500 sm:text-sm">
                    {{ t('app.forms.price_symbol') }}
                  </span>
                </div>
                <input
                  type="number"
                  id="variant-discount-price-inline"
                  v-model.number="variantForm.discount_price"
                  step="0.01"
                  min="0"
                  class="block w-full pl-7 pr-12 py-2 rounded-md border-gray-300 dark:border-gray-600 focus:border-indigo-500 focus:ring-indigo-500 dark:bg-gray-800 dark:text-gray-100 sm:text-sm"
                  :placeholder="t('app.forms.discount_placeholder')"
                />
              </div>
              <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                {{ t('app.forms.discount_price_help') }}
              </p>
            </div>

            <!-- Available toggle -->
            <div class="flex items-center">
              <input
                id="variant-available-inline"
                type="checkbox"
                v-model="variantForm.is_available"
                class="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-indigo-600 focus:ring-indigo-500"
              />
              <label
                for="variant-available-inline"
                class="ml-2 block text-sm text-gray-700 dark:text-gray-200"
              >
                {{ t('app.forms.variant.available') }}
              </label>
            </div>

            <!-- Action buttons -->
            <div class="flex gap-3 pt-2">
              <button
                type="button"
                class="flex-1 inline-flex justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                @click="handleSaveVariant"
              >
                {{ t('app.actions.save') }}
              </button>
              <button
                type="button"
                class="flex-1 inline-flex justify-center rounded-md bg-white dark:bg-gray-800 px-3 py-2 text-sm font-semibold text-gray-900 dark:text-gray-100 shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
                @click="resetVariantForm"
              >
                {{ t('app.actions.cancel') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Form Actions -->
    <div class="flex justify-between items-center pt-4">
      <div v-if="props.menuItem?.id">
        <button
          type="button"
          @click="showDeleteConfirm = true"
          class="inline-flex items-center px-4 py-2 rounded-md border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          :disabled="isDeleting"
        >
          <TrashIcon v-if="!isDeleting" class="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
          <ArrowPathIcon v-else class="animate-spin -ml-1 mr-2 h-5 w-5" aria-hidden="true" />
          {{ isDeleting ? 'Deleting...' : 'Delete Item' }}
        </button>
      </div>
      <div class="flex space-x-3">
        <button
          type="button"
          @click="handleCancel"
          class="inline-flex items-center px-4 py-2 rounded-md border border-gray-300 shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          :disabled="loading"
        >
          {{ t('app.actions.cancel') }}
        </button>
        <button
          type="submit"
          class="inline-flex justify-center items-center px-4 py-2 rounded-md border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          :disabled="!isFormValid || loading"
        >
          <ArrowPathIcon v-if="loading" class="animate-spin -ml-1 mr-2 h-4 w-4" />
          {{ isEditing ? t('app.forms.update_item') : t('app.forms.create_item') }}
        </button>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <TransitionRoot as="template" :show="showDeleteConfirm">
      <Dialog as="div" class="relative z-50" @close="showDeleteConfirm = false">
        <TransitionChild
          as="template"
          enter="ease-out duration-300"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="ease-in duration-200"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-gray-500 dark:bg-gray-900 bg-opacity-75 transition-opacity" />
        </TransitionChild>

        <div class="fixed inset-0 z-10 overflow-y-auto">
          <div class="flex min-h-full items-end justify-center p-0 sm:p-4 text-center sm:items-center">
            <TransitionChild
              as="template"
              enter="ease-out duration-300"
              enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enter-to="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leave-from="opacity-100 translate-y-0 sm:scale-100"
              leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <DialogPanel class="relative transform overflow-hidden rounded-none sm:rounded-lg bg-white dark:bg-gray-900 px-4 pb-4 pt-5 text-left shadow-xl transition-all w-full min-h-screen sm:min-h-0 sm:my-8 sm:max-w-lg sm:p-6 border-0 sm:border border-gray-200 dark:border-gray-800">
                <div class="sm:flex sm:items-start">
                  <div class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                    <ExclamationTriangleIcon class="h-6 w-6 text-red-600" aria-hidden="true" />
                  </div>
                  <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left">
                    <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">
                      {{ t('app.messages.delete_item_confirm_title') }}
                    </DialogTitle>
                    <div class="mt-2">
                      <p class="text-sm text-gray-500">
                        {{ t('app.messages.delete_item_confirm_text') }}
                      </p>
                    </div>
                  </div>
                </div>
                <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                  <button
                    type="button"
                    class="inline-flex w-full justify-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 sm:ml-3 sm:w-auto"
                    @click="handleDelete"
                    :disabled="isDeleting"
                  >
                    {{ isDeleting ? t('app.status.loading') : t('app.actions.delete') }}
                  </button>
                  <button
                    type="button"
                    class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
                    @click="showDeleteConfirm = false"
                    :disabled="isDeleting"
                  >
                    {{ t('app.actions.cancel') }}
                  </button>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </form>


</template>
