<template>
  <TransitionRoot :show="isOpen" as="template">
    <Dialog as="div" class="relative z-50" @close="closeModal">
      <TransitionChild
        as="template"
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black bg-opacity-25" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <TransitionChild
            as="template"
            enter="ease-out duration-300"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="ease-in duration-200"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel class="w-full max-w-4xl transform overflow-hidden rounded-2xl bg-white dark:bg-gray-800 p-6 shadow-xl transition-all">
              <DialogTitle class="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                {{ t('app.subscription.choose_plan') }}
              </DialogTitle>

              <!-- Loading State -->
              <div v-if="loading" class="flex justify-center py-12">
                <ArrowPathIcon class="h-12 w-12 animate-spin text-indigo-600" />
              </div>

              <!-- Plans Grid -->
              <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div
                  v-for="plan in plans"
                  :key="plan.id"
                  :class="[
                    'relative rounded-lg border-2 p-6 cursor-pointer transition-all',
                    selectedPlanId === plan.id
                      ? 'border-indigo-600 bg-indigo-50 dark:bg-indigo-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-indigo-300'
                  ]"
                  @click="selectedPlanId = plan.id"
                >
                  <!-- Current Plan Badge -->
                  <div v-if="plan.id === currentPlanId" class="absolute -top-2 -right-2">
                    <span class="bg-green-600 text-white text-xs font-semibold px-3 py-1 rounded-full shadow-lg">
                      {{ t('app.subscription.current_plan') }}
                    </span>
                  </div>
                  
                  <!-- Popular Badge (only if not current plan) -->
                  <div v-else-if="plan.is_popular" class="absolute -top-2 -right-2">
                    <span class="bg-indigo-600 text-white text-xs font-semibold px-3 py-1 rounded-full shadow-lg">
                      {{ t('app.subscription.popular') }}
                    </span>
                  </div>

                  <!-- Plan Name -->
                  <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">
                    {{ plan.name }}
                  </h3>

                  <!-- Plan Description -->
                  <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    {{ plan.description }}
                  </p>

                  <!-- Price -->
                  <div class="mb-4">
                    <div class="flex items-baseline gap-2">
                      <span class="text-3xl font-bold text-gray-900 dark:text-white">
                        ${{ formatMoney(billingCycle === 'monthly' ? plan.monthly_price : plan.annual_price) }}
                      </span>
                      <span class="text-gray-500 dark:text-gray-400">
                        /{{ t(`app.subscription.${billingCycle}`) }}
                      </span>
                    </div>
                    <div v-if="billingCycle === 'annual' && plan.annual_price" class="text-sm text-green-600 dark:text-green-400 mt-1">
                      {{ t('app.subscription.save') }} ${{ formatMoney((plan.monthly_price * 12) - plan.annual_price) }}/{{ t('app.subscription.year') }}
                    </div>
                  </div>

                  <!-- Limits -->
                  <div class="space-y-2 mb-4">
                    <div class="flex items-center text-sm">
                      <CheckIcon class="h-4 w-4 text-green-500 mr-2" />
                      <span class="text-gray-700 dark:text-gray-300">
                        {{ plan.limits.max_tables === -1 ? t('app.subscription.unlimited') : plan.limits.max_tables }} {{ t('app.subscription.tables') }}
                      </span>
                    </div>
                    <div class="flex items-center text-sm">
                      <CheckIcon class="h-4 w-4 text-green-500 mr-2" />
                      <span class="text-gray-700 dark:text-gray-300">
                        {{ plan.limits.max_menu_items === -1 ? t('app.subscription.unlimited') : plan.limits.max_menu_items }} {{ t('app.subscription.menu_items') }}
                      </span>
                    </div>
                    <div class="flex items-center text-sm">
                      <CheckIcon class="h-4 w-4 text-green-500 mr-2" />
                      <span class="text-gray-700 dark:text-gray-300">
                        {{ plan.limits.max_admin_users === -1 ? t('app.subscription.unlimited') : plan.limits.max_admin_users }} {{ t('app.subscription.admin_users') }}
                      </span>
                    </div>
                    
                    <!-- Staff Sub-roles -->
                    <div v-if="plan.limits.max_waiter_users" class="flex items-center text-sm">
                      <CheckIcon class="h-4 w-4 text-green-500 mr-2" />
                      <span class="text-gray-700 dark:text-gray-300">
                        {{ plan.limits.max_waiter_users === -1 ? t('app.subscription.unlimited') : plan.limits.max_waiter_users }} {{ t('app.subscription.waiter_users') }}
                      </span>
                    </div>
                    <div v-if="plan.limits.max_cashier_users" class="flex items-center text-sm">
                      <CheckIcon class="h-4 w-4 text-green-500 mr-2" />
                      <span class="text-gray-700 dark:text-gray-300">
                        {{ plan.limits.max_cashier_users === -1 ? t('app.subscription.unlimited') : plan.limits.max_cashier_users }} {{ t('app.subscription.cashier_users') }}
                      </span>
                    </div>
                    <div v-if="plan.limits.max_kitchen_users" class="flex items-center text-sm">
                      <CheckIcon class="h-4 w-4 text-green-500 mr-2" />
                      <span class="text-gray-700 dark:text-gray-300">
                        {{ plan.limits.max_kitchen_users === -1 ? t('app.subscription.unlimited') : plan.limits.max_kitchen_users }} {{ t('app.subscription.kitchen_users') }}
                      </span>
                    </div>
                  </div>

                  <!-- Features -->
                  <div class="space-y-1 text-xs">
                    <div v-if="plan.features.has_kitchen_module" class="flex items-center text-gray-600 dark:text-gray-400">
                      <CheckIcon class="h-3 w-3 mr-1" />
                      {{ t('app.subscription.kitchen_module') }}
                    </div>
                    <div v-if="plan.features.has_ingredients_module" class="flex items-center text-gray-600 dark:text-gray-400">
                      <CheckIcon class="h-3 w-3 mr-1" />
                      {{ t('app.subscription.ingredients_module') }}
                    </div>
                    <div v-if="plan.features.has_advanced_reports" class="flex items-center text-gray-600 dark:text-gray-400">
                      <CheckIcon class="h-3 w-3 mr-1" />
                      {{ t('app.subscription.advanced_reports') }}
                    </div>
                  </div>

                  <!-- Selected Indicator -->
                  <div v-if="selectedPlanId === plan.id" class="absolute top-4 right-4">
                    <CheckCircleIcon class="h-6 w-6 text-indigo-600" />
                  </div>
                </div>
              </div>

              <!-- Billing Cycle Toggle -->
              <div class="mt-6 flex justify-center">
                <div class="inline-flex rounded-lg border border-gray-300 dark:border-gray-600 p-1">
                  <button
                    @click="billingCycle = 'monthly'"
                    :class="[
                      'px-4 py-2 rounded-md text-sm font-medium transition-colors',
                      billingCycle === 'monthly'
                        ? 'bg-indigo-600 text-white'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                    ]"
                  >
                    {{ t('app.subscription.monthly') }}
                  </button>
                  <button
                    @click="billingCycle = 'annual'"
                    :class="[
                      'px-4 py-2 rounded-md text-sm font-medium transition-colors',
                      billingCycle === 'annual'
                        ? 'bg-indigo-600 text-white'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                    ]"
                  >
                    {{ t('app.subscription.annual') }}
                    <span class="ml-1 text-xs">({{ t('app.subscription.save_label') }})</span>
                  </button>
                </div>
              </div>

              <!-- Actions -->
              <div class="mt-6 flex justify-end gap-3">
                <button
                  @click="closeModal"
                  class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  {{ t('app.common.cancel') }}
                </button>
                <button
                  @click="confirmUpgrade"
                  :disabled="!selectedPlanId || submitting"
                  class="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                >
                  <ArrowPathIcon v-if="submitting" class="h-4 w-4 animate-spin" />
                  {{ t('app.subscription.confirm_upgrade') }}
                </button>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  TransitionRoot,
  TransitionChild,
} from '@headlessui/vue';
import { ArrowPathIcon, CheckIcon, CheckCircleIcon } from '@heroicons/vue/24/outline';
import { subscriptionService } from '@/services/subscriptionService';
import { useToast, POSITION } from 'vue-toastification';

