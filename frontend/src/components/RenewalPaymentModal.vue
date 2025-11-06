<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 overflow-y-auto" @click.self="close">
    <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75" @click="close"></div>

      <!-- Modal panel -->
      <div class="inline-block w-full max-w-2xl my-8 overflow-hidden text-left align-middle transition-all transform bg-white dark:bg-gray-800 rounded-lg shadow-xl">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between">
            <h3 class="text-xl font-semibold text-gray-900 dark:text-white">
              {{ t('app.subscription.renewal.title') }}
            </h3>
            <button @click="close" class="text-gray-400 hover:text-gray-500">
              <XMarkIcon class="w-6 h-6" />
            </button>
          </div>
          
          <!-- Progress Steps -->
          <div class="mt-4 flex items-center justify-between">
            <div v-for="step in 4" :key="step" class="flex items-center flex-1">
              <div 
                :class="[
                  'w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold',
                  currentStep >= step 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                ]"
              >
                {{ step }}
              </div>
              <div 
                v-if="step < 4" 
                :class="[
                  'flex-1 h-1 mx-2',
                  currentStep > step ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
                ]"
              ></div>
            </div>
          </div>
        </div>

        <!-- Content -->
        <div class="px-6 py-6">
          <!-- Step 1: Plan Selection -->
          <div v-if="currentStep === 1">
            <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              {{ t('app.subscription.renewal.step1_title') }}
            </h4>
            
            <div class="space-y-4">
              <!-- Plan Selection -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {{ t('app.subscription.renewal.select_plan') }}
                </label>
                <select 
                  v-model="selectedPlanId" 
                  class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option :value="null">{{ t('app.subscription.renewal.select_plan_placeholder') }}</option>
                  <option v-for="plan in availablePlans" :key="plan.id" :value="plan.id">
                    {{ plan.display_name }} - ${{ plan.monthly_price }}/mes
                  </option>
                </select>
              </div>

              <!-- Billing Cycle -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {{ t('app.subscription.renewal.billing_cycle') }}
                </label>
                <div class="flex gap-4">
                  <label class="flex items-center">
                    <input 
                      type="radio" 
                      v-model="billingCycle" 
                      value="monthly"
                      class="mr-2"
                    />
                    <span class="text-gray-900 dark:text-white">{{ t('app.subscription.renewal.monthly') }}</span>
                  </label>
                  <label class="flex items-center">
                    <input 
                      type="radio" 
                      v-model="billingCycle" 
                      value="annual"
                      class="mr-2"
                    />
                    <span class="text-gray-900 dark:text-white">
                      {{ t('app.subscription.renewal.annual') }}
                      <span class="text-xs text-green-600 dark:text-green-400 ml-1">({{ t('app.subscription.renewal.discount') }})</span>
                    </span>
                  </label>
                </div>
              </div>

              <!-- Price Summary -->
              <div v-if="selectedPlan" class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div class="flex justify-between items-center">
                  <span class="text-gray-700 dark:text-gray-300">{{ t('app.subscription.price') }}:</span>
                  <span class="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    ${{ calculatedPrice }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 2: Payment Instructions -->
          <div v-if="currentStep === 2">
            <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              {{ t('app.subscription.renewal.step2_title') }}
            </h4>

            <div class="space-y-4">
              <!-- Reference Number -->
              <div class="p-4 bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-400 rounded">
                <p class="text-sm font-semibold text-yellow-800 dark:text-yellow-300 mb-2">
                  {{ t('app.subscription.renewal.important') }}
                </p>
                <p class="text-sm text-yellow-700 dark:text-yellow-400">
                  {{ t('app.subscription.renewal.include_reference') }}
                </p>
              </div>

              <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {{ t('app.subscription.renewal.reference_number') }}
                </label>
                <div class="flex items-center gap-2">
                  <input 
                    :value="paymentData?.reference_number" 
                    readonly
                    class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white font-mono text-lg"
                  />
                  <button 
                    @click="copyReference"
                    class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    {{ t('app.subscription.renewal.copy_reference') }}
                  </button>
                </div>
              </div>

              <!-- Bank Details -->
              <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <h5 class="font-semibold text-gray-900 dark:text-white mb-3">
                  {{ t('app.subscription.renewal.bank_details') }}
                </h5>
                <div class="space-y-2 text-sm">
                  <div class="flex justify-between">
                    <span class="text-gray-600 dark:text-gray-400">{{ t('app.subscription.renewal.bank') }}:</span>
                    <span class="font-semibold text-gray-900 dark:text-white">{{ paymentData?.bank_details.bank }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600 dark:text-gray-400">{{ t('app.subscription.renewal.account') }}:</span>
                    <span class="font-semibold text-gray-900 dark:text-white">{{ paymentData?.bank_details.account }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600 dark:text-gray-400">{{ t('app.subscription.renewal.clabe') }}:</span>
                    <span class="font-semibold text-gray-900 dark:text-white">{{ paymentData?.bank_details.clabe }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-600 dark:text-gray-400">{{ t('app.subscription.renewal.beneficiary') }}:</span>
                    <span class="font-semibold text-gray-900 dark:text-white">{{ paymentData?.bank_details.beneficiary }}</span>
                  </div>
                </div>
              </div>

              <!-- Amount -->
              <div class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <div class="flex justify-between items-center">
                  <span class="text-gray-700 dark:text-gray-300">{{ t('app.subscription.price') }}:</span>
                  <span class="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    ${{ paymentData?.amount }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 3: Upload Proof -->
          <div v-if="currentStep === 3">
            <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              {{ t('app.subscription.renewal.step3_title') }}
            </h4>

            <div class="space-y-4">
              <!-- Payment Date -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {{ t('app.subscription.renewal.payment_date') }}
                </label>
                <input 
                  type="datetime-local" 
                  v-model="paymentDate"
                  class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>

              <!-- Proof Image URL -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {{ t('app.subscription.renewal.proof_image') }}
                </label>
                <input 
                  type="url" 
                  v-model="proofImageUrl"
                  placeholder="https://..."
                  class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
                <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  URL de la imagen del comprobante (opcional)
                </p>
              </div>

              <!-- Notes -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  {{ t('app.subscription.renewal.notes') }}
                </label>
                <textarea 
                  v-model="notes"
                  rows="3"
                  :placeholder="t('app.subscription.renewal.notes_placeholder')"
                  class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                ></textarea>
              </div>
            </div>
          </div>

          <!-- Step 4: Confirmation -->
          <div v-if="currentStep === 4">
            <div class="text-center py-8">
              <div class="w-16 h-16 bg-green-100 dark:bg-green-900/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircleIcon class="w-8 h-8 text-green-600 dark:text-green-400" />
              </div>
              <h4 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                {{ t('app.subscription.renewal.payment_submitted') }}
              </h4>
              <p class="text-gray-600 dark:text-gray-400 mb-1">
                {{ t('app.subscription.renewal.pending_approval') }}
              </p>
              <p class="text-sm text-gray-500 dark:text-gray-500">
                {{ t('app.subscription.renewal.estimated_time') }}
              </p>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="px-6 py-4 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700">
          <div class="flex justify-between">
            <button 
              v-if="currentStep > 1 && currentStep < 4"
              @click="previousStep"
              class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
            >
              {{ t('app.common.back') }}
            </button>
            <div v-else></div>

            <div class="flex gap-2">
              <button 
                v-if="currentStep < 4"
                @click="close"
                class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
              >
                {{ t('app.common.cancel') }}
              </button>

              <button 
                v-if="currentStep === 1"
                @click="requestRenewal"
                :disabled="!selectedPlanId || loading"
                class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ loading ? t('app.common.loading') : t('app.subscription.renewal.continue') }}
              </button>

              <button 
                v-if="currentStep === 2"
                @click="nextStep"
                class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                {{ t('app.subscription.renewal.already_paid') }}
              </button>

              <button 
                v-if="currentStep === 3"
                @click="submitProof"
                :disabled="!paymentDate || loading"
                class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ loading ? t('app.common.loading') : t('app.subscription.renewal.submit_proof') }}
              </button>

              <button 
                v-if="currentStep === 4"
                @click="close"
                class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                {{ t('app.subscription.renewal.close') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { XMarkIcon, CheckCircleIcon } from '@heroicons/vue/24/outline'
import { paymentService, type RenewalResponse } from '@/services/paymentService'
import { useToast } from '@/composables/useToast'

const { t } = useI18n()
const { showSuccess, showError } = useToast()

interface Props {
  isOpen: boolean
  availablePlans: any[]
}

const props = defineProps<Props>()
const emit = defineEmits(['close', 'success'])

const currentStep = ref(1)
const loading = ref(false)

// Step 1 data
const selectedPlanId = ref<number | null>(null)
const billingCycle = ref<'monthly' | 'annual'>('monthly')

// Step 2 data
const paymentData = ref<RenewalResponse | null>(null)

// Step 3 data
const paymentDate = ref('')
const proofImageUrl = ref('')
const notes = ref('')

const selectedPlan = computed(() => {
  return props.availablePlans.find(p => p.id === selectedPlanId.value)
})

const calculatedPrice = computed(() => {
  if (!selectedPlan.value) return 0
  return billingCycle.value === 'monthly' 
    ? selectedPlan.value.monthly_price 
    : selectedPlan.value.annual_price
})

const close = () => {
  emit('close')
  resetForm()
}

const resetForm = () => {
  currentStep.value = 1
  selectedPlanId.value = null
  billingCycle.value = 'monthly'
  paymentData.value = null
  paymentDate.value = ''
  proofImageUrl.value = ''
  notes.value = ''
}

const nextStep = () => {
  currentStep.value++
}

const previousStep = () => {
  currentStep.value--
}

const requestRenewal = async () => {
  if (!selectedPlanId.value) return

  loading.value = true
  try {
    const response = await paymentService.requestRenewal({
      plan_id: selectedPlanId.value,
      billing_cycle: billingCycle.value
    })

    paymentData.value = response
    showSuccess('Solicitud de renovación creada')
    nextStep()
  } catch (error: any) {
    showError(error.response?.data?.detail || 'Error al solicitar renovación')
  } finally {
    loading.value = false
  }
}

const copyReference = () => {
  if (paymentData.value?.reference_number) {
    navigator.clipboard.writeText(paymentData.value.reference_number)
    showSuccess('Número de referencia copiado')
  }
}

const submitProof = async () => {
  if (!paymentData.value || !paymentDate.value) return

  loading.value = true
  try {
    await paymentService.submitPayment(paymentData.value.payment_id, {
      reference_number: paymentData.value.reference_number,
      payment_date: paymentDate.value,
      proof_image_url: proofImageUrl.value || undefined,
      notes: notes.value || undefined
    })

    showSuccess('Comprobante enviado para revisión')
    nextStep()
    emit('success')
  } catch (error: any) {
    showError(error.response?.data?.detail || 'Error al enviar comprobante')
  } finally {
    loading.value = false
  }
}
</script>
