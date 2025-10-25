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
      @add-item="openAddForm"
      @edit-item="openEditForm"
      @delete-item="deleteMenuItem"
      @toggle-availability="toggleAvailability"
      @filter-category="filterByCategory"
    />

    <!-- Menu Item Form -->
    <MenuItemFormContainer
      v-else
      :current-item="currentItem"
      :form-loading="formLoading"
      :form-errors="formErrors"
      @submit="submitForm"
      @cancel="closeForm"
    />

    <!-- Limit Reached Modal -->
    <LimitReachedModal
      :is-open="showLimitModal"
      :message="limitModalData.message"
      :current-usage="limitModalData.currentUsage"
      :max-limit="limitModalData.maxLimit"
      :current-plan="limitModalData.currentPlan"
      limit-type="menu_items"
      @close="showLimitModal = false"
    />
  </MainLayout>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useMenuStore } from '@/stores/menu';
import { useMenuManagement } from '@/composables/useMenuManagement';
import MainLayout from '@/components/layout/MainLayout.vue';
import MenuList from '@/components/menu/MenuList.vue';
import MenuItemFormContainer from '@/components/menu/MenuItemFormContainer.vue';
import LimitReachedModal from '@/components/subscription/LimitReachedModal.vue';

const menuStore = useMenuStore();

// Use the composable for all menu management logic
const {
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
  initialize,
  filterByCategory,
  openAddForm,
  openEditForm,
  closeForm,
  deleteMenuItem,
  toggleAvailability,
  submitForm
} = useMenuManagement();

// Initialize on mount
onMounted(() => {
  initialize();
});
</script>