const { t } = useI18n();
const toast = useToast();

const props = defineProps<{
  isOpen: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'upgraded'): void;
  (e: 'requiresPayment', data: { planId: number, billingCycle: string }): void;
}>();

// State
const loading = ref(false);
const submitting = ref(false);
const plans = ref<any[]>([]);
const selectedPlanId = ref<number | null>(null);
const billingCycle = ref<'monthly' | 'annual'>('monthly');
const currentPlanId = ref<number | null>(null);

// Methods
const loadPlans = async () => {
  loading.value = true;
  try {
    plans.value = await subscriptionService.getPlans();
    
    // Load current subscription to highlight current plan
    try {
      const subscription = await subscriptionService.getMySubscription();
      if (subscription.has_subscription && subscription.subscription?.plan?.id) {
        currentPlanId.value = subscription.subscription.plan.id;
        // Set current plan as selected by default
        selectedPlanId.value = currentPlanId.value;
      }
    } catch (error) {
      console.error('Error loading current subscription:', error);
    }
  } catch (error) {
    console.error('Error loading plans:', error);
  } finally {
    loading.value = false;
  }
};

const formatMoney = (amount: number) => {
  return amount.toLocaleString('es-MX', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};

const closeModal = () => {
  emit('close');
};

const confirmUpgrade = async () => {
  if (!selectedPlanId.value) return;
  
  submitting.value = true;
  try {
    await subscriptionService.upgradePlan(selectedPlanId.value, billingCycle.value);
    
    toast.success('Plan actualizado exitosamente', {
      position: POSITION.TOP_RIGHT,
      timeout: 3000
    });
    
    emit('upgraded');
    closeModal();
  } catch (error: any) {
    console.error('Error upgrading plan:', error);
    
    // Handle 402 Payment Required (expired subscription - needs manual payment)
    if (error.response?.status === 402) {
      const detail = error.response?.data?.detail;
      const message = typeof detail === 'object' ? detail.message : detail;
      
      toast.info(message || 'Tu suscripción ha expirado. Serás redirigido al proceso de pago.', {
        position: POSITION.TOP_RIGHT,
        timeout: 5000
      });
      
      // Emit event with plan data so parent can open renewal modal
      emit('requiresPayment', {
        planId: selectedPlanId.value!,
        billingCycle: billingCycle.value
      });
      
      closeModal();
      return;
    }
    
    const errorMessage = error.response?.data?.detail || 'Error al actualizar el plan. Por favor intenta de nuevo.';
    
    // Show error with proper formatting for multiline messages
    toast.error(errorMessage, {
      position: POSITION.TOP_RIGHT,
      timeout: 8000,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true
    });
  } finally {
    submitting.value = false;
  }
};

// Lifecycle
watch(() => props.isOpen, (newValue) => {
  if (newValue) {
    loadPlans();
  }
});

onMounted(() => {
  if (props.isOpen) {
    loadPlans();
  }
});
</script>
