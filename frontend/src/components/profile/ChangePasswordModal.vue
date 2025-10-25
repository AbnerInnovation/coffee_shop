<template>
  <TransitionRoot appear :show="show" as="template">
    <Dialog as="div" @close="emit('close')" class="relative z-[10001]">
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
                {{ t('app.profile.change_password.title') }}
              </DialogTitle>

              <form @submit.prevent="handleSubmit" class="space-y-4">
                <!-- Current Password -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {{ t('app.profile.change_password.current_password') }} *
                  </label>
                  <input
                    v-model="form.current_password"
                    type="password"
                    required
                    class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                    :placeholder="t('app.profile.change_password.current_password_placeholder')"
                  />
                </div>

                <!-- New Password -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {{ t('app.profile.change_password.new_password') }} *
                  </label>
                  <input
                    v-model="form.new_password"
                    type="password"
                    required
                    minlength="8"
                    class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                    :placeholder="t('app.profile.change_password.new_password_placeholder')"
                  />
                  <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    {{ t('app.profile.change_password.password_requirements') }}
                  </p>
                </div>

                <!-- Confirm New Password -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {{ t('app.profile.change_password.confirm_password') }} *
                  </label>
                  <input
                    v-model="form.confirm_password"
                    type="password"
                    required
                    minlength="8"
                    class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
                    :placeholder="t('app.profile.change_password.confirm_password_placeholder')"
                  />
                  <p v-if="form.new_password && form.confirm_password && form.new_password !== form.confirm_password" class="mt-1 text-xs text-red-600 dark:text-red-400">
                    {{ t('app.profile.change_password.passwords_dont_match') }}
                  </p>
                </div>

                <!-- Info Box -->
                <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                  <p class="text-sm text-blue-900 dark:text-blue-200">
                    <strong>{{ t('app.profile.change_password.note') }}:</strong> {{ t('app.profile.change_password.note_text') }}
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
                    :disabled="loading || !isFormValid"
                    class="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    <svg v-if="loading" class="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ loading ? t('app.common.loading') : t('app.profile.change_password.submit') }}
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
import { ref, computed } from 'vue';
import { TransitionRoot, TransitionChild, Dialog, DialogPanel, DialogTitle } from '@headlessui/vue';
import { useI18n } from 'vue-i18n';
import { useToast, POSITION } from 'vue-toastification';
import api from '@/services/api';

const { t } = useI18n();
const toast = useToast();

interface Props {
  show: boolean;
}

defineProps<Props>();
const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'success'): void;
}>();

const loading = ref(false);
const form = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
});

const isFormValid = computed(() => {
  return form.value.current_password &&
         form.value.new_password &&
         form.value.confirm_password &&
         form.value.new_password === form.value.confirm_password &&
         form.value.new_password.length >= 8;
});

const resetForm = () => {
  form.value = {
    current_password: '',
    new_password: '',
    confirm_password: ''
  };
};

const handleSubmit = async () => {
  if (!isFormValid.value) {
    toast.error(t('app.profile.change_password.validation_error'), {
      position: POSITION.TOP_RIGHT,
      timeout: 3000
    });
    return;
  }

  loading.value = true;
  
  try {
    await api.post('/auth/change-password', {
      current_password: form.value.current_password,
      new_password: form.value.new_password
    });
    
    resetForm();
    emit('success');
    emit('close');
  } catch (error: any) {
    console.error('Error changing password:', error);
    
    // Handle validation errors
    if (error.response?.data?.error?.validation_errors) {
      const validationErrors = error.response.data.error.validation_errors;
      const errorMessages = validationErrors.map((err: any) => err.message).join('\n');
      toast.error(errorMessages, {
        position: POSITION.TOP_RIGHT,
        timeout: 4000
      });
    } else {
      toast.error(error.response?.data?.error?.message || error.response?.data?.detail || t('app.profile.change_password.error'), {
        position: POSITION.TOP_RIGHT,
        timeout: 4000
      });
    }
  } finally {
    loading.value = false;
  }
};
</script>
