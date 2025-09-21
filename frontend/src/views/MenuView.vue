<template>
  <div class="min-h-full dark:bg-gray-950">
      <main>
        <div class="mx-auto max-w-7xl sm:px-6 lg:px-8 dark:bg-gray-950">
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
                  {{ t('app.views.menu.view.back') }}
                </button>
              </div>
              
              <div class="rounded-lg bg-white dark:bg-gray-900 shadow">
                <div class="px-4 py-5 sm:p-6">
                  <MenuItemForm
                    v-if="currentItem !== null"
                    :menu-item="currentItem"
                    :loading="formLoading"
                    :errors="formErrors"
                    :is-editing="true"
                    @submit="handleSubmit"
                    @cancel="showForm = false"
                  />
                  <MenuItemForm
                    v-else
                    :loading="formLoading"
                    :errors="formErrors"
                    :is-editing="false"
                    @submit="handleSubmit"
                    @cancel="showForm = false"
                  />
                </div>
              </div>
            </div>
        </div>
      </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useMenuStore } from '@/stores/menu';
import { useConfirm } from '@/composables/useConfirm';
import { useToast } from '@/composables/useToast';
import MenuList from '@/components/menu/MenuList.vue';
import MenuItemForm from '@/components/menu/MenuItemForm.vue';
import type { MenuItem } from '@/types/menu';
import { ArrowLeftIcon } from '@heroicons/vue/20/solid';

const menuStore = useMenuStore();
const { confirm } = useConfirm();
const { showSuccess, showError } = useToast();
const { t } = useI18n();

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
  console.log('Loading menu items...');
  loading.value = true;
  error.value = null;
  try {
    const items = await menuStore.fetchMenuItems();
    console.log('Fetched menu items:', items);
    menuItems.value = items;
    console.log('menuItems after update:', menuItems.value);
  } catch (err: unknown) {
    const errorMessage = err instanceof Error ? err.message : 'Failed to load menu items';
    console.error('Error loading menu items:', errorMessage);
    error.value = errorMessage;
    showError(errorMessage);
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
  } catch (err: any) {
    showError(err.message || 'Failed to update menu item availability');
  }
}

async function handleSubmit(formData: Omit<MenuItem, 'id'>) {
  formLoading.value = true;
  formErrors.value = {};
  
  try {
    if (currentItem.value) {
      // Update existing item
      await menuStore.updateMenuItem(currentItem.value.id, formData);
      showSuccess('Menu item updated successfully');
    } else {
      // Create new item
      await menuStore.createMenuItem(formData);
      showSuccess('Menu item created successfully');
    }
    
    // Refresh the menu items list
    await loadMenuItems();
    showForm.value = false;
    currentItem.value = null;
  } catch (err: unknown) {
    const error = err as any;
    if (error?.response?.data?.errors) {
      formErrors.value = error.response.data.errors;
    } else {
      const errorMessage = error instanceof Error ? error.message : 'Failed to save menu item';
      showError(errorMessage);
    }
  } finally {
    formLoading.value = false;
  }
}
</script>
