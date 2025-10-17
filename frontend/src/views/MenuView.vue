<template>
  <MainLayout>
    <!-- Menu List -->
    <MenuList
      v-if="!showForm"
      :menu-items="menuItems"
      :loading="loading"
      :error="error"
      :categories="menuStore.categoriesDetailed"
      :selected-category-id="selectedCategoryId"
      @add-item="handleAddItem"
      @edit-item="handleEditItem"
      @delete-item="handleDeleteItem"
      @toggle-availability="handleToggleAvailability"
      @filter-category="handleFilterCategory"
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
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useMenuStore } from '@/stores/menu';
import { useConfirm } from '@/composables/useConfirm';
import { useToast } from '@/composables/useToast';
import MainLayout from '@/components/layout/MainLayout.vue';
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
const selectedCategoryId = ref<number | null>(null);

// Fetch menu items on component mount
onMounted(async () => {
  // getCategories has built-in caching, so it won't fetch twice
  await menuStore.getCategories();
  await loadMenuItems();
});

async function loadMenuItems(categoryId?: number) {
  loading.value = true;
  error.value = null;
  try {
    const items = await menuStore.fetchMenuItems(categoryId);
    menuItems.value = items;
  } catch (err: unknown) {
    const errorMessage = err instanceof Error ? err.message : 'Failed to load menu items';
    console.error('Error loading menu items:', errorMessage);
    error.value = errorMessage;
    showError(errorMessage);
  } finally {
    loading.value = false;
  }
}

function handleFilterCategory(categoryId: number | null) {
  selectedCategoryId.value = categoryId;
  loadMenuItems(categoryId || undefined);
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
    t('app.messages.delete_item_confirm_title') as string,
    t('app.messages.delete_item_confirm_text_named', { name: item.name }) as string,
    t('app.actions.delete') as string,
    t('app.actions.cancel') as string,
    'bg-red-600 hover:bg-red-700 focus:ring-red-500'
  )

  if (!confirmed) return

  try {
    await menuStore.deleteMenuItem(item.id)
    // Refresh list with current filter to ensure consistency
    await loadMenuItems(selectedCategoryId.value || undefined)
    showSuccess(t('app.messages.delete_item_success') as string)
  } catch (err: any) {
    showError(err.message || (t('app.messages.delete_item_failed') as string))
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
      (updatedItem.is_available
        ? t('app.views.menu.list.enabled_success')
        : t('app.views.menu.list.disabled_success')) as string
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
      showSuccess(t('app.messages.update_item_success') as string);
    } else {
      // Create new item
      await menuStore.createMenuItem(formData);
      showSuccess(t('app.messages.create_item_success') as string);
    }
    
    // Refresh the menu items list with current filter
    await loadMenuItems(selectedCategoryId.value || undefined);
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
