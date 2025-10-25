import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useMenuStore } from '@/stores/menu';
import { useConfirm } from '@/composables/useConfirm';
import { useToast } from '@/composables/useToast';
import type { MenuItem } from '@/types/menu';

export interface LimitModalData {
  message: string;
  currentUsage?: number;
  maxLimit?: number;
  currentPlan?: string;
}

export function useMenuManagement() {
  const menuStore = useMenuStore();
  const { confirm } = useConfirm();
  const { showSuccess, showError } = useToast();
  const { t } = useI18n();

  // State
  const menuItems = ref<MenuItem[]>([]);
  const loading = ref<boolean>(false);
  const error = ref<string | null>(null);
  const showForm = ref<boolean>(false);
  const formLoading = ref<boolean>(false);
  const formErrors = ref<Record<string, string>>({});
  const currentItem = ref<MenuItem | null>(null);
  const selectedCategoryId = ref<number | null>(null);
  const showLimitModal = ref(false);
  const limitModalData = ref<LimitModalData>({ message: '' });

  // Load menu items
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

  // Initialize menu data
  async function initialize() {
    await menuStore.getCategories();
    await loadMenuItems();
  }

  // Filter by category
  function filterByCategory(categoryId: number | null) {
    selectedCategoryId.value = categoryId;
    loadMenuItems(categoryId || undefined);
  }

  // Open add form
  function openAddForm() {
    currentItem.value = null;
    showForm.value = true;
    formErrors.value = {};
  }

  // Open edit form
  function openEditForm(item: MenuItem) {
    currentItem.value = { ...item };
    showForm.value = true;
    formErrors.value = {};
  }

  // Close form
  function closeForm() {
    showForm.value = false;
    currentItem.value = null;
    formErrors.value = {};
  }

  // Delete menu item
  async function deleteMenuItem(item: MenuItem) {
    const confirmed = await confirm(
      t('app.messages.delete_item_confirm_title') as string,
      t('app.messages.delete_item_confirm_text_named', { name: item.name }) as string,
      t('app.actions.delete') as string,
      t('app.actions.cancel') as string,
      'bg-red-600 hover:bg-red-700 focus:ring-red-500'
    );

    if (!confirmed) return;

    try {
      await menuStore.deleteMenuItem(item.id);
      await loadMenuItems(selectedCategoryId.value || undefined);
      showSuccess(t('app.messages.delete_item_success') as string);
    } catch (err: any) {
      showError(err.message || (t('app.messages.delete_item_failed') as string));
    }
  }

  // Toggle availability
  async function toggleAvailability(item: MenuItem) {
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

  // Handle subscription limit error
  function handleLimitError(error: any) {
    const message = error.response?.data?.detail || 
                   error.response?.data?.error?.message || 
                   'Límite de suscripción alcanzado';
    
    // Extract usage info from error if available
    const usageMatch = message.match(/(\d+)\s*\/\s*(\d+)/);
    
    limitModalData.value = {
      message,
      currentUsage: usageMatch ? parseInt(usageMatch[1]) : undefined,
      maxLimit: usageMatch ? parseInt(usageMatch[2]) : undefined,
      currentPlan: 'Starter' // TODO: Get from subscription API
    };
    
    showLimitModal.value = true;
  }

  // Handle validation errors
  function handleValidationErrors(error: any) {
    if (error?.response?.data?.errors) {
      formErrors.value = error.response.data.errors;
    } else {
      const errorMessage = error?.response?.data?.detail || 
                          error?.response?.data?.error?.message ||
                          (error instanceof Error ? error.message : 'Failed to save menu item');
      showError(errorMessage);
    }
  }

  // Submit form (create or update)
  async function submitForm(formData: Omit<MenuItem, 'id'>) {
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
      closeForm();
    } catch (err: unknown) {
      const error = err as any;
      
      // Handle subscription limit errors (403)
      if (error?.response?.status === 403) {
        handleLimitError(error);
        return; // Don't close the form, let user see the modal
      }
      
      handleValidationErrors(error);
    } finally {
      formLoading.value = false;
    }
  }

  return {
    // State
    menuItems,
    loading,
    error,
    showForm,
    formLoading,
    formErrors,
    currentItem,
    selectedCategoryId,
    showLimitModal,
    limitModalData,
    
    // Methods
    initialize,
    loadMenuItems,
    filterByCategory,
    openAddForm,
    openEditForm,
    closeForm,
    deleteMenuItem,
    toggleAvailability,
    submitForm
  };
}
