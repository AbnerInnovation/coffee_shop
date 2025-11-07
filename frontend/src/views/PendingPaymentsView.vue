<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
        Pagos Pendientes
      </h1>
      <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
        Revisa y aprueba los pagos de suscripción pendientes
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
        No hay pagos pendientes
      </h3>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Todos los pagos han sido procesados
      </p>
    </div>

    <!-- Payments List -->
    <div v-else class="space-y-4">
      <div
        v-for="payment in payments"
        :key="payment.id"
        class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden"
      >
        <div class="p-6">
          <div class="flex items-start justify-between">
            <!-- Payment Info -->
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                  {{ payment.restaurant_name || `Restaurant #${payment.restaurant_id}` }}
                </h3>
                <span class="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                  Pendiente
                </span>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Plan</p>
                  <p class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ payment.plan_name || 'N/A' }}
                  </p>
                </div>

                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Monto</p>
                  <p class="text-lg font-bold text-gray-900 dark:text-white">
                    ${{ formatMoney(payment.amount) }}
                  </p>
                </div>

                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Ciclo</p>
                  <p class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ payment.billing_cycle === 'monthly' ? 'Mensual' : 'Anual' }}
                  </p>
                </div>

                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Referencia</p>
                  <p class="text-sm font-mono font-medium text-gray-900 dark:text-white">
                    {{ payment.reference_number }}
                  </p>
                </div>

                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Fecha de Pago</p>
                  <p class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ formatDate(payment.payment_date) }}
                  </p>
                </div>

                <div>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Enviado</p>
                  <p class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ formatDate(payment.created_at) }}
                  </p>
                </div>
              </div>

              <!-- Proof Image -->
              <div v-if="payment.proof_image_url" class="mt-4">
                <p class="text-sm text-gray-500 dark:text-gray-400 mb-2">Comprobante</p>
                <a 
                  :href="payment.proof_image_url" 
                  target="_blank"
                  class="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 underline"
                >
                  Ver comprobante →
                </a>
              </div>

              <!-- Notes -->
              <div v-if="payment.notes" class="mt-4">
                <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Notas</p>
                <p class="text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-700 p-3 rounded">
                  {{ payment.notes }}
                </p>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="mt-6 flex gap-3">
            <button
              @click="openApproveModal(payment)"
              class="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
            >
              <CheckCircleIcon class="w-5 h-5 inline mr-2" />
              Aprobar
            </button>
            <button
              @click="openRejectModal(payment)"
              class="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
            >
              <XCircleIcon class="w-5 h-5 inline mr-2" />
              Rechazar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Approve Modal -->
    <div v-if="showApproveModal" class="fixed inset-0 z-50 overflow-y-auto" @click.self="closeModals">
      <div class="flex items-center justify-center min-h-screen px-4">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75" @click="closeModals"></div>
        
        <div class="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Aprobar Pago
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
            ¿Estás seguro de aprobar este pago de <strong>${{ formatMoney(selectedPayment?.amount || 0) }}</strong> 
            para {{ selectedPayment?.restaurant_name }}?
          </p>
          <div class="flex gap-3">
            <button
              @click="closeModals"
              class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              Cancelar
            </button>
            <button
              @click="approvePayment"
              :disabled="processing"
              class="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
            >
              {{ processing ? 'Procesando...' : 'Confirmar' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Reject Modal -->
    <div v-if="showRejectModal" class="fixed inset-0 z-50 overflow-y-auto" @click.self="closeModals">
      <div class="flex items-center justify-center min-h-screen px-4">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75" @click="closeModals"></div>
        
        <div class="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Rechazar Pago
          </h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Proporciona una razón para rechazar este pago (mínimo 10 caracteres):
          </p>
          <textarea
            v-model="rejectionReason"
            rows="4"
            placeholder="Ej: El comprobante no es válido, el monto no coincide, etc."
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white mb-2"
          ></textarea>
          <p class="text-xs text-gray-500 dark:text-gray-400 mb-4">
            {{ rejectionReason.length }}/10 caracteres
          </p>
          <div class="flex gap-3">
            <button
              @click="closeModals"
              class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              Cancelar
            </button>
            <button
              @click="rejectPayment"
              :disabled="processing || rejectionReason.trim().length < 10"
              class="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
            >
              {{ processing ? 'Procesando...' : 'Rechazar' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ArrowPathIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/vue/24/outline'
import { useToast } from '@/composables/useToast'
import api from '@/services/api'

interface Payment {
  id: number
  restaurant_id: number
  subscription_id: number
  plan_id: number
  amount: number
  billing_cycle: string
  payment_method: string
  reference_number: string
  payment_date: string | null
  proof_image_url: string | null
  notes: string | null
  status: string
  created_at: string
  restaurant_name?: string
  plan_name?: string
}

const { showSuccess, showError } = useToast()

const loading = ref(true)
const payments = ref<Payment[]>([])
const showApproveModal = ref(false)
const showRejectModal = ref(false)
const selectedPayment = ref<Payment | null>(null)
const rejectionReason = ref('')
const processing = ref(false)

const loadPayments = async () => {
  loading.value = true
  try {
    const response = await api.get('/sysadmin/payments/pending') as unknown as Payment[]
    payments.value = response
  } catch (error: any) {
    showError(error.response?.data?.detail || 'Error al cargar pagos')
  } finally {
    loading.value = false
  }
}

const openApproveModal = (payment: Payment) => {
  selectedPayment.value = payment
  showApproveModal.value = true
}

const openRejectModal = (payment: Payment) => {
  selectedPayment.value = payment
  rejectionReason.value = ''
  showRejectModal.value = true
}

const closeModals = () => {
  showApproveModal.value = false
  showRejectModal.value = false
  selectedPayment.value = null
  rejectionReason.value = ''
}

const approvePayment = async () => {
  if (!selectedPayment.value) return

  processing.value = true
  try {
    await api.post(`/sysadmin/payments/${selectedPayment.value.id}/approve`)
    showSuccess('Pago aprobado exitosamente')
    closeModals()
    await loadPayments()
  } catch (error: any) {
    showError(error.response?.data?.detail || 'Error al aprobar pago')
  } finally {
    processing.value = false
  }
}

const rejectPayment = async () => {
  if (!selectedPayment.value || rejectionReason.value.trim().length < 10) {
    showError('La razón debe tener al menos 10 caracteres')
    return
  }

  processing.value = true
  try {
    await api.post(`/sysadmin/payments/${selectedPayment.value.id}/reject`, {
      reason: rejectionReason.value.trim()
    })
    showSuccess('Pago rechazado')
    closeModals()
    await loadPayments()
  } catch (error: any) {
    showError(error.response?.data?.detail || 'Error al rechazar pago')
  } finally {
    processing.value = false
  }
}

const formatMoney = (amount: number) => {
  return amount.toLocaleString('es-MX', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

const formatDate = (dateString: string | null) => {
  if (!dateString) return 'N/A'
  
  const date = new Date(dateString)
  return date.toLocaleDateString('es-MX', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadPayments()
})
</script>
