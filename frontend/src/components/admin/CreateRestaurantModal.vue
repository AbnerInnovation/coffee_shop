<template>
  <TransitionRoot appear :show="show" as="template">
    <Dialog as="div" @close="emit('close')" class="relative z-50">
      <TransitionChild
        as="template"
        enter="duration-300 ease-out"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="duration-200 ease-in"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black bg-opacity-25" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 text-center">
          <TransitionChild
            as="template"
            enter="duration-300 ease-out"
            enter-from="opacity-0 scale-95"
            enter-to="opacity-100 scale-100"
            leave="duration-200 ease-in"
            leave-from="opacity-100 scale-100"
            leave-to="opacity-0 scale-95"
          >
            <DialogPanel class="w-full max-w-2xl transform overflow-hidden rounded-2xl bg-white dark:bg-gray-800 p-6 text-left align-middle shadow-xl transition-all">
              <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900 dark:text-white mb-4">
                {{ createdRestaurant ? t('app.sysadmin.create_restaurant.success_title') : t('app.sysadmin.create_restaurant.title') }}
              </DialogTitle>

              <!-- Success Message with Subdomain Link -->
              <div v-if="createdRestaurant" class="space-y-4">
                <div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                  <div class="flex items-start gap-3">
                    <svg class="h-6 w-6 text-green-600 dark:text-green-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div class="flex-1">
                      <p class="text-sm font-medium text-green-900 dark:text-green-200">
                        {{ t('app.sysadmin.create_restaurant.created_successfully') }}
                      </p>
                      <p class="text-sm text-green-700 dark:text-green-300 mt-1">
                        {{ t('app.sysadmin.create_restaurant.restaurant_name') }}: <strong>{{ createdRestaurant.name }}</strong>
                      </p>
                    </div>
                  </div>
                </div>

                <!-- Subdomain Link -->
                <div class="bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800 rounded-lg p-4">
                  <label class="block text-sm font-medium text-indigo-900 dark:text-indigo-200 mb-2">
                    {{ t('app.sysadmin.create_restaurant.subdomain_link') }}
                  </label>
                  <div class="flex items-center gap-2">
                    <input
                      :value="getSubdomainUrl()"
                      readonly
                      class="flex-1 px-4 py-2 bg-white dark:bg-gray-700 border border-indigo-300 dark:border-indigo-600 rounded-lg text-sm text-gray-900 dark:text-white font-mono"
                    />
                    <button
                      type="button"
                      @click="copyToClipboard(getSubdomainUrl())"
                      class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium"
                    >
                      {{ t('app.common.copy') }}
                    </button>
                  </div>
                  <p class="mt-2 text-xs text-indigo-700 dark:text-indigo-300">
                    {{ t('app.sysadmin.create_restaurant.subdomain_link_hint') }}
                  </p>
                </div>

                <!-- Trial Info -->
                <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <p class="text-sm text-blue-900 dark:text-blue-200">
                    <strong>{{ t('app.sysadmin.create_restaurant.trial_created') }}:</strong> {{ form.trial_days }} {{ t('app.common.days') }}
                  </p>
                  <p class="text-xs text-blue-700 dark:text-blue-300 mt-1">
                    {{ t('app.sysadmin.create_restaurant.admin_credentials_console') }}
                  </p>
                </div>

                <!-- Close Button -->
                <div class="flex justify-end pt-4 border-t border-gray-200 dark:border-gray-700">
                  <button
                    type="button"
                    @click="handleClose"
                    class="px-6 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700"
                  >
                    {{ t('app.common.close') }}
                  </button>
                </div>
              </div>

              <!-- Creation Form -->
              <form v-else @submit.prevent="handleSubmit" class="space-y-4">
                <!-- Name -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {{ t('app.sysadmin.create_restaurant.name') }} *
                  </label>
                  <input
                    v-model="form.name"
                    type="text"
                    required
                    class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                    :placeholder="t('app.sysadmin.create_restaurant.name_placeholder')"
                  />
                </div>

                <!-- Subdomain -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {{ t('app.sysadmin.create_restaurant.subdomain') }} *
                  </label>
                  <div class="flex items-center gap-2">
                    <input
                      v-model="form.subdomain"
                      type="text"
                      required
                      pattern="[a-z0-9\-]+"
                      class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                      :placeholder="t('app.sysadmin.create_restaurant.subdomain_placeholder')"
                      @input="validateSubdomain"
                    />
                    <span class="text-sm text-gray-500 dark:text-gray-400">.tudominio.com</span>
                  </div>
                  <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    {{ t('app.sysadmin.create_restaurant.subdomain_hint') }}
                  </p>
                </div>

                <!-- Email -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {{ t('app.sysadmin.create_restaurant.email') }} *
                  </label>
                  <input
                    v-model="form.email"
                    type="email"
                    required
                    class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                    :placeholder="t('app.sysadmin.create_restaurant.email_placeholder')"
                  />
                </div>

                <!-- Phone -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {{ t('app.sysadmin.create_restaurant.phone') }}
                  </label>
                  <input
                    v-model="form.phone"
                    type="tel"
                    class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                    :placeholder="t('app.sysadmin.create_restaurant.phone_placeholder')"
                  />
                </div>

                <!-- Address -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {{ t('app.sysadmin.create_restaurant.address') }}
                  </label>
                  <textarea
                    v-model="form.address"
                    rows="2"
                    class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                    :placeholder="t('app.sysadmin.create_restaurant.address_placeholder')"
                  />
                </div>

                <!-- Description -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {{ t('app.sysadmin.create_restaurant.description') }}
                  </label>
                  <textarea
                    v-model="form.description"
                    rows="3"
                    class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                    :placeholder="t('app.sysadmin.create_restaurant.description_placeholder')"
                  />
                </div>

                <!-- Trial Days Selector -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {{ t('app.sysadmin.create_restaurant.trial_days') }} *
                  </label>
                  <select
                    v-model.number="form.trial_days"
                    class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                  >
                    <option :value="14">14 {{ t('app.common.days') }} ({{ t('app.sysadmin.create_restaurant.trial_default') }})</option>
                    <option :value="30">30 {{ t('app.common.days') }} (1 {{ t('app.common.month') }})</option>
                    <option :value="60">60 {{ t('app.common.days') }} (2 {{ t('app.common.months') }})</option>
                  </select>
                  <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    {{ t('app.sysadmin.create_restaurant.trial_days_hint') }}
                  </p>
                </div>

                <!-- Trial Info -->
                <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <div class="flex items-start gap-3">
                    <svg class="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div class="flex-1">
                      <p class="text-sm font-medium text-blue-900 dark:text-blue-200">
                        {{ t('app.sysadmin.create_restaurant.trial_info_title') }}
                      </p>
                      <p class="text-sm text-blue-700 dark:text-blue-300 mt-1">
                        {{ t('app.sysadmin.create_restaurant.trial_info_desc') }}
                      </p>
                    </div>
                  </div>
                </div>

                <!-- Actions -->
                <div class="flex justify-end gap-3 mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <button
                    type="button"
                    @click="emit('close')"
                    class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600"
                    :disabled="submitting"
                  >
                    {{ t('app.common.cancel') }}
                  </button>
                  <button
                    type="submit"
                    class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    :disabled="submitting"
                  >
                    <svg v-if="submitting" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ t('app.sysadmin.create_restaurant.create_button') }}
                  </button>
                </div>
              </form>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { Dialog, DialogPanel, DialogTitle, TransitionRoot, TransitionChild } from '@headlessui/vue';
