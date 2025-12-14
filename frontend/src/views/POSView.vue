<template>
  <div class="h-full bg-gray-100 dark:bg-gray-900 flex flex-col">
    <!-- Main Content -->
    <main class="flex-1 overflow-hidden flex items-center justify-center p-4">
      <!-- Button to open POS when modal is closed -->
      <div v-if="!isModalOpen" class="text-center">
        <div class="mb-8">
          <svg class="mx-auto h-24 w-24 text-gray-400 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
          <h2 class="mt-4 text-2xl font-semibold text-gray-900 dark:text-gray-100">
            {{ t('app.views.pos.title') || 'Punto de Venta' }}
          </h2>
          <p class="mt-2 text-gray-600 dark:text-gray-400">
            {{ t('app.views.pos.description') || 'Gestiona tus ventas de forma rápida y eficiente' }}
          </p>
          
          <!-- Session stats if any -->
          <div v-if="sessionStats.salesCount > 0" class="mt-6 inline-flex items-center gap-6 px-6 py-3 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <div class="text-center">
              <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('app.views.pos.sales_today') || 'Ventas' }}</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ sessionStats.salesCount }}</p>
            </div>
            <div class="h-12 w-px bg-gray-200 dark:bg-gray-700"></div>
            <div class="text-center">
              <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('app.views.pos.total') || 'Total' }}</p>
              <p class="text-2xl font-bold text-green-600 dark:text-green-400">${{ sessionStats.totalAmount.toFixed(2) }}</p>
            </div>
          </div>
        </div>
        
        <button
          type="button"
          @click="openPOS"
          class="inline-flex items-center px-8 py-4 border border-transparent text-lg font-medium rounded-lg shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
        >
          <svg class="h-6 w-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          {{ t('app.views.pos.open_pos') || 'Abrir POS' }}
        </button>
      </div>

      <!-- Modal - Full screen in POS mode -->
      <div v-else class="fixed inset-0 z-50">
        <NewOrderModal
          :open="isModalOpen"
          :mode="'create'"
          :pos-mode="true"
          @close="handleModalClose"
          @order-created="handleOrderCreated"
        />
      </div>
    </main>

    <!-- Last Sale Indicator -->
    <Transition
      enter-active-class="transition ease-out duration-300"
      enter-from-class="translate-y-full opacity-0"
      enter-to-class="translate-y-0 opacity-100"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="translate-y-0 opacity-100"
      leave-to-class="translate-y-full opacity-0"
    >
      <div
        v-if="lastSale && showLastSaleNotification"
        class="fixed bottom-6 right-6 bg-green-50 dark:bg-green-900/20 border-2 border-green-500 dark:border-green-600 rounded-lg shadow-lg p-4 max-w-sm"
      >
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svg class="h-6 w-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="ml-3 flex-1">
            <h3 class="text-sm font-medium text-green-800 dark:text-green-200">
              {{ t('app.views.pos.sale_completed') || '¡Venta Completada!' }}
            </h3>
            <div class="mt-1 text-sm text-green-700 dark:text-green-300">
              <p>{{ t('app.views.pos.ticket') || 'Ticket' }}: #{{ lastSale.ticket_number }}</p>
              <p class="font-semibold">{{ t('app.views.pos.total') || 'Total' }}: ${{ lastSale.total?.toFixed(2) || '0.00' }}</p>
            </div>
          </div>
          <button
            type="button"
            @click="showLastSaleNotification = false"
            class="ml-4 flex-shrink-0 text-green-600 dark:text-green-400 hover:text-green-800 dark:hover:text-green-200"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import NewOrderModal from '@/components/orders/NewOrderModal.vue';
import { useToast } from '@/composables/useToast';
import { useCashRegisterSession } from '@/composables/useCashRegisterSession';

/**
 * POSView - Dedicated POS view with always-open order modal
 * 
 * This view provides a continuous sales flow for POS mode:
 * - Modal is always open and cannot be closed
 * - Auto-resets after each sale
 * - Shows session statistics
 * - Provides quick access to orders and cash register
 * 
 * Best practices:
 * - Reuses existing NewOrderModal component (no code duplication)
 * - Minimal wrapper logic
 * - Clear separation of concerns
 */

const router = useRouter();
const { t } = useI18n();
const { showSuccess } = useToast();

// Use existing cash register session composable
const { currentSession, transactions, currentBalance } = useCashRegisterSession();

// Modal state - starts closed
const isModalOpen = ref(false);

/**
 * Open POS modal
 */
const openPOS = () => {
  isModalOpen.value = true;
};

// Computed session statistics from transactions
const sessionStats = computed(() => {
  if (!transactions.value.length) {
    return { salesCount: 0, totalAmount: 0 };
  }
  
  // Filter only sale transactions (exclude expenses)
  const salesTransactions = transactions.value.filter(
    (t: any) => t.transaction_type === 'sale' || t.transaction_type === 'SALE'
  );
  
  return {
    salesCount: salesTransactions.length,
    totalAmount: salesTransactions.reduce((sum: number, t: any) => sum + (t.amount || 0), 0)
  };
});

// Last sale tracking
const lastSale = ref<any>(null);
const showLastSaleNotification = ref(false);

/**
 * Handle order creation
 * - Show success notification
 * - Keep modal open for next sale
 * - Session stats update automatically via useCashRegisterSession
 */
const handleOrderCreated = (order: any) => {
  // Store last sale
  lastSale.value = order;
  showLastSaleNotification.value = true;
  
  // Auto-hide notification after 5 seconds
  setTimeout(() => {
    showLastSaleNotification.value = false;
  }, 5000);
  
  // Show success toast
  showSuccess(
    t('app.views.pos.sale_success', { ticket: order.ticket_number }) || 
    `Venta #${order.ticket_number} completada`
  );
  
  // Keep modal open - it will auto-reset internally
  isModalOpen.value = true;
  
  // Trigger event to reload session (useCashRegisterSession listens to this)
  window.dispatchEvent(new Event('orderPaymentCompleted'));
};

/**
 * Handle modal close
 * Close the modal and show the "Abrir POS" button
 */
const handleModalClose = () => {
  isModalOpen.value = false;
};

/**
 * Navigate to orders view
 */
const goToOrders = () => {
  router.push('/orders');
};

/**
 * Handle POS closure
 * Confirm before leaving if there are sales in the session
 */
const handleClosePOS = () => {
  if (sessionStats.value.salesCount > 0) {
    const confirmed = confirm(
      t('app.views.pos.confirm_close') || 
      `¿Cerrar caja? Has realizado ${sessionStats.value.salesCount} ventas por $${sessionStats.value.totalAmount.toFixed(2)}`
    );
    
    if (!confirmed) return;
  }
  
  router.push('/orders');
};

/**
 * Keyboard shortcuts
 */
const handleKeyboard = (event: KeyboardEvent) => {
  // F2: Close POS
  if (event.key === 'F2') {
    event.preventDefault();
    handleClosePOS();
  }
  
  // F3: View orders
  if (event.key === 'F3') {
    event.preventDefault();
    goToOrders();
  }
};

onMounted(() => {
  // Add keyboard shortcuts
  window.addEventListener('keydown', handleKeyboard);
});

onBeforeUnmount(() => {
  // Remove keyboard shortcuts
  window.removeEventListener('keydown', handleKeyboard);
});
</script>
