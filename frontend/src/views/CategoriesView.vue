<template>
  <MainLayout>
    <div class="sm:flex sm:items-center">
      <div class="sm:flex-auto">
        <h1 class="text-base font-semibold leading-6 text-gray-900 dark:text-gray-100">{{ t('app.views.menu.categories.title') || 'Categories' }}</h1>
        <p class="mt-2 text-sm text-gray-700 dark:text-gray-400">
          {{ t('app.views.menu.categories.subtitle') || 'Manage your menu categories' }}
        </p>
      </div>
      <div class="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
        <button
          type="button"
          @click="openCategoryModal()"
          class="block rounded-md bg-indigo-600 px-3 py-2 text-center text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
        >
          {{ t('app.views.menu.categories.add') || 'Add Category' }}
        </button>
      </div>
    </div>
    
    <div class="mt-8 flow-root">
      <div class="overflow-x-auto">
        <div class="inline-block min-w-full py-2 align-middle">
          <div v-if="categoriesLoading" class="text-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
          </div>
          <div v-else class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg dark:bg-gray-950">
            <div v-if="menuCategoriesDetailed.length === 0" class="text-center py-12 text-sm text-gray-500 dark:text-gray-400">
              {{ t('app.views.menu.categories.empty') || 'No categories yet' }}
            </div>
            <ul v-else class="divide-y divide-gray-200 dark:divide-gray-700 bg-white dark:bg-gray-900">
              <li v-for="cat in menuCategoriesDetailed" :key="cat.id" :data-dropdown-container="`category-${cat.id}`" class="px-4 py-4 sm:px-6 relative hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                <div class="flex items-center justify-between">
                  <div class="flex-1 min-w-0 pr-12">
                    <p class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ cat.name }}</p>
                    <p v-if="cat.description" class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ cat.description }}</p>
                  </div>
                  <div v-if="cat.id" class="absolute top-4 right-4" @click.stop>
                    <DropdownMenu
                      :id="`category-${cat.id}`"
                      button-label="Category actions"
                      width="md"
                    >
                      <DropdownMenuItem
                        :icon="PencilIcon"
                        variant="default"
                        @click="openCategoryModal(cat)"
                      >
                        {{ t('app.actions.edit') }}
                      </DropdownMenuItem>
                      
                      <DropdownMenuDivider />
                      
                      <DropdownMenuItem
                        :icon="TrashIcon"
                        variant="danger"
                        @click="confirmDeleteCategory(cat)"
                      >
                        {{ t('app.actions.delete') }}
                      </DropdownMenuItem>
                    </DropdownMenu>
                  </div>
                </div>
              </li>
            </ul>
          </div>
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
              <button type="button" class="px-4 py-2 rounded-md bg-indigo-600 text-white text-sm hover:bg-indigo-500" @click="saveCategory">{{ t('app.actions.save') || 'Save' }}</button>
            </div>
          </div>
        </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useMenuStore } from '@/stores/menu';
import { useToast } from '@/composables/useToast';
import { useConfirm } from '@/composables/useConfirm';
import MainLayout from '@/components/layout/MainLayout.vue';
import DropdownMenu from '@/components/ui/DropdownMenu.vue';
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue';
import DropdownMenuDivider from '@/components/ui/DropdownMenuDivider.vue';
import { PencilIcon, TrashIcon } from '@heroicons/vue/24/outline';
import type { MenuCategory } from '@/types/menu';

const menuStore = useMenuStore();
const { showSuccess, showError } = useToast();
const { confirm } = useConfirm();
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

async function confirmDeleteCategory(cat: MenuCategory) {
  const confirmed = await confirm(
    getCategoryDeleteTitle(),
    getCategoryDeleteMessage(cat),
    t('app.actions.delete') as string,
    t('app.actions.cancel') as string,
    'bg-red-600 hover:bg-red-700 focus:ring-red-500'
  );
  
  if (confirmed) {
    await onDeleteCategory(cat);
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
