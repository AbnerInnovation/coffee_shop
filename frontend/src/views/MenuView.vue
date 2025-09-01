<template>
  <div class="min-h-full">
    <div class="py-10">
      <header>
        <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <h1 class="text-3xl font-bold leading-tight tracking-tight text-gray-900">
            Menu Management
          </h1>
        </div>
      </header>
      <main>
        <div class="mx-auto max-w-7xl sm:px-6 lg:px-8">
          <div class="px-4 py-8 sm:px-0">
            <!-- Menu List -->
            <MenuList
              v-if="!showForm"
              :menu-items="menuItems"
              :loading="loading"
              :error="error"
              @add-item="handleAddItem"
              @edit-item="handleEditItem"
              @delete-item="handleDeleteItem"
              @toggle-availability="handleToggleAvailability"
            />

            <!-- Menu Item Form -->
            <div v-else>
              <div class="mb-6">
                <button
                  type="button"
                  @click="showForm = false; currentItem = null"
                  class="inline-flex items-center text-sm text-gray-600 hover:text-gray-900"
                >
                  <ArrowLeftIcon class="mr-1 h-4 w-4" />
                  Back to menu items
                </button>
              </div>
              
              <div class="rounded-lg bg-white shadow">
                <div class="px-4 py-5 sm:p-6">
                  <MenuItemForm
                    :menu-item="currentItem || {}"
                    :loading="formLoading"
                    :errors="formErrors"
                    :is-editing="!!currentItem"
                    @submit="handleSubmit"
                    @cancel="showForm = false"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useMenuStore } from '@/stores/menu';
import { useConfirm } from '@/composables/useConfirm';
import { useToast } from '@/composables/useToast';
import MenuList from '@/components/menu/MenuList.vue';
import MenuItemForm, { type MenuItemFormData } from '@/components/menu/MenuItemForm.vue';
import type { MenuItem } from '@/components/menu/MenuItemCard.vue';
import { ArrowLeftIcon } from '@heroicons/vue/20/solid';

const menuStore = useMenuStore();
const { confirm } = useConfirm();
const { showSuccess, showError } = useToast();

const menuItems = ref<MenuItem[]>([]);
const loading = ref<boolean>(false);
const error = ref<string | null>(null);
const showForm = ref<boolean>(false);
const formLoading = ref<boolean>(false);
const formErrors = ref<Record<string, string>>({});
const currentItem = ref<MenuItem | null>(null);

// Fetch menu items on component mount
onMounted(async () => {
  await loadMenuItems();
});

async function loadMenuItems() {
  loading.value = true;
  error.value = null;
  try {
    menuItems.value = await menuStore.fetchMenuItems();
  } catch (err) {
    error.value = err.message || 'Failed to load menu items';
    showError(error.value);
  } finally {
    loading.value = false;
  }
}

function handleAddItem() {
  currentItem.value = null;
  showForm.value = true;
  formErrors.value = {};
}

function handleEditItem(item) {
  currentItem.value = { ...item };
  showForm.value = true;
  formErrors.value = {};
}

async function handleDeleteItem(item) {
  const confirmed = await confirm(
    'Delete Menu Item',
    `Are you sure you want to delete "${item.name}"? This action cannot be undone.`,
    'Delete',
    'Cancel',
    'bg-red-600 hover:bg-red-700 focus:ring-red-500'
  )

  if (!confirmed) return

  try {
    await menuStore.deleteMenuItem(item.id)
    menuItems.value = menuItems.value.filter(i => i.id !== item.id)
    showSuccess('Menu item deleted successfully')
  } catch (err: any) {
    showError(err.message || 'Failed to delete menu item')
  }
}

async function handleToggleAvailability(item) {
  try {
    const updatedItem = await menuStore.toggleMenuItemAvailability(
      item.id,
      !item.is_available
    );
    
    // Update the item in the list
    const index = menuItems.value.findIndex(i => i.id === item.id);
    if (index !== -1) {
      menuItems.value[index] = updatedItem;
    }
    
    showSuccess(
      `Menu item ${updatedItem.is_available ? 'enabled' : 'disabled'} successfully`
    );
  } catch (err) {
    showError(err.message || 'Failed to update menu item availability');
  }
}

async function handleSubmit(formData: MenuItemFormData) {
  formLoading.value = true;
  formErrors.value = {};
  
  try {
    if (currentItem.value) {
      // Update existing item
      const updatedItem = await menuStore.updateMenuItem(
        currentItem.value.id.toString(),
        formData
      );
      
      // Update the item in the list
      const index = menuItems.value.findIndex(i => i.id === updatedItem.id);
      if (index !== -1) {
        menuItems.value[index] = updatedItem;
      }
      
      showSuccess('Menu item updated successfully');
    } else {
      // Create new item
      const newItem = await menuStore.createMenuItem(formData);
      menuItems.value.unshift(newItem);
      showSuccess('Menu item created successfully');
    }
    
    // Go back to the list
    showForm.value = false;
    currentItem.value = null;
  } catch (err: any) {
    if (err.response?.data?.detail) {
      formErrors.value = err.response.data.detail;
    } else {
      showError(err.message || 'An error occurred while saving the menu item');
    }
  } finally {
    formLoading.value = false;
  }
}
</script>
