<template>
  <div class="rounded-lg bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          {{ t('app.views.printers.title') }}
        </h1>
        <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
          {{ t('app.views.printers.description') }}
        </p>
      </div>

      <!-- Add Printer Button - Only show when there are printers -->
      <div v-if="!loading && printers.length > 0" class="mb-6">
        <button
          @click="openCreateModal"
          class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <PlusIcon class="h-5 w-5 mr-2" />
          {{ t('app.views.printers.add_printer') }}
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!loading && printers.length === 0" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">{{ t('app.views.printers.no_printers') }}</h3>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">Comienza agregando tu primera impresora</p>
        <div class="mt-6">
          <button
            @click="openCreateModal"
            class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
          >
            <PlusIcon class="h-5 w-5 mr-2" />
            {{ t('app.views.printers.add_printer') }}
          </button>
        </div>
      </div>

      <!-- Printers by Type - Only show sections that have printers -->
      <div v-else class="space-y-8">
        <!-- Kitchen Printers - Only show if has printers -->
        <PrinterTypeSection
          v-if="printersByType.kitchen.length > 0"
          :title="t('app.views.printers.types.kitchen')"
          :printers="printersByType.kitchen"
          :type="PrinterType.KITCHEN"
          @edit="openEditModal"
          @delete="confirmDelete"
          @toggleActive="toggleActive"
          @setDefault="setAsDefault"
          @assignCategories="openCategoryModal"
        />

        <!-- Bar Printers - Only show if has printers -->
        <PrinterTypeSection
          v-if="printersByType.bar.length > 0"
          :title="t('app.views.printers.types.bar')"
          :printers="printersByType.bar"
          :type="PrinterType.BAR"
          @edit="openEditModal"
          @delete="confirmDelete"
          @toggleActive="toggleActive"
          @setDefault="setAsDefault"
          @assignCategories="openCategoryModal"
        />

        <!-- Cashier Printers - Only show if has printers -->
        <PrinterTypeSection
          v-if="printersByType.cashier.length > 0"
          :title="t('app.views.printers.types.cashier')"
          :printers="printersByType.cashier"
          :type="PrinterType.CASHIER"
          @edit="openEditModal"
          @delete="confirmDelete"
          @toggleActive="toggleActive"
          @setDefault="setAsDefault"
          @assignCategories="openCategoryModal"
        />
      </div>

      <!-- Printer Form Modal -->
      <PrinterFormModal
        v-if="showFormModal"
        :printer="selectedPrinter"
        :categories="categories"
        @close="closeFormModal"
        @save="handleSave"
      />

      <!-- Category Assignment Modal -->
      <CategoryAssignmentModal
        v-if="showCategoryModal"
        :printer="selectedPrinter"
        :categories="categories"
        @close="closeCategoryModal"
        @save="handleCategoryAssignment"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { PlusIcon } from '@heroicons/vue/24/outline';
import {
  getPrinters,
  createPrinter,
  updatePrinter,
  deletePrinter,
  assignCategoriesToPrinter,
  type Printer,
  type PrinterCreate,
  type PrinterUpdate,
  PrinterType
} from '@/services/printerService';
import { getCategories, type Category } from '@/services/menuService';
import { useToast } from '@/composables/useToast';
import { useConfirm } from '@/composables/useConfirm';
import PrinterTypeSection from '@/components/printers/PrinterTypeSection.vue';
import PrinterFormModal from '@/components/printers/PrinterFormModal.vue';
import CategoryAssignmentModal from '@/components/printers/CategoryAssignmentModal.vue';

const { t } = useI18n();
const { showToast } = useToast();
const { confirm } = useConfirm();

const loading = ref(false);
const printers = ref<Printer[]>([]);
const categories = ref<Category[]>([]);
const showFormModal = ref(false);
const showCategoryModal = ref(false);
const selectedPrinter = ref<Printer | null>(null);