import { adminService } from '@/services/adminService';
import { useToast, POSITION } from 'vue-toastification';

const { t } = useI18n();
const toast = useToast();

const props = defineProps<{
  show: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'created'): void;
}>();

const submitting = ref(false);
const createdRestaurant = ref<any>(null);
const form = ref({
  name: '',
  subdomain: '',
  email: '',
  phone: '',
  address: '',
  description: '',
  trial_days: 14
});

const validateSubdomain = (event: Event) => {
  const input = event.target as HTMLInputElement;
  // Only allow lowercase letters, numbers, and hyphens
  input.value = input.value.toLowerCase().replace(/[^a-z0-9-]/g, '');
  form.value.subdomain = input.value;
};

const resetForm = () => {
  form.value = {
    name: '',
    subdomain: '',
    email: '',
    phone: '',
    address: '',
    description: '',
    trial_days: 14
  };
  createdRestaurant.value = null;
};

const handleSubmit = async () => {
  submitting.value = true;
  try {
    const restaurant = await adminService.createRestaurant(form.value);
    createdRestaurant.value = restaurant;
    
    toast.success(t('app.sysadmin.create_restaurant.success'), {
      position: POSITION.TOP_RIGHT,
      timeout: 5000
    });
  } catch (error: any) {
    console.error('Error creating restaurant:', error);
    
    const errorMessage = error.response?.data?.detail || t('app.sysadmin.create_restaurant.error');
    toast.error(errorMessage, {
      position: POSITION.TOP_RIGHT,
      timeout: 5000
    });
  } finally {
    submitting.value = false;
  }
};

const handleClose = () => {
  if (createdRestaurant.value) {
    emit('created');
  }
  resetForm();
  emit('close');
};

const getSubdomainUrl = () => {
  if (!createdRestaurant.value) return '';
  const subdomain = createdRestaurant.value.subdomain;
  // Use current hostname for development, or shopacoffee.com for production
  const hostname = window.location.hostname;
  if (hostname === 'localhost' || hostname.startsWith('127.')) {
    return `http://${subdomain}.shopacoffee.local:3000`;
  }
  return `https://${subdomain}.shopacoffee.com`;
};

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text);
    toast.success(t('app.common.copied'), {
      position: POSITION.TOP_RIGHT,
      timeout: 2000
    });
  } catch (error) {
    console.error('Failed to copy:', error);
    toast.error(t('app.common.copy_failed'), {
      position: POSITION.TOP_RIGHT,
      timeout: 2000
    });
  }
};

watch(() => props.show, (newValue) => {
  if (newValue) {
    resetForm();
  }
});
</script>
