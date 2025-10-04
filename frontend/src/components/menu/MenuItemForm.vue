<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue';
import { XMarkIcon, PlusIcon, ArrowPathIcon, TrashIcon, ExclamationTriangleIcon, PencilIcon } from '@heroicons/vue/24/outline';
import type { MenuItem, MenuItemVariant, CategoryForm } from '@/types/menu';
import { useMenuStore } from '@/stores/menu';
import * as menuService from '@/services/menuService';
import { useToast } from '@/composables/useToast';
import { useI18n } from 'vue-i18n';

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


// Helper function to normalize category input
const normalizeCategory = (category: string | CategoryForm | undefined): string => {
  if (!category) return '';
  if (typeof category === 'string') return category;
  if (typeof category === 'object' && 'name' in category) return category.name;
  return '';
};

// Initialize categories on component mount
onMounted(() => {
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
  category: string | CategoryForm;
  is_available: boolean;
  image_url: string;
  variants: Array<{
    id?: string | number;
    name: string;
    price: number;
    is_available: boolean;
  }>;
};

// Initialize form data with proper types
const formData = ref<FormData>({
  name: '',
  description: '',
  price: 0,
  category: '',
  is_available: true,
  image_url: '',
  variants: []
});

// Load initial data if editing
if (props.menuItem) {
  const menuItem = props.menuItem;
  formData.value = {
    name: menuItem.name || '',
    description: menuItem.description || '',
    price: menuItem.price || 0,
    category: menuItem.category || '',
    is_available: menuItem.is_available ?? true,
    image_url: menuItem.image_url || '',
    variants: (menuItem.variants || []).map(variant => ({
      id: variant.id,
      name: variant.name,
      price: variant.price,
      is_available: variant.is_available ?? true
    }))
  };
}

const showVariantForm = ref(false);
const editingVariantIndex = ref<number | null>(null);
// Define variant form type
type VariantForm = {
  id?: string | number;
  name: string;
  price: number;
  is_available: boolean;
};

const variantForm = ref<VariantForm>({
  name: '',
  price: 0,
  is_available: true
});

const formErrors = ref<Record<string, string>>({});

// Computed property to check if the form is valid
const isFormValid = computed(() => {
  return (
    formData.value.name.trim() !== '' &&
    formData.value.category &&
    formData.value.price >= 0
  );
});

// Load categories when component mounts
onMounted(async () => {
  console.log('Component mounted, loading categories...');
  try {
    // Load categories first
    const categories = await menuStore.getCategories();
    console.log('Categories loaded:', categories);
    
    // If editing, load the menu item data
    if (props.menuItem?.id) {
      console.log('Loading menu item data for ID:', props.menuItem.id);
      const item = await menuStore.getMenuItem(props.menuItem.id);
      const normalizedCategory = normalizeCategory(item.category);
      
      // Update form data with the menu item
      formData.value = {
        ...item,
        category: normalizedCategory || '',
        isAvailable: item.isAvailable ?? item.is_available ?? true,
        imageUrl: item.imageUrl ?? item.image_url ?? '',
        variants: (item.variants || []).map(v => ({
          ...v,
          isAvailable: v.isAvailable ?? v.is_available ?? true
        }))
      };
      
      // Ensure the current category is in the categories list
      console.log('Normalized category:', normalizedCategory);
      console.log('Current categories:', menuStore.categories);
      
      if (normalizedCategory && !menuStore.categories.includes(normalizedCategory)) {
        console.log('Adding category to list:', normalizedCategory);
        menuStore.categories = [normalizedCategory, ...menuStore.categories];
      }
    } else if (menuStore.categories.length > 0) {
      // For new items, set the first category as default
      formData.value.category = menuStore.categories[0];
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
    const categories = await menuStore.getCategories();
    console.log('Loaded categories:', categories);
    
    // If we're editing and the current category isn't in the list, add it
    if (props.menuItem?.id && formData.value.category && !categories.includes(formData.value.category)) {
      console.log('Adding missing category to store:', formData.value.category);
      menuStore.categories = [formData.value.category, ...categories];
    }
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
  
  if (!formData.value.category) {
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
    category: formData.value.category,
    is_available: formData.value.is_available,
    image_url: formData.value.image_url,
    variants: formData.value.variants.map(variant => ({
      ...variant,
      price: Number(variant.price),
      is_available: variant.is_available
    }))
  };
  
  console.log('Submitting menu item:', submitData);
  
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
  console.log('variantForm.value:', variantForm.value)
  if (!variantForm.value || !formData.value) return;
  if (!variantForm.value.name || variantForm.value.price === undefined) {
    showError(t('app.messages.variant_required'));
    return;
  }

  const variantData = {
    id: variantForm.value.id,
    name: variantForm.value.name,
    price: Number(variantForm.value.price),
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
              v-model="formData.category"
              class="block dark:bg-gray-900 dark:text-white w-full rounded-md border border-gray-300 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
              :class="{ 
                'border-red-500': formErrors.category,
                'opacity-50': loadingCategories || menuStore.loading
              }"
              :disabled="loadingCategories || menuStore.loading"
              required
            >
              <option v-if="loadingCategories || menuStore.loading" value="" disabled>{{ t('app.forms.loading_categories') }}</option>
              <option v-else-if="!menuStore.categories || menuStore.categories.length === 0" value="" disabled>{{ t('app.forms.no_categories') }}</option>
              <option 
                v-else
                v-for="category in menuStore.categories" 
                :key="category" 
                :value="category"
                :selected="formData.category === category"
              >
                {{ category }}
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

      <!-- Variants Section -->
      <div class="border-t border-gray-200 pt-4">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-medium text-gray-700">{{ t('app.forms.variants') }}</h3>
          <button @click="handleAddVariant" type="button" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            <PlusIcon class="-ml-0.5 mr-2 h-4 w-4" />
            {{ t('app.forms.add_variant') }}
          </button>
        </div>

        <!-- Variants List -->
        <div v-if="formData.variants && formData.variants.length > 0" class="mt-4 space-y-2">
          <div 
            v-for="(variant, index) in formData.variants" 
            :key="index"
            class="flex items-center justify-between rounded-md border border-gray-200 p-3"
          >
            <div>
              <p class="text-sm font-medium text-gray-900">{{ variant.name }}</p>
              <p class="text-sm text-gray-500">${{ typeof variant.price === 'number' ? variant.price.toFixed(2) : variant.price }}</p>
              <span 
                v-if="!variant.is_available"
                class="inline-flex items-center rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800"
              >
                {{ t('app.status.unavailable') }}
              </span>
            </div>
            <div class="flex space-x-2">
              <button
                type="button"
                class="text-indigo-600 hover:text-indigo-900"
                @click="editVariant(index)"
              >
                <span class="sr-only">{{ t('app.forms.edit') }}</span>
                <PencilIcon class="h-4 w-4" />
              </button>
              <button
                type="button"
                class="text-red-600 hover:text-red-900"
                @click="handleRemoveVariant(index)"
              >
                <XMarkIcon class="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
        <p v-else class="mt-2 text-sm text-gray-500">
          {{ t('app.forms.no_variants') }}
        </p>
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
          <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <TransitionChild
              as="template"
              enter="ease-out duration-300"
              enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enter-to="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leave-from="opacity-100 translate-y-0 sm:scale-100"
              leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white dark:bg-gray-900 px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
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

<!-- Variant Form Modal -->
<TransitionRoot as="template" :show="showVariantForm">
  <Dialog as="div" class="relative z-10" @close="resetVariantForm">
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
      <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
        <TransitionChild
          as="template"
          enter="ease-out duration-300"
          enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          enter-to="opacity-100 translate-y-0 sm:scale-100"
          leave="ease-in duration-200"
          leave-from="opacity-100 translate-y-0 sm:scale-100"
          leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
        >
          <DialogPanel
            class="relative transform overflow-hidden rounded-lg bg-white dark:bg-gray-900 px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6"
          >
            <!-- Close button -->
            <div class="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
              <button
                type="button"
                class="rounded-md bg-white dark:bg-gray-900 text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                @click="resetVariantForm"
              >
                <span class="sr-only">Close</span>
                <XMarkIcon class="h-6 w-6" aria-hidden="true" />
              </button>
            </div>

            <!-- Content -->
            <div class="sm:flex sm:items-start">
              <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                <DialogTitle
                  as="h3"
                  class="text-lg font-medium leading-6 text-gray-900 dark:text-gray-100"
                >
                  {{ editingVariantIndex !== null ? t('app.forms.variant.edit') : t('app.forms.variant.add') }}
                </DialogTitle>

                <div class="mt-5">
                  <div class="space-y-4">
                    <!-- Variant name -->
                    <div>
                      <label
                        for="variant-name"
                        class="block text-sm font-medium text-gray-700 dark:text-gray-100"
                      >
                        {{ t('app.forms.variant.name') }}
                      </label>
                      <input
                        type="text"
                        id="variant-name"
                        v-model="variantForm.name"
                        class="mt-1 block w-full rounded-md border-gray-300 dark:border-gray-700 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-800 dark:text-gray-100"
                        placeholder="e.g., Small, Large, Iced"
                      />
                    </div>

                    <!-- Variant price -->
                    <div>
                      <label
                        for="variant-price"
                        class="block text-sm font-medium text-gray-700 dark:text-gray-100"
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
                          id="variant-price"
                          v-model.number="variantForm.price"
                          step="0.01"
                          min="0"
                          class="block w-full pl-7 pr-12 rounded-md border-gray-300 dark:border-gray-700 focus:border-indigo-500 focus:ring-indigo-500 dark:bg-gray-800 dark:text-gray-100 sm:text-sm"
                          :placeholder="t('app.forms.placeholder_price')"
                        />
                      </div>
                    </div>

                    <!-- Available toggle -->
                    <div class="flex items-center">
                      <input
                        id="variant-available"
                        type="checkbox"
                        v-model="variantForm.is_available"
                        class="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-indigo-600 focus:ring-indigo-500"
                      />
                      <label
                        for="variant-available"
                        class="ml-2 block text-sm text-gray-700 dark:text-gray-100"
                      >
                        {{ t('app.forms.variant.available') }}
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Footer buttons -->
            <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
              <button
                type="button"
                class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 sm:ml-3 sm:w-auto"
                @click="handleSaveVariant"
              >
                {{ t('app.actions.save') }}
              </button>
              <button
                type="button"
                class="mt-3 inline-flex w-full justify-center rounded-md bg-white dark:bg-gray-800 px-3 py-2 text-sm font-semibold text-gray-900 dark:text-gray-100 shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 sm:mt-0 sm:w-auto"
                @click="resetVariantForm"
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

</template>