const printersByType = computed(() => {
  const grouped: Record<PrinterType, Printer[]> = {
    [PrinterType.KITCHEN]: [],
    [PrinterType.BAR]: [],
    [PrinterType.CASHIER]: []
  };
  
  printers.value.forEach(printer => {
    grouped[printer.printer_type].push(printer);
  });
  
  return grouped;
});

const loadPrinters = async () => {
  try {
    loading.value = true;
    const response = await getPrinters();
    printers.value = response.printers;
  } catch (error) {
    console.error('Error loading printers:', error);
    showToast(t('app.views.printers.errors.load_failed'), 'error');
  } finally {
    loading.value = false;
  }
};

const loadCategories = async () => {
  try {
    categories.value = await getCategories();
  } catch (error) {
    console.error('Error loading categories:', error);
  }
};

const openCreateModal = () => {
  selectedPrinter.value = null;
  showFormModal.value = true;
};

const openEditModal = (printer: Printer) => {
  selectedPrinter.value = printer;
  showFormModal.value = true;
};

const closeFormModal = () => {
  showFormModal.value = false;
  selectedPrinter.value = null;
};

const openCategoryModal = (printer: Printer) => {
  selectedPrinter.value = printer;
  showCategoryModal.value = true;
};

const closeCategoryModal = () => {
  showCategoryModal.value = false;
  selectedPrinter.value = null;
};

const handleSave = async (printerData: PrinterCreate | PrinterUpdate) => {
  try {
    if (selectedPrinter.value) {
      await updatePrinter(selectedPrinter.value.id, printerData as PrinterUpdate);
      showToast(t('app.views.printers.success.updated'), 'success');
    } else {
      await createPrinter(printerData as PrinterCreate);
      showToast(t('app.views.printers.success.created'), 'success');
    }
    closeFormModal();
    await loadPrinters();
  } catch (error: any) {
    console.error('Error saving printer:', error);
    showToast(
      error.response?.data?.error?.message || t('app.views.printers.errors.save_failed'),
      'error'
    );
  }
};

const handleCategoryAssignment = async (categoryIds: number[]) => {
  if (!selectedPrinter.value) return;
  
  try {
    await assignCategoriesToPrinter(selectedPrinter.value.id, categoryIds);
    showToast(t('app.views.printers.success.categories_assigned'), 'success');
    closeCategoryModal();
    await loadPrinters();
  } catch (error) {
    console.error('Error assigning categories:', error);
    showToast(t('app.views.printers.errors.assign_failed'), 'error');
  }
};

const confirmDelete = async (printer: Printer) => {
  const confirmed = await confirm(
    t('app.views.printers.confirm_delete_title'),
    t('app.views.printers.confirm_delete', { name: printer.name }),
    t('app.actions.delete'),
    t('app.actions.cancel')
  );
  
  if (confirmed) {
    try {
      await deletePrinter(printer.id);
      showToast(t('app.views.printers.success.deleted'), 'success');
      await loadPrinters();
    } catch (error) {
      console.error('Error deleting printer:', error);
      showToast(t('app.views.printers.errors.delete_failed'), 'error');
    }
  }
};

const toggleActive = async (printer: Printer) => {
  try {
    await updatePrinter(printer.id, { is_active: !printer.is_active });
    showToast(
      printer.is_active
        ? t('app.views.printers.success.deactivated')
        : t('app.views.printers.success.activated'),
      'success'
    );
    await loadPrinters();
  } catch (error) {
    console.error('Error toggling printer status:', error);
    showToast(t('app.views.printers.errors.toggle_failed'), 'error');
  }
};

const setAsDefault = async (printer: Printer) => {
  try {
    await updatePrinter(printer.id, { is_default: true });
    showToast(t('app.views.printers.success.set_default'), 'success');
    await loadPrinters();
  } catch (error) {
    console.error('Error setting default printer:', error);
    showToast(t('app.views.printers.errors.set_default_failed'), 'error');
  }
};

onMounted(async () => {
  await Promise.all([loadPrinters(), loadCategories()]);
});
</script>
