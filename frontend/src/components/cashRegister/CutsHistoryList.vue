<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
    <!-- Header -->
    <div class="p-4 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-purple-600 dark:text-purple-400" viewBox="0 0 20 20" fill="currentColor">
            <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
            <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clip-rule="evenodd" />
          </svg>
          {{ t('app.views.cashRegister.cutsHistory') }}
        </h3>
        <button
          v-if="!isExpanded"
          @click="loadCuts"
          :disabled="loading"
          class="text-sm text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 font-medium disabled:opacity-50"
        >
          {{ loading ? 'Cargando...' : 'Ver Historial' }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="p-6 text-center">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Cargando cortes...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="p-6 text-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-red-400 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p class="text-sm text-red-600 dark:text-red-400">{{ error }}</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="isExpanded && cuts.length === 0" class="p-6 text-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-400 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p class="text-sm text-gray-500 dark:text-gray-400">{{ t('app.views.cashRegister.noCuts') }}</p>
    </div>

    <!-- Cuts List -->
    <div v-else-if="isExpanded && cuts.length > 0" class="divide-y divide-gray-200 dark:divide-gray-700">
      <div
        v-for="(cut, index) in cuts"
        :key="cut.id"
        class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
      >
        <div class="flex items-start justify-between">
          <!-- Cut Info -->
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-sm font-semibold text-purple-600 dark:text-purple-400">
                {{ t('app.views.cashRegister.cutNumber', { number: cuts.length - index }) }}
              </span>
              <span class="text-xs text-gray-500 dark:text-gray-400">
                {{ formatDate(cut.generated_at) }}
              </span>
            </div>

            <!-- Cut Summary -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
              <div>
                <span class="text-gray-500 dark:text-gray-400">{{ t('app.views.cashRegister.totalSales') }}:</span>
                <span class="ml-1 font-medium text-gray-900 dark:text-white">{{ formatCurrency(getCutData(cut).total_sales) }}</span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">{{ t('app.views.cashRegister.totalExpenses') }}:</span>
                <span class="ml-1 font-medium text-gray-900 dark:text-white">{{ formatCurrency(getCutData(cut).total_expenses) }}</span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">{{ t('app.views.cashRegister.transactions') }}:</span>
                <span class="ml-1 font-medium text-gray-900 dark:text-white">{{ getCutData(cut).total_transactions }}</span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">{{ t('app.views.cashRegister.netCashFlow') }}:</span>
                <span class="ml-1 font-medium text-gray-900 dark:text-white">{{ formatCurrency(getCutData(cut).net_cash_flow) }}</span>
              </div>
            </div>
          </div>

          <!-- View Details Button -->
          <button
            @click="viewCutDetails(cut)"
            class="ml-4 px-3 py-1.5 text-xs font-medium text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/30 rounded-lg transition-colors"
          >
            {{ t('app.views.cashRegister.viewCutDetails') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Cut Details Modal -->
    <Teleport to="body">
      <div
        v-if="selectedCut"
        class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[10001] p-4"
        @click.self="selectedCut = null"
      >
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <!-- Modal Header -->
          <div class="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 sm:p-6">
            <div class="flex items-center justify-between">
              <h2 class="text-xl font-bold text-gray-900 dark:text-white">
                {{ t('app.views.cashRegister.cutDetails') }}
              </h2>
              <button
                @click="selectedCut = null"
                class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Modal Content -->
          <div class="p-4 sm:p-6">
            <CutDetails 
              :cut-data="getCutData(selectedCut)" 
              :is-loading="false"
              :show-border="false"
            />
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import cashRegisterService from '@/services/cashRegisterService';
import { formatCurrency } from '@/utils/priceHelpers';
import CutDetails from '@/components/cashRegister/CutDetails.vue';

const { t } = useI18n();

const props = defineProps<{
  sessionId: number;
  autoLoad?: boolean;
}>();

const cuts = ref<any[]>([]);
const loading = ref(false);
const error = ref('');
const isExpanded = ref(false);
const selectedCut = ref<any>(null);

const loadCuts = async () => {
  if (cuts.value.length > 0 && isExpanded.value) {
    isExpanded.value = false;
    return;
  }

  try {
    loading.value = true;
    error.value = '';
    isExpanded.value = true;
    const response = await cashRegisterService.getAllCuts(props.sessionId);
    
    // Filter only daily_summary reports (cuts)
    const reports = Array.isArray(response) ? response : [];
    cuts.value = reports
      .filter((report: any) => report.report_type === 'daily_summary')
      .sort((a: any, b: any) => new Date(b.generated_at).getTime() - new Date(a.generated_at).getTime());
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Error al cargar cortes';
    console.error('Error loading cuts:', err);
  } finally {
    loading.value = false;
  }
};

const getCutData = (cut: any) => {
  try {
    const data = typeof cut.data === 'string' ? JSON.parse(cut.data) : cut.data;
    // Agregar generated_at del cut principal al objeto de datos
    return {
      ...data,
      generated_at: cut.generated_at
    };
  } catch (e) {
    console.error('Error parsing cut data:', e);
    return {
      total_sales: 0,
      total_expenses: 0,
      total_transactions: 0,
      net_cash_flow: 0,
      cash_payments: 0,
      card_payments: 0,
      digital_payments: 0,
      other_payments: 0,
      generated_at: cut.generated_at
    };
  }
};

const formatDate = (dateString: string) => {
  try {
    const date = new Date(dateString);
    return date.toLocaleString('es-MX', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (e) {
    return dateString;
  }
};

const viewCutDetails = (cut: any) => {
  selectedCut.value = cut;
};

onMounted(() => {
  if (props.autoLoad) {
    loadCuts();
  }
});
</script>
