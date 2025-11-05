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

              <!-- Success Message with Credentials -->
              <div v-if="createdRestaurant && restaurantCreationData" class="space-y-4">
                <!-- Success Header -->
                <div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                  <div class="flex items-start gap-3">
                    <svg class="h-6 w-6 text-green-600 dark:text-green-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div class="flex-1">
                      <p class="text-sm font-medium text-green-900 dark:text-green-200">
                        ¡Restaurante Creado Exitosamente!
                      </p>
                      <p class="text-sm text-green-700 dark:text-green-300 mt-1">
                        <strong>{{ createdRestaurant.name }}</strong>
                      </p>
                    </div>
                  </div>
                </div>

                <!-- Admin Credentials Card -->
                <div class="bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 border-2 border-indigo-300 dark:border-indigo-700 rounded-lg p-5">
                  <div class="flex items-center gap-2 mb-3">
                    <svg class="h-5 w-5 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                    </svg>
                    <h4 class="text-base font-semibold text-indigo-900 dark:text-indigo-200">
                      Credenciales del Administrador
                    </h4>
                  </div>

                  <!-- URL -->
                  <div class="mb-3">
                    <label class="block text-xs font-medium text-indigo-700 dark:text-indigo-300 mb-1">
                      URL del Sistema:
                    </label>
                    <div class="flex items-center gap-2">
                      <input
                        :value="restaurantCreationData.restaurant_url"
                        readonly
                        class="flex-1 px-3 py-2 bg-white dark:bg-gray-800 border border-indigo-200 dark:border-indigo-600 rounded-lg text-sm text-gray-900 dark:text-white font-mono"
                      />
                      <button
                        type="button"
                        @click="copyToClipboard(restaurantCreationData.restaurant_url, 'URL')"
                        class="px-3 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm"
                      >
                        Copiar
                      </button>
                    </div>
                  </div>

                  <!-- Email -->
                  <div class="mb-3">
                    <label class="block text-xs font-medium text-indigo-700 dark:text-indigo-300 mb-1">
                      Email:
                    </label>
                    <div class="flex items-center gap-2">
                      <input
                        :value="restaurantCreationData.admin_email"
                        readonly
                        class="flex-1 px-3 py-2 bg-white dark:bg-gray-800 border border-indigo-200 dark:border-indigo-600 rounded-lg text-sm text-gray-900 dark:text-white font-mono"
                      />
                      <button
                        type="button"
                        @click="copyToClipboard(restaurantCreationData.admin_email, 'Email')"
                        class="px-3 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm"
                      >
                        Copiar
                      </button>
                    </div>
                  </div>

                  <!-- Password -->
                  <div class="mb-3">
                    <label class="block text-xs font-medium text-indigo-700 dark:text-indigo-300 mb-1">
                      Contraseña:
                    </label>
                    <div class="flex items-center gap-2">
                      <input
                        :value="restaurantCreationData.admin_password"
                        readonly
                        class="flex-1 px-3 py-2 bg-white dark:bg-gray-800 border border-indigo-200 dark:border-indigo-600 rounded-lg text-sm text-gray-900 dark:text-white font-mono font-bold"
                      />
                      <button
                        type="button"
                        @click="copyToClipboard(restaurantCreationData.admin_password, 'Contraseña')"
                        class="px-3 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm"
                      >
                        Copiar
                      </button>
                    </div>
                  </div>

                  <!-- Warning -->
                  <div class="bg-amber-50 dark:bg-amber-900/20 border border-amber-300 dark:border-amber-700 rounded-lg p-3 mt-4">
                    <div class="flex items-start gap-2">
                      <svg class="h-5 w-5 text-amber-600 dark:text-amber-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <p class="text-xs text-amber-800 dark:text-amber-200">
                        <strong>¡IMPORTANTE!</strong> Esta es la única vez que verás esta contraseña. Cópiala ahora y compártela con el administrador del restaurante.
                      </p>
                    </div>
                  </div>
                </div>

                <!-- Trial Info -->
                <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <div class="flex items-center gap-2 mb-2">
                    <svg class="h-5 w-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <h4 class="text-sm font-semibold text-blue-900 dark:text-blue-200">
                      Período de Prueba
                    </h4>
                  </div>
                  <p class="text-sm text-blue-800 dark:text-blue-300">
                    <strong>{{ restaurantCreationData.trial_days }} días</strong> de acceso completo
                  </p>
                  <p class="text-xs text-blue-700 dark:text-blue-400 mt-1">
                    Vence: {{ formatTrialDate(restaurantCreationData.trial_expires) }}
                  </p>
                </div>

                <!-- Action Buttons -->
                <div class="flex flex-col sm:flex-row gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <button
                    type="button"
                    @click="copyWelcomeMessage"
                    class="flex-1 px-4 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:from-green-700 hover:to-emerald-700 transition-all text-sm font-medium flex items-center justify-center gap-2 shadow-lg"
                  >
                    <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3" />
                    </svg>
                    Copiar Mensaje para Admin
                  </button>
                  <button
                    type="button"
                    @click="handleClose"
                    class="px-6 py-3 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
                  >
                    Cerrar
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

                <!-- Admin Email (Optional) -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Email del Administrador (Opcional)
                  </label>
                  <input
                    v-model="form.admin_email"
                    type="email"
                    class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                    placeholder="admin@ejemplo.com"
                  />
                  <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    Si se deja vacío, se usará: admin-{{ form.subdomain || 'subdomain' }}@shopacoffee.com
                  </p>
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
const restaurantCreationData = ref<any>(null);
const form = ref({
  name: '',
  subdomain: '',
  email: '',
  admin_email: '',
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
    admin_email: '',
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
    const response = await adminService.createRestaurant(form.value);
    
    console.log('🔍 Restaurant creation response:', response);
    console.log('🔍 Has welcome_message?', !!response.welcome_message);
    console.log('🔍 Has shareable_message?', !!response.shareable_message);
    console.log('🔍 Has admin_password?', !!response.admin_password);
    
    // Check if response has welcome message (new format)
    if (response.welcome_message && response.shareable_message && response.admin_password) {
      // New format with complete welcome data
      console.log('✅ Showing credentials in modal');
      restaurantCreationData.value = response;
      createdRestaurant.value = response.restaurant;
    } else {
      // Old format (just restaurant object) or missing data
      console.warn('⚠️ Response missing welcome data, showing basic success message');
      console.log('Response keys:', Object.keys(response));
      createdRestaurant.value = response.restaurant || response;
      restaurantCreationData.value = null;
    }
    
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

const copyToClipboard = async (text: string, label: string = 'Texto') => {
  try {
    await navigator.clipboard.writeText(text);
    toast.success(`${label} copiado al portapapeles`, {
      position: POSITION.TOP_RIGHT,
      timeout: 2000
    });
  } catch (error) {
    console.error('Failed to copy:', error);
    toast.error('Error al copiar', {
      position: POSITION.TOP_RIGHT,
      timeout: 2000
    });
  }
};

const copyWelcomeMessage = async () => {
  if (!restaurantCreationData.value) return;
  
  const message = `🎉 ¡Bienvenido a Cloud Restaurant!

Tu restaurante "${createdRestaurant.value.name}" ha sido creado exitosamente.

📋 ACCESO AL SISTEMA:
🌐 URL: ${restaurantCreationData.value.restaurant_url}
📧 Email: ${restaurantCreationData.value.admin_email}
🔑 Contraseña: ${restaurantCreationData.value.admin_password}

⚠️ IMPORTANTE: 
• Cambia tu contraseña al iniciar sesión por primera vez
• Ve a tu perfil → Cambiar Contraseña

🎁 PERÍODO DE PRUEBA:
• Duración: ${restaurantCreationData.value.trial_days} días
• Acceso completo a todas las funcionalidades

📝 PRIMEROS PASOS:
1. Ingresa al sistema con las credenciales proporcionadas
2. Cambia tu contraseña
3. Configura la información de tu restaurante
4. Crea tu menú y categorías
5. Agrega tus mesas
6. Crea usuarios para tu personal
7. ¡Comienza a tomar pedidos!

¡Éxito con tu restaurante! 🍽️`;

  await copyToClipboard(message, 'Mensaje completo');
};

const formatTrialDate = (dateStr: string) => {
  if (!dateStr) return 'N/A';
  const date = new Date(dateStr);
  return date.toLocaleDateString('es-ES', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
};

watch(() => props.show, (newValue) => {
  if (newValue) {
    resetForm();
  }
});
</script>
