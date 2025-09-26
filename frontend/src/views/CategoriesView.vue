<template>
  <div class="min-h-full dark:bg-gray-950">
    <main>
      <div class="mx-auto max-w-7xl sm:px-6 lg:px-8 dark:bg-gray-950">
        <div class="rounded-lg bg-white dark:bg-gray-900 shadow mb-6">
          <div class="px-4 py-5 sm:p-6">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h2 class="text-base font-semibold text-gray-900 dark:text-gray-100">{{ t('app.views.menu.categories.title') || 'Categories' }}</h2>
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ t('app.views.menu.categories.subtitle') || 'Manage your menu categories' }}</p>
              </div>
              <button type="button" @click="openCategoryModal()" class="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">
                {{ t('app.views.menu.categories.add') || 'Add Category' }}
              </button>
            </div>

            <div v-if="categoriesLoading" class="text-center py-6">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
            </div>
            <div v-else>
              <div v-if="menuCategoriesDetailed.length === 0" class="text-sm text-gray-500 dark:text-gray-400">{{ t('app.views.menu.categories.empty') || 'No categories yet' }}</div>
              <ul v-else class="divide-y divide-gray-200 dark:divide-gray-800">
                <li v-for="cat in menuCategoriesDetailed" :key="cat.id" class="py-2 flex items-center justify-between">
                  <div>
                    <p class="text-sm text-gray-900 dark:text-gray-100">{{ cat.name }}</p>
                    <p v-if="cat.description" class="text-xs text-gray-500 dark:text-gray-400">{{ cat.description }}</p>
                  </div>
                  <div class="flex items-center space-x-3">
                    <button type="button" class="text-indigo-600 hover:text-indigo-800 dark:text-indigo-400" @click="openCategoryModal(cat)">{{ t('app.actions.edit') || 'Edit' }}</button>
                    <ConfirmDeleteButton
                      :title="getCategoryDeleteTitle()"
                      :message="getCategoryDeleteMessage(cat)"
                      :confirmText="t('app.actions.delete') as string"
                      :cancelText="t('app.actions.cancel') as string"
                      confirmClass="bg-red-600 hover:bg-red-700 focus:ring-red-500"
                      @confirm="onDeleteCategory(cat)"
                    >
                      {{ t('app.actions.delete') || 'Delete' }}
                    </ConfirmDeleteButton>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Category Modal -->
        <div v-if="categoryModalOpen" class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
          <div class="w-full max-w-md rounded-lg bg-white dark:bg-gray-900 p-6 shadow-lg">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              {{ categoryEditingId !== null ? (t('app.actions.edit') || 'Edit') : (t('app.actions.add') || 'Add') }} {{ t('app.forms.category') || 'Category' }}
            </h3>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">{{ t('app.forms.name') || 'Name' }}</label>
            <input v-model="categoryFormName" type="text" class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-200 mt-4 mb-1">{{ t('app.forms.description') || 'Description' }}</label>
            <textarea v-model="categoryFormDescription" rows="3" class="w-full rounded-md border border-gray-300 dark:border-gray-700 dark:bg-gray-800 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"></textarea>
            <div class="mt-6 flex justify-end space-x-3">
              <button type="button" class="px-4 py-2 rounded-md border border-gray-300 dark:border-gray-700 text-sm" @click="categoryModalOpen = false">{{ t('app.actions.cancel') || 'Cancel' }}</button>
              <button type="button" class="px-4 py-2 rounded-md bg-indigo-600 text-white text-sm" @click="saveCategory">{{ t('app.actions.save') || 'Save' }}</button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useMenuStore } from '@/stores/menu';
import { useToast } from '@/composables/useToast';
import ConfirmDeleteButton from '@/components/ui/ConfirmDeleteButton.vue';
import type { MenuCategory } from '@/types/menu';

const menuStore = useMenuStore();
const { showSuccess, showError } = useToast();
const { t } = useI18n();

// Categories state
const categoriesLoading = ref<boolean>(false);
const categoryModalOpen = ref<boolean>(false);
const categoryFormName = ref<string>('');
const categoryFormDescription = ref<string>('');
const categoryEditingId = ref<string | number | null>(null);
const menuCategoriesDetailed = computed(() => menuStore.categoriesDetailed);

onMounted(async () => {
  await loadCategories();
});

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

function openCategoryModal(existing?: Partial<MenuCategory>) {
  if (existing && typeof existing === 'object') {
    categoryEditingId.value = existing.id ?? null;
    categoryFormName.value = existing.name ?? '';
    categoryFormDescription.value = existing.description ?? '';
  } else {
    categoryEditingId.value = null;
    categoryFormName.value = '';
    categoryFormDescription.value = '';
  }
  categoryModalOpen.value = true;
}

async function saveCategory() {
  const name = categoryFormName.value.trim();
  if (!name) {
    showError(t('validation.name_required') as string);
    return;
  }
  try {
    if (categoryEditingId.value !== null) {
      await (menuStore as any).updateCategory(categoryEditingId.value, { name, description: categoryFormDescription.value });
      showSuccess(t('app.messages.update_success') as string);
    } else {
      await (menuStore as any).createCategory(name, categoryFormDescription.value);
      showSuccess(t('app.messages.create_success') as string);
    }
    categoryModalOpen.value = false;
  } catch (err: any) {
    showError(err?.message || (t('app.messages.submit_failed') as string));
  }
}

async function onDeleteCategory(cat: MenuCategory) {
  try {
    await (menuStore as any).deleteCategory(cat.id);
    showSuccess(t('app.messages.delete_success') as string);
  } catch (err: any) {
    showError(err?.message || (t('app.messages.delete_failed') as string));
  }
}

function getCategoryDeleteTitle(): string {
  return (t('app.views.menu.categories.confirm_delete_title') as string) || 'Delete category';
}

function getCategoryDeleteMessage(cat: { name: string }): string {
  const localized = t('app.views.menu.categories.confirm_delete_message_named', { name: cat.name }) as string;
  return (localized && typeof localized === 'string') ? localized : `Delete category "${cat.name}"?`;
}
</script>
