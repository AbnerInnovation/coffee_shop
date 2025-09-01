<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from '@headlessui/vue';
import { XMarkIcon, PlusIcon, ArrowPathIcon, TrashIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline';
import type { MenuItem, MenuItemVariant, CategoryForm } from '@/types/menu';
import { useMenuStore } from '@/stores/menu';

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
const loadingCategories = ref(false);
const showDeleteConfirm = ref(false);
const isDeleting = ref(false);

// Simple toast implementation
const showError = (message: string) => {
  // You can replace this with a proper toast implementation
  console.error(message);
  alert(message);
};

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
    menuStore.getCategories().catch(err => {
      console.error('Failed to load categories:', err);
    });
  }
});

// Define form data type
type FormData = {
  name: string;
  description: string;
  price: number;
  category: string | CategoryForm;
  isAvailable: boolean;
  imageUrl: string;
  variants: Array<{
    id?: string | number;
    name: string;
    price: number;
    isAvailable: boolean;
    is_available?: boolean;
  }>;
};

// Initialize form data with proper types
const formData = ref<FormData>({
  name: '',
  description: '',
  price: 0,
  category: '',
  isAvailable: true,
  imageUrl: '',
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
    isAvailable: menuItem.isAvailable ?? menuItem.is_available ?? true,
    imageUrl: menuItem.imageUrl || menuItem.image_url || '',
    variants: (menuItem.variants || []).map(variant => ({
      id: variant.id,
      name: variant.name,
      price: variant.price,
      isAvailable: variant.isAvailable ?? variant.is_available ?? true,
      is_available: variant.is_available ?? variant.isAvailable ?? true
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
  isAvailable: boolean;
};

const variantForm = ref<VariantForm>({
  name: '',
  price: 0,
  isAvailable: true
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
  } catch (error) {
    console.error('Error initializing form:', error);
    showError('Failed to initialize form data');
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
  } catch (error) {
    console.error('Error loading categories:', error);
    showError('Failed to load categories. Please try again.');
  } finally {
    loadingCategories.value = false;
  }
}

// Handle delete confirmation
const handleDelete = async () => {
  if (!props.menuItem?.id) {
    console.error('No menu item ID found for deletion');
    return;
  }
  
  console.log('Initiating delete for menu item ID:', props.menuItem.id);
  isDeleting.value = true;
  
  try {
    console.log('Calling menuStore.deleteMenuItem...');
    await menuStore.deleteMenuItem(props.menuItem.id);
    console.log('Menu item deleted successfully, emitting events...');
    
    // Emit events to notify parent components
    emit('delete', props.menuItem.id);
    emit('close');
    
    // Show success message
    showError('Menu item deleted successfully');
    console.log('Delete flow completed successfully');
  } catch (error) {
    console.error('Error in handleDelete:', {
      error,
      response: error.response,
      message: error.message,
      status: error.response?.status,
      data: error.response?.data
    });
    showError('Failed to delete menu item. Please try again.');
  } finally {
    isDeleting.value = false;
    showDeleteConfirm.value = false;
  }
};

function handleSubmit() {
  if (!isFormValid.value) {
    showError('Please fill in all required fields');
    return;
  }
  
  // Convert price to number if it's a string
  const price = typeof formData.value.price === 'string' 
    ? parseFloat(formData.value.price) 
    : formData.value.price;
  const variants = formData.value.variants?.map(variant => ({
    ...variant,
    price: typeof variant.price === 'string' 
      ? parseFloat(variant.price) 
      : variant.price
  }));
  
  // Prepare the submit data with proper typing
  const submitData: Omit<MenuItem, 'id'> = {
    name: formData.value.name,
    description: formData.value.description || '',
    category: typeof formData.value.category === 'string' 
      ? formData.value.category 
      : formData.value.category?.name || '',
    price,
    isAvailable: formData.value.isAvailable,
    is_available: formData.value.isAvailable,
    image_url: formData.value.imageUrl,
    imageUrl: formData.value.imageUrl,
    variants: variants.map(({ isAvailable, ...rest }) => ({
      ...rest,
      is_available: isAvailable,
      isAvailable
    }))
  };
  
  console.log('Submitting menu item:', submitData);
  
  emit('submit', submitData);
}

function handleCancel() {
  emit('cancel');
}

// Handle saving a variant
function handleSaveVariant() {
  if (!variantForm.value.name || variantForm.value.price === undefined) {
    showError('Variant name and price are required');
    return;
  }

  const variantData = {
    id: variantForm.value.id,
    name: variantForm.value.name,
    price: Number(variantForm.value.price),
    isAvailable: variantForm.value.isAvailable ?? true,
    is_available: variantForm.value.isAvailable ?? true
  };

  if (editingVariantIndex.value !== null) {
    formData.value.variants[editingVariantIndex.value] = variantData;
  } else {
    formData.value.variants.push(variantData);
  }

  resetVariantForm();
}

// Handle removing a variant
function handleRemoveVariant(index: number) {
  formData.value.variants.splice(index, 1);
}

// Handle adding a new variant
function handleAddVariant() {
  formData.value.variants.push({
    name: '',
    price: 0,
    isAvailable: true,
    is_available: true
  });
  editingVariantIndex.value = formData.value.variants.length - 1;
  showVariantForm.value = true;
}

function editVariant(index: number) {
  const variant = formData.value.variants?.[index];
  if (!variant) return;
  
  variantForm.value = { ...variant };
  editingVariantIndex.value = index;
  showVariantForm.value = true;
}

function resetVariantForm() {
  variantForm.value = {
    name: '',
    price: 0,
    isAvailable: true
  };
  editingVariantIndex.value = null;
  showVariantForm.value = false;
}

// Export the form data type for parent components
defineExpose({
  formData: formData
});
</script>

<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <div class="space-y-4">
      <!-- Name -->
      <div>
        <label for="name" class="block text-sm font-medium text-gray-700">
          Name <span class="text-red-500">*</span>
        </label>
        <input
          id="name"
          v-model="formData.name"
          type="text"
          class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
          :class="{ 'border-red-500': formErrors.name }"
          required
        />
        <p v-if="formErrors.name" class="mt-1 text-sm text-red-600">
          {{ formErrors.name }}
        </p>
      </div>

      <!-- Description -->
      <div>
        <label for="description" class="block text-sm font-medium text-gray-700">
          Description
        </label>
        <textarea
          id="description"
          v-model="formData.description"
          rows="3"
          class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
          :class="{ 'border-red-500': formErrors.description }"
        />
        <p v-if="formErrors.description" class="mt-1 text-sm text-red-600">
          {{ formErrors.description }}
        </p>
      </div>

      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <!-- Category -->
        <div>
          <div class="flex items-center justify-between">
            <label for="category" class="block text-sm font-medium text-gray-700">
              Category <span class="text-red-500">*</span>
            </label>
            <button 
              type="button"
              @click="loadCategories"
              class="text-xs text-indigo-600 hover:text-indigo-800"
              :disabled="loadingCategories"
            >
              {{ loadingCategories ? 'Refreshing...' : 'Refresh Categories' }}
            </button>
          </div>
          <div class="mt-1 relative">
            <select
              id="category"
              v-model="formData.category"
              class="block w-full rounded-md border border-gray-300 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
              :class="{ 
                'border-red-500': formErrors.category,
                'opacity-50': loadingCategories || menuStore.loading
              }"
              :disabled="loadingCategories || menuStore.loading"
              required
            >
              <option v-if="loadingCategories || menuStore.loading" value="" disabled>Loading categories...</option>
              <option v-else-if="!menuStore.categories || menuStore.categories.length === 0" value="" disabled>No categories available</option>
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
          <button 
            type="button"
            @click="menuStore.getCategories()"
            class="mt-2 text-xs text-indigo-600 hover:text-indigo-500 flex items-center"
            :disabled="menuStore.loading"
          >
            <ArrowPathIcon class="h-4 w-4 mr-1" :class="{ 'animate-spin': menuStore.loading }" />
            {{ menuStore.loading ? 'Loading...' : 'Refresh categories' }}
          </button>
          <p v-if="formErrors.category" class="mt-1 text-sm text-red-600">
            {{ formErrors.category }}
          </p>
        </div>

        <!-- Price -->
        <div>
          <label for="price" class="block text-sm font-medium text-gray-700">
            Base Price <span class="text-red-500">*</span>
          </label>
          <div class="relative mt-1 rounded-md shadow-sm">
            <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
              <span class="text-gray-500 sm:text-sm">$</span>
            </div>
            <input
              id="price"
              v-model.number="formData.price"
              type="number"
              step="0.01"
              min="0"
              class="block w-full rounded-md border border-gray-300 pl-7 pr-12 py-2 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
              :class="{ 'border-red-500': formErrors.price }"
              placeholder="0.00"
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
        <label for="imageUrl" class="block text-sm font-medium text-gray-700">
          Image URL
        </label>
        <input
          id="imageUrl"
          v-model="formData.imageUrl"
          type="url"
          class="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
          :class="{ 'border-red-500': formErrors.imageUrl }"
          placeholder="https://example.com/image.jpg"
        />
        <p v-if="formErrors.imageUrl" class="mt-1 text-sm text-red-600">
          {{ formErrors.imageUrl }}
        </p>
      </div>

      <!-- Availability -->
      <div class="flex items-center">
        <input
          id="isAvailable"
          v-model="formData.isAvailable"
          type="checkbox"
          class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
        />
        <label for="isAvailable" class="ml-2 block text-sm text-gray-700">
          Available for ordering
        </label>
      </div>

      <!-- Variants Section -->
      <div class="border-t border-gray-200 pt-4">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-medium text-gray-700">Variants</h3>
          <button @click="handleSaveVariant" type="button" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
          >
            <PlusIcon class="-ml-0.5 mr-2 h-4 w-4" />
            Add Variant
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
                v-if="!variant.isAvailable"
                class="inline-flex items-center rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800"
              >
                Unavailable
              </span>
            </div>
            <div class="flex space-x-2">
              <button
                type="button"
                class="text-indigo-600 hover:text-indigo-900"
                @click="editVariant(index)"
              >
                <span class="sr-only">Edit</span>
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
          No variants added. Add variants like sizes or flavors.
        </p>
      </div>
    </div>

    <!-- Form Actions -->
    <div class="flex justify-between items-center pt-4">
      <div v-if="props.menuItem?.id">
        <button
          type="button"
          @click="showDeleteConfirm = true"
          class="inline-flex items-center rounded-md border border-transparent bg-red-100 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50"
          :disabled="isSubmitting"
        >
          <TrashIcon class="h-4 w-4 mr-2" />
          Delete Item
        </button>
      </div>
      <div class="flex space-x-3">
        <button
          type="button"
          class="rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
          @click="handleCancel"
          :disabled="isSubmitting"
        >
          Cancel
        </button>
        <button
          type="submit"
          :disabled="!isFormValid || isSubmitting"
          class="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50"
        >
          {{ isSubmitting ? 'Saving...' : 'Save' }}
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
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
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
              <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                <div class="sm:flex sm:items-start">
                  <div class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                    <ExclamationTriangleIcon class="h-6 w-6 text-red-600" aria-hidden="true" />
                  </div>
                  <div class="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left">
                    <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">
                      Delete menu item
                    </DialogTitle>
                    <div class="mt-2">
                      <p class="text-sm text-gray-500">
                        Are you sure you want to delete this menu item? This action cannot be undone.
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
                    {{ isDeleting ? 'Deleting...' : 'Delete' }}
                  </button>
                  <button
                    type="button"
                    class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
                    @click="showDeleteConfirm = false"
                    :disabled="isDeleting"
                  >
                    Cancel
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
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
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
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div class="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
                <button
                  type="button"
                  class="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                  @click="resetVariantForm"
                >
                  <span class="sr-only">Close</span>
                  <XMarkIcon class="h-6 w-6" aria-hidden="true" />
                </button>
              </div>
              <div class="sm:flex sm:items-start">
                <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
                  <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                    {{ editingVariantIndex !== null ? 'Edit Variant' : 'Add Variant' }}
                  </DialogTitle>
                  <div class="mt-5">
                    <div class="space-y-4">
                      <div>
                        <label for="variant-name" class="block text-sm font-medium text-gray-700">Name</label>
                        <input
                          type="text"
                          id="variant-name"
                          v-model="variantForm.name"
                          class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          placeholder="e.g., Small, Large, Iced"
                        />
                      </div>
                      <div>
                        <label for="variant-price" class="block text-sm font-medium text-gray-700">Price</label>
                        <div class="mt-1 relative rounded-md shadow-sm">
                          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <span class="text-gray-500 sm:text-sm">$</span>
                          </div>
                          <input
                            type="number"
                            id="variant-price"
                            v-model.number="variantForm.price"
                            step="0.01"
                            min="0"
                            class="block w-full pl-7 pr-12 rounded-md border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                            placeholder="0.00"
                          />
                        </div>
                      </div>
                      <div class="flex items-center">
                        <input
                          id="variant-available"
                          type="checkbox"
                          v-model="variantForm.isAvailable"
                          class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                        />
                        <label for="variant-available" class="ml-2 block text-sm text-gray-700">
                          Available for ordering
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 sm:ml-3 sm:w-auto"
                  @click="handleSaveVariant"
                >
                  Save
                </button>
                <button
                  type="button"
                  class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
                  @click="resetVariantForm"
                >
                  Cancel
                </button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>
