<template>
  <div
    v-if="show"
    class="fixed inset-0 z-[10001] overflow-y-auto"
    @click.self="$emit('close')"
  >
    <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75 dark:bg-gray-900 dark:bg-opacity-75"></div>

      <!-- Modal panel -->
      <div class="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
        <!-- Header -->
        <div class="bg-white dark:bg-gray-800 px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white">
              {{ hasSubscription ? t('app.sysadmin.modal.manage_title') : t('app.sysadmin.modal.assign_title') }}
            </h3>
            <button
              @click="$emit('close')"
              class="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
            >
              <XMarkIcon class="h-6 w-6" />
            </button>
          </div>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {{ restaurant.name }} ({{ restaurant.subdomain }})
          </p>
        </div>

        <!-- Content -->
        <div class="bg-white dark:bg-gray-800 px-6 py-4 max-h-[70vh] overflow-y-auto">
          <!-- Admin Users Section -->
          <div class="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-sm font-medium text-gray-900 dark:text-white">
                {{ t('app.sysadmin.modal.admin_users') }}
              </h4>
              <button
                v-if="!hasAdmins"
                @click="showCreateAdminForm = true"
                class="text-sm text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300 font-medium"
              >
                {{ t('app.sysadmin.modal.create_admin') }}
              </button>
            </div>
            
            <!-- Loading -->
            <div v-if="loadingAdmins" class="text-sm text-gray-500 dark:text-gray-400">
              {{ t('app.common.loading') }}
            </div>
            
            <!-- No admins -->
            <div v-else-if="!hasAdmins && !showCreateAdminForm" class="text-sm text-amber-700 dark:text-amber-400">
              ⚠️ {{ t('app.sysadmin.modal.no_admin_warning') }}
            </div>
            
            <!-- Admin list -->
            <div v-else-if="hasAdmins && !showCreateAdminForm" class="space-y-2">
              <div
                v-for="admin in admins"
                :key="admin.id"
                class="flex items-center justify-between p-3 bg-white dark:bg-gray-700 rounded-lg"
              >
                <div>
                  <div class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ admin.full_name }}
                  </div>
                  <div class="text-xs text-gray-500 dark:text-gray-400">
                    {{ admin.email }}
                  </div>
                </div>
                <span class="text-xs px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded-full">
                  Admin
                </span>
              </div>
              <button
                @click="showCreateAdminForm = true"
                class="w-full text-sm text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300 font-medium py-2"
              >
                + {{ t('app.sysadmin.modal.add_another_admin') }}
              </button>
            </div>
            
            <!-- Create admin form -->
            <div v-if="showCreateAdminForm" class="space-y-3">
              <div>
                <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {{ t('app.sysadmin.create_admin.full_name') }} *
                </label>
                <input
                  v-model="adminForm.full_name"
                  type="text"
                  required
                  class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                  :placeholder="t('app.sysadmin.create_admin.full_name_placeholder')"
                />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {{ t('app.sysadmin.create_admin.email') }} *
                </label>
                <input
                  v-model="adminForm.email"
                  type="email"
                  required
                  class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                  :placeholder="t('app.sysadmin.create_admin.email_placeholder')"
                />
              </div>
              <div>
                <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {{ t('app.sysadmin.create_admin.password') }} *
                </label>
                <input
                  v-model="adminForm.password"
                  type="password"
                  required
                  minlength="8"
                  class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                  :placeholder="t('app.sysadmin.create_admin.password_placeholder')"
                />
                <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  {{ t('app.sysadmin.create_admin.password_requirements') }}
                </p>
              </div>
              <div class="flex gap-2">
                <button
                  @click="cancelCreateAdmin"
                  type="button"
                  class="flex-1 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  {{ t('app.common.cancel') }}
                </button>
                <button
                  @click="handleCreateAdmin"
                  :disabled="creatingAdmin"
                  class="flex-1 px-3 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                >
                  {{ creatingAdmin ? t('app.common.loading') : t('app.sysadmin.create_admin.submit') }}
                </button>
              </div>
            </div>
          </div>

          <!-- Current Subscription Info (if exists) -->
          <div v-if="hasSubscription && subscriptionDetails" class="mb-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-3">
              {{ t('app.sysadmin.modal.current_subscription') }}
            </h4>
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span class="text-gray-500 dark:text-gray-400">{{ t('app.sysadmin.modal.plan') }}:</span>
                <span class="ml-2 font-medium text-gray-900 dark:text-white">{{ restaurant.plan_name }}</span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">{{ t('app.sysadmin.modal.status') }}:</span>
                <span
                  :class="getStatusClass(restaurant.subscription_status)"
                  class="ml-2 px-2 py-1 text-xs font-semibold rounded-full"
                >
                  {{ t(`app.sysadmin.status.${restaurant.subscription_status}`) }}
                </span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">{{ t('app.sysadmin.modal.price') }}:</span>
                <span class="ml-2 font-medium text-gray-900 dark:text-white">${{ restaurant.monthly_price }}/{{ t('app.common.month') }}</span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">{{ t('app.sysadmin.modal.renewal') }}:</span>
                <span class="ml-2 font-medium text-gray-900 dark:text-white">{{ restaurant.days_until_renewal }} {{ t('app.common.days') }}</span>
              </div>
            </div>
          </div>

          <!-- Select Plan -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ hasSubscription ? t('app.sysadmin.modal.change_plan') : t('app.sysadmin.modal.select_plan') }}
            </label>
            <select
              v-model.number="selectedPlanId"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
            >
              <option :value="null">{{ t('app.sysadmin.modal.select_plan_placeholder') }}</option>
              <option v-for="plan in plans" :key="plan.id" :value="plan.id">
                {{ plan.display_name }} - ${{ plan.monthly_price }}/{{ t('app.common.month') }}
              </option>
            </select>
          </div>

          <!-- Plan Details (if selected) -->
          <div v-if="selectedPlan" class="mb-6 p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
            <h4 class="text-sm font-medium text-gray-900 dark:text-white mb-3">
              {{ selectedPlan.display_name }}
            </h4>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
              {{ selectedPlan.description }}
            </p>
            
            <div class="grid grid-cols-2 gap-4 text-sm mb-4">
              <div>
                <span class="text-gray-500 dark:text-gray-400">{{ t('app.sysadmin.modal.limits.users') }}:</span>
                <span class="ml-2 text-gray-900 dark:text-white">
                  {{ (selectedPlan.limits?.max_admin_users || 0) + (selectedPlan.limits?.max_waiter_users || 0) + (selectedPlan.limits?.max_cashier_users || 0) + (selectedPlan.limits?.max_kitchen_users || 0) }}
                </span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">{{ t('app.sysadmin.modal.limits.tables') }}:</span>
                <span class="ml-2 text-gray-900 dark:text-white">{{ selectedPlan.limits?.max_tables || '-' }}</span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">{{ t('app.sysadmin.modal.limits.products') }}:</span>
                <span class="ml-2 text-gray-900 dark:text-white">{{ selectedPlan.limits?.max_menu_items || '-' }}</span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">{{ t('app.sysadmin.modal.price') }}:</span>
                <span class="ml-2 font-bold text-indigo-600 dark:text-indigo-400">${{ selectedPlan.monthly_price || 0 }}/{{ t('app.common.month') }}</span>
              </div>
            </div>

            <div class="flex flex-wrap gap-2">
              <span v-if="selectedPlan.features?.has_kitchen_module" class="px-2 py-1 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded">
                {{ t('app.sysadmin.modal.features.kitchen') }}
              </span>
              <span v-if="selectedPlan.features?.has_ingredients_module" class="px-2 py-1 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded">
                {{ t('app.sysadmin.modal.features.ingredients') }}
              </span>
              <span v-if="selectedPlan.features?.has_inventory_module" class="px-2 py-1 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded">
                {{ t('app.sysadmin.modal.features.inventory') }}
              </span>
              <span v-if="selectedPlan.features?.has_advanced_reports" class="px-2 py-1 text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded">
                {{ t('app.sysadmin.modal.features.reports') }}
              </span>
            </div>
          </div>

          <!-- Billing Cycle (only for new subscriptions) -->
          <div v-if="!hasSubscription" class="mb-6">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ t('app.sysadmin.modal.billing_cycle') }}
            </label>
            <div class="flex gap-4">
              <label class="flex items-center">
                <input
                  v-model="billingCycle"
                  type="radio"
                  value="monthly"
                  class="mr-2"
                />
                <span class="text-sm text-gray-900 dark:text-white">{{ t('app.sysadmin.modal.monthly') }}</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="billingCycle"
                  type="radio"
                  value="annual"
                  class="mr-2"
                />
                <span class="text-sm text-gray-900 dark:text-white">{{ t('app.sysadmin.modal.annual') }} (25% {{ t('app.sysadmin.modal.discount') }})</span>
              </label>
            </div>
          </div>

          <!-- Cancel Subscription (if exists) -->
          <div v-if="hasSubscription && restaurant.subscription_status !== 'cancelled'" class="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <h4 class="text-sm font-medium text-red-900 dark:text-red-200 mb-2">
              {{ t('app.sysadmin.modal.cancel_subscription') }}
            </h4>
            <p class="text-sm text-red-700 dark:text-red-300 mb-3">
              {{ t('app.sysadmin.modal.cancel_warning') }}
            </p>
            <div class="flex gap-2">
              <button
                @click="cancelSubscription(false)"
                :disabled="loading"
                class="px-4 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50"
              >
                {{ t('app.sysadmin.modal.cancel_at_period_end') }}
              </button>
              <button
                @click="cancelSubscription(true)"
                :disabled="loading"
                class="px-4 py-2 text-sm bg-red-800 text-white rounded-lg hover:bg-red-900 disabled:opacity-50"
              >
                {{ t('app.sysadmin.modal.cancel_immediately') }}
              </button>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="bg-gray-50 dark:bg-gray-700 px-6 py-4 flex justify-end gap-3">
          <button
            @click="$emit('close')"
            :disabled="loading"
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-500 disabled:opacity-50"
          >
            {{ t('app.common.cancel') }}
          </button>
          <button
            v-if="selectedPlanId"
            @click="saveSubscription"
            :disabled="loading"
            class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-2"
          >
            <ArrowPathIcon v-if="loading" class="h-4 w-4 animate-spin" />
            {{ hasSubscription ? t('app.sysadmin.modal.change_plan_button') : t('app.sysadmin.modal.assign_plan_button') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { XMarkIcon, ArrowPathIcon } from '@heroicons/vue/24/outline';
import { adminService } from '@/services/adminService';
import { subscriptionService } from '@/services/subscriptionService';

const { t } = useI18n();

const props = defineProps<{
  show: boolean;
  restaurant: any;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'updated'): void;
}>();

// State
const loading = ref(false);
const plans = ref<any[]>([]);
const selectedPlanId = ref<number | null>(null);
const billingCycle = ref<'monthly' | 'annual'>('monthly');
const subscriptionDetails = ref<any>(null);

// Admin users state
const loadingAdmins = ref(false);
const admins = ref<any[]>([]);
const showCreateAdminForm = ref(false);
const creatingAdmin = ref(false);
const adminForm = ref({
  full_name: '',
  email: '',
  password: ''
});

// Computed
const hasSubscription = computed(() => !!props.restaurant.subscription_id);
const selectedPlan = computed(() => plans.value?.find(p => p.id === selectedPlanId.value));
const hasAdmins = computed(() => admins.value.length > 0);

// Methods
const loadPlans = async () => {
  try {
    plans.value = await subscriptionService.getPlans();
    if (import.meta.env.DEV) {
      console.log('Plans loaded:', plans.value);
    }
  } catch (error) {
    console.error('Error loading plans:', error);
  }
};

const loadSubscriptionDetails = async () => {
  if (!hasSubscription.value) return;
  
  try {
    subscriptionDetails.value = await adminService.getRestaurantSubscription(props.restaurant.id);
  } catch (error) {
    console.error('Error loading subscription details:', error);
  }
};

const loadAdmins = async () => {
  loadingAdmins.value = true;
  try {
    const response = await adminService.getRestaurantAdmins(props.restaurant.id);
    admins.value = response.admins || [];
  } catch (error) {
    console.error('Error loading admins:', error);
    admins.value = [];
  } finally {
    loadingAdmins.value = false;
  }
};

const handleCreateAdmin = async () => {
  if (!adminForm.value.full_name || !adminForm.value.email || !adminForm.value.password) {
    alert('Por favor completa todos los campos');
    return;
  }
  
  creatingAdmin.value = true;
  try {
    await adminService.createRestaurantAdmin(props.restaurant.id, adminForm.value);
    
    // Reload admins list
    await loadAdmins();
    
    // Reset form
    adminForm.value = {
      full_name: '',
      email: '',
      password: ''
    };
    showCreateAdminForm.value = false;
    
    alert('Admin creado exitosamente');
  } catch (error: any) {
    console.error('Error creating admin:', error);
    
    // Handle validation errors
    if (error.response?.data?.error?.validation_errors) {
      const validationErrors = error.response.data.error.validation_errors;
      const errorMessages = validationErrors.map((err: any) => err.message).join('\n');
      alert(`Error de validación:\n${errorMessages}`);
    } else {
      alert(error.response?.data?.error?.message || error.response?.data?.detail || 'Error al crear el admin');
    }
  } finally {
    creatingAdmin.value = false;
  }
};

const cancelCreateAdmin = () => {
  adminForm.value = {
    full_name: '',
    email: '',
    password: ''
  };
  showCreateAdminForm.value = false;
};

const saveSubscription = async () => {
  if (!selectedPlanId.value) return;
  
  loading.value = true;
  try {
    if (hasSubscription.value) {
      // Upgrade/change plan
      await adminService.upgradeSubscription(props.restaurant.id, {
        new_plan_id: selectedPlanId.value
      });
    } else {
      // Create new subscription
      await adminService.createSubscription(props.restaurant.id, {
        plan_id: selectedPlanId.value,
        billing_cycle: billingCycle.value
      });
    }
    
    emit('updated');
  } catch (error: any) {
    console.error('Error saving subscription:', error);
    alert(error.response?.data?.detail || 'Error saving subscription');
  } finally {
    loading.value = false;
  }
};

const cancelSubscription = async (immediate: boolean) => {
  const confirmMsg = immediate
    ? t('app.sysadmin.modal.confirm_cancel_immediate')
    : t('app.sysadmin.modal.confirm_cancel_period_end');
  
  if (!confirm(confirmMsg)) return;
  
  loading.value = true;
  try {
    await adminService.cancelSubscription(props.restaurant.id, immediate);
    emit('updated');
  } catch (error: any) {
    console.error('Error cancelling subscription:', error);
    alert(error.response?.data?.detail || 'Error cancelling subscription');
  } finally {
    loading.value = false;
  }
};

const getStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    'trial': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'active': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'past_due': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    'cancelled': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    'expired': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
  };
  return classes[status] || 'bg-gray-100 text-gray-800';
};

// Watchers
watch(selectedPlanId, (newId) => {
  if (import.meta.env.DEV) {
    console.log('Selected plan ID changed:', newId);
    console.log('Selected plan object:', selectedPlan.value);
  }
});

// Lifecycle
onMounted(async () => {
  await loadPlans();
  await loadSubscriptionDetails();
  await loadAdmins();
  
  // Pre-select current plan if exists
  if (hasSubscription.value && props.restaurant.plan_id) {
    selectedPlanId.value = props.restaurant.plan_id;
  }
});
</script>
