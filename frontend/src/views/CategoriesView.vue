<template>
  <MainLayout>
    <PageHeader
      :title="t('app.views.menu.categories.title') || 'Categories'"
      :subtitle="t('app.views.menu.categories.subtitle') || 'Manage your menu categories'"
    >
      <template #actions>
        <button
          v-if="canEditCategories"
          type="button"
          @click="openModal()"
          class="block rounded-md bg-indigo-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
        >
          {{ t('app.views.menu.categories.add') || 'Add Category' }}
        </button>
      </template>
    </PageHeader>
    
    <!-- Category List -->
    <CategoryList
      :categories="menuCategoriesDetailed"
      :loading="categoriesLoading"
      :can-edit="canEditCategories"
      :empty-message="t('app.views.menu.categories.empty') || 'No categories yet'"
      @edit="openModal"
      @delete="deleteCategory"
    />

    <!-- Category Modal -->
    <CategoryModal
      :is-open="categoryModalOpen"
      v-model:name="categoryFormName"
      v-model:description="categoryFormDescription"
      :is-editing="isEditing"
      :limit-error="subscriptionLimitError"
      @save="saveCategory"
      @cancel="closeModal"
    />
  </MainLayout>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { usePermissions } from '@/composables/usePermissions';
import { useCategoryManagement } from '@/composables/useCategoryManagement';
import MainLayout from '@/components/layout/MainLayout.vue';
import PageHeader from '@/components/layout/PageHeader.vue';
import CategoryList from '@/components/categories/CategoryList.vue';
import CategoryModal from '@/components/categories/CategoryModal.vue';

const { canEditCategories } = usePermissions();
const { t } = useI18n();

// Use the composable for all category management logic
const {
  categoriesLoading,
  categoryModalOpen,
  categoryFormName,
  categoryFormDescription,
  subscriptionLimitError,
  menuCategoriesDetailed,
  isEditing,
  initialize,
  openModal,
  closeModal,
  saveCategory,
  deleteCategory
} = useCategoryManagement();

// Initialize on mount
onMounted(() => {
  initialize();
});
</script>
