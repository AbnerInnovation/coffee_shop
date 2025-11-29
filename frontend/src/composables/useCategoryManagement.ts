import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useMenuStore } from '@/stores/menu';
import { useToast } from '@/composables/useToast';
import { useConfirm } from '@/composables/useConfirm';
import { handleError } from '@/utils/errorTranslator';
import type { MenuCategory } from '@/types/menu';

export function useCategoryManagement() {
  const menuStore = useMenuStore();
  const { showSuccess, showError } = useToast();
  const { confirm } = useConfirm();
  const { t } = useI18n();

  // State
  const categoriesLoading = ref<boolean>(false);
  const categoryModalOpen = ref<boolean>(false);
  const categoryFormName = ref<string>('');
  const categoryFormDescription = ref<string>('');
  const categoryFormVisibleInKitchen = ref<boolean>(true);
  const categoryEditingId = ref<string | number | null>(null);
  const subscriptionLimitError = ref<string>('');
  
  // Computed
  const menuCategoriesDetailed = computed(() => menuStore.categoriesDetailed);
  const isEditing = computed(() => categoryEditingId.value !== null);

  // Load categories
  async function loadCategories() {
    categoriesLoading.value = true;
    try {
      await menuStore.getCategories(true);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load categories';
      showError(msg);
    } finally {
      categoriesLoading.value = false;
    }
  }

  // Initialize
  async function initialize() {
    await loadCategories();
  }

  // Open modal for add or edit
  function openModal(category?: MenuCategory) {
    if (category && category.id) {
      categoryEditingId.value = category.id;
      categoryFormName.value = category.name;
      categoryFormDescription.value = category.description || '';
      categoryFormVisibleInKitchen.value = (category as any).visible_in_kitchen !== false;
    } else {
      categoryEditingId.value = null;
      categoryFormName.value = '';
      categoryFormDescription.value = '';
      categoryFormVisibleInKitchen.value = true;
    }
    subscriptionLimitError.value = '';
    categoryModalOpen.value = true;
  }

  // Close modal
  function closeModal() {
    categoryModalOpen.value = false;
    categoryEditingId.value = null;
    categoryFormName.value = '';
    categoryFormDescription.value = '';
    categoryFormVisibleInKitchen.value = true;
    subscriptionLimitError.value = '';
  }

  // Validate form
  function validateForm(): boolean {
    const name = categoryFormName.value.trim();
    if (!name) {
      showError(t('validation.name_required') as string);
      return false;
    }
    return true;
  }

  // Handle subscription limit error
  function handleLimitError(error: any) {
    const message = error.response?.data?.detail || 
                   error.response?.data?.error?.message || 
                   'Límite de suscripción alcanzado. Por favor mejora tu plan.';
    subscriptionLimitError.value = message;
  }

  // Handle general error
  function handleGeneralError(error: any) {
    const errorMessage = error?.response?.data?.detail || 
                        error?.response?.data?.error?.message ||
                        error?.message || 
                        (t('app.messages.submit_failed') as string);
    showError(errorMessage);
  }

  // Save category (create or update)
  async function saveCategory() {
    if (!validateForm()) return;

    const name = categoryFormName.value.trim();
    const description = categoryFormDescription.value;
    const visibleInKitchen = categoryFormVisibleInKitchen.value;

    try {
      if (categoryEditingId.value !== null) {
        await (menuStore as any).updateCategory(categoryEditingId.value, { name, description, visible_in_kitchen: visibleInKitchen });
        showSuccess(t('app.messages.update_success') as string);
      } else {
        await (menuStore as any).createCategory(name, description, visibleInKitchen);
        showSuccess(t('app.messages.create_success') as string);
      }
      closeModal();
    } catch (err: any) {
      // Handle subscription limit errors (403)
      if (err?.response?.status === 403) {
        handleLimitError(err);
        return; // Don't close modal
      }
      
      handleGeneralError(err);
    }
  }

  // Delete category with confirmation
  async function deleteCategory(category: MenuCategory) {
    const confirmed = await confirm(
      getCategoryDeleteTitle(),
      getCategoryDeleteMessage(category),
      t('app.actions.delete') as string,
      t('app.actions.cancel') as string,
      'bg-red-600 hover:bg-red-700 focus:ring-red-500'
    );
    
    if (!confirmed) return;

    try {
      await (menuStore as any).deleteCategory(category.id);
      showSuccess(t('app.messages.delete_success') as string);
    } catch (err: any) {
      const errorMessage = handleError(err, t, 'category', t('app.messages.delete_failed') as string);
      showError(errorMessage);
    }
  }

  // Helper functions for delete confirmation
  function getCategoryDeleteTitle(): string {
    return (t('app.views.menu.categories.confirm_delete_title') as string) || 'Delete category';
  }

  function getCategoryDeleteMessage(category: { name: string }): string {
    const localized = t('app.views.menu.categories.confirm_delete_message_named', { name: category.name }) as string;
    return (localized && typeof localized === 'string') ? localized : `Delete category "${category.name}"?`;
  }

  return {
    // State
    categoriesLoading,
    categoryModalOpen,
    categoryFormName,
    categoryFormDescription,
    categoryFormVisibleInKitchen,
    categoryEditingId,
    subscriptionLimitError,
    menuCategoriesDetailed,
    isEditing,
    
    // Methods
    initialize,
    loadCategories,
    openModal,
    closeModal,
    saveCategory,
    deleteCategory
  };
}
