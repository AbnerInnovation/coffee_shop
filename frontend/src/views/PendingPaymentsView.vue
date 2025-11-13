<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
    <!-- Header -->
    <div class="mb-6 sm:mb-8">
      <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
        {{ t('app.pending_payments.title') }}
      </h1>
      <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
        {{ t('app.pending_payments.subtitle') }}
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <ArrowPathIcon class="h-12 w-12 animate-spin text-indigo-600" />
    </div>

    <!-- Empty State -->
    <div v-else-if="!payments || payments.length === 0" class="text-center py-12">
      <CheckCircleIcon class="mx-auto h-12 w-12 text-gray-400" />
      <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">
        {{ t('app.pending_payments.no_payments') }}
      </h3>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        {{ t('app.pending_payments.all_processed') }}
      </p>
    </div>

    <!-- Payments List -->
    <div v-else class="space-y-4">
      <PaymentCard
        v-for="payment in payments"
        :key="payment.id"
        :payment="payment"
        @approve="handleApprove"
        @reject="handleReject"
      />
    </div>

    <!-- Approve Modal -->
    <ApprovePaymentModal
      :show="showApproveModal"
      :payment="selectedPayment"
      :processing="processing"
      @close="closeModals"
      @confirm="confirmApprove"
    />

    <!-- Reject Modal -->
    <RejectPaymentModal
      :show="showRejectModal"
      v-model="rejectionReason"
      :processing="processing"
      @close="closeModals"
      @confirm="confirmReject"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { ArrowPathIcon, CheckCircleIcon } from '@heroicons/vue/24/outline';
import { useToast } from '@/composables/useToast';
import { usePendingPayments, type Payment } from '@/composables/usePendingPayments';
import PaymentCard from '@/components/payments/PaymentCard.vue';
import ApprovePaymentModal from '@/components/payments/ApprovePaymentModal.vue';
import RejectPaymentModal from '@/components/payments/RejectPaymentModal.vue';

const { t } = useI18n();
const { showSuccess, showError } = useToast();

// Composable
const {
  payments,
  loading,
  error,
  processing,
  loadPayments,
  approvePayment,
  rejectPayment
} = usePendingPayments();

// Modal state
const showApproveModal = ref(false);
const showRejectModal = ref(false);
const selectedPayment = ref<Payment | null>(null);
const rejectionReason = ref('');

// Handlers
const handleApprove = (payment: Payment) => {
  selectedPayment.value = payment;
  showApproveModal.value = true;
};

const handleReject = (payment: Payment) => {
  selectedPayment.value = payment;
  rejectionReason.value = '';
  showRejectModal.value = true;
};

const closeModals = () => {
  showApproveModal.value = false;
  showRejectModal.value = false;
  selectedPayment.value = null;
  rejectionReason.value = '';
};

const confirmApprove = async () => {
  if (!selectedPayment.value) return;

  const success = await approvePayment(selectedPayment.value.id);
  
  if (success) {
    showSuccess(t('app.pending_payments.approved_success'));
    closeModals();
  } else if (error.value) {
    showError(error.value);
  }
};

const confirmReject = async () => {
  if (!selectedPayment.value || rejectionReason.value.trim().length < 10) {
    showError(t('app.pending_payments.reason_min_length'));
    return;
  }

  const success = await rejectPayment(selectedPayment.value.id, rejectionReason.value);
  
  if (success) {
    showSuccess(t('app.pending_payments.rejected_success'));
    closeModals();
  } else if (error.value) {
    showError(error.value);
  }
};

// Initialize
onMounted(() => {
  loadPayments();
});
</script>
