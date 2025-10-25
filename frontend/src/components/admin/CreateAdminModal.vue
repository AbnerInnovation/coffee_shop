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
            <DialogPanel class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white dark:bg-gray-800 p-6 text-left align-middle shadow-xl transition-all">
              <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900 dark:text-white mb-4">
                {{ t('app.sysadmin.create_admin.title') }}
              </DialogTitle>

              <form @submit.prevent="handleSubmit" class="space-y-4">
                <!-- Restaurant Name (read-only) -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {{ t('app.sysadmin.create_admin.restaurant') }}
                  </label>
                  <input
                    :value="restaurant.name"
                    type="text"
                    disabled
                    class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 cursor-not-allowed"
                  />
                </div>

                <!-- Full Name -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {{ t('app.sysadmin.create_admin.full_name') }} *
                  </label>
                  <input
                    v-model="form.full_name"
                    type="text"
                    required
                    class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                    :placeholder="t('app.sysadmin.create_admin.full_name_placeholder')"
                  />
                </div>

                <!-- Email -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {{ t('app.sysadmin.create_admin.email') }} *
                  </label>
                  <input
                    v-model="form.email"
                    type="email"
                    required
                    class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                    :placeholder="t('app.sysadmin.create_admin.email_placeholder')"
                  />
                </div>

                <!-- Password -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {{ t('app.sysadmin.create_admin.password') }} *
                  </label>
                  <input
                    v-model="form.password"
                    type="password"
                    required
                    minlength="8"
                    class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                    :placeholder="t('app.sysadmin.create_admin.password_placeholder')"
                  />
                  <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    {{ t('app.sysadmin.create_admin.password_hint') }}
                  </p>
                </div>

                <!-- Info Box -->
                <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <p class="text-sm text-blue-900 dark:text-blue-200">
                    <strong>{{ t('app.sysadmin.create_admin.note') }}:</strong> {{ t('app.sysadmin.create_admin.note_text') }}
                  </p>
                </div>

                <!-- Actions -->
                <div class="flex gap-3 mt-6">
                  <button
                    type="button"
                    @click="emit('close')"
                    class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    {{ t('app.common.cancel') }}
                  </button>
                  <button
                    type="submit"
                    :disabled="loading"
                    class="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    <svg v-if="loading" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ loading ? t('app.common.loading') : t('app.sysadmin.create_admin.submit') }}
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
import { ref } from 'vue';
import { TransitionRoot, TransitionChild, Dialog, DialogPanel, DialogTitle } from '@headlessui/vue';
import { useI18n } from 'vue-i18n';
import { useToast, POSITION } from 'vue-toastification';
import { adminService } from '@/services/adminService';

const { t } = useI18n();
const toast = useToast();

interface Props {
  show: boolean;
  restaurant: {
    id: number;
    name: string;
  };
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'created'): void;
}>();

const loading = ref(false);
const form = ref({
  full_name: '',
  email: '',
  password: ''
});

const resetForm = () => {
  form.value = {
    full_name: '',
    email: '',
    password: ''
  };
};

const handleSubmit = async () => {
  loading.value = true;
  
  try {
    await adminService.createRestaurantAdmin(props.restaurant.id, form.value);
    
    toast.success(t('app.sysadmin.create_admin.success'), {
      position: POSITION.TOP_RIGHT,
      timeout: 3000
    });
    
    resetForm();
    emit('created');
    emit('close');
  } catch (error: any) {
    console.error('Error creating admin:', error);
    toast.error(error.response?.data?.detail || t('app.sysadmin.create_admin.error'), {
      position: POSITION.TOP_RIGHT,
      timeout: 4000
    });
  } finally {
    loading.value = false;
  }
};
</script>
