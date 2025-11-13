<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-[10001]"
    @click.self="$emit('close')"
  >
    <div class="flex h-full w-full sm:items-center sm:justify-center sm:p-4">
      <!-- Backdrop -->
      <div class="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity"></div>

      <!-- Modal -->
      <div class="relative overflow-y-auto bg-white dark:bg-gray-900 rounded-none sm:rounded-xl shadow-2xl w-full h-full sm:h-auto sm:max-w-lg p-4 sm:p-8 border-0 sm:border border-gray-200 dark:border-gray-800">
        <!-- Header -->
        <div class="mb-4 sm:mb-6 pb-3 sm:pb-4 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-2 sm:gap-3">
            <div class="flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
              <UserPlusIcon v-if="mode === 'create'" class="h-4 w-4 sm:h-5 sm:w-5 text-indigo-600 dark:text-indigo-400" />
              <PencilIcon v-else class="h-4 w-4 sm:h-5 sm:w-5 text-indigo-600 dark:text-indigo-400" />
            </div>
            <div>
              <h3 class="text-lg sm:text-xl font-bold text-gray-900 dark:text-white">
                {{ mode === 'create' ? t('app.users.modal.create_title') : t('app.users.modal.edit_title') }}
              </h3>
              <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                {{ mode === 'create' ? 'Completa los datos del nuevo usuario' : 'Actualiza la información del usuario' }}
              </p>
            </div>
          </div>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="space-y-3 sm:space-y-4">
          <!-- Full Name -->
          <div>
            <label class="block text-xs sm:text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5 sm:mb-2">
              {{ t('app.users.modal.full_name') }}
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <UserIcon class="h-5 w-5 text-gray-400" />
              </div>
              <input
                v-model="form.full_name"
                type="text"
                required
                @input="fullNameTouched = true; fullNameError = ''"
                :class="[
                  'w-full pl-10 pr-3 py-2 sm:py-2.5 text-sm border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-800 dark:text-white transition-colors',
                  fullNameError && fullNameTouched ? 'border-red-500 dark:border-red-500' : 'border-gray-300 dark:border-gray-700'
                ]"
                :placeholder="t('app.users.modal.full_name_placeholder')"
              />
            </div>
            <p v-if="fullNameError && fullNameTouched" class="mt-1.5 text-xs text-red-600 dark:text-red-400 flex items-center gap-1">
              <ExclamationCircleIcon class="h-4 w-4" />
              {{ fullNameError }}
            </p>
          </div>

          <!-- Email -->
          <div>
            <label class="block text-xs sm:text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5 sm:mb-2">
              {{ t('app.users.modal.email') }}
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <EnvelopeIcon class="h-5 w-5 text-gray-400" />
              </div>
              <input
                v-model="form.email"
                type="email"
                required
                @blur="validateEmail"
                @input="emailTouched = true"
                :class="[
                  'w-full pl-10 pr-3 py-2 sm:py-2.5 text-sm border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-800 dark:text-white transition-colors',
                  emailError && emailTouched ? 'border-red-500 dark:border-red-500' : 'border-gray-300 dark:border-gray-700'
                ]"
                :placeholder="t('app.users.modal.email_placeholder')"
              />
            </div>
            <p v-if="emailError && emailTouched" class="mt-1.5 text-xs text-red-600 dark:text-red-400 flex items-center gap-1">
              <ExclamationCircleIcon class="h-4 w-4" />
              {{ emailError }}
            </p>
          </div>

          <!-- Password -->
          <div>
            <label class="block text-xs sm:text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5 sm:mb-2">
              {{ t('app.users.modal.password') }}
              <span v-if="mode === 'edit'" class="text-xs font-normal text-gray-500 dark:text-gray-400">
                ({{ t('app.users.modal.password_optional') }})
              </span>
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <LockClosedIcon class="h-5 w-5 text-gray-400" />
              </div>
              <input
                v-model="form.password"
                type="password"
                :required="mode === 'create'"
                minlength="8"
                @blur="validatePassword"
                @input="passwordTouched = true"
                :class="[
                  'w-full pl-10 pr-3 py-2 sm:py-2.5 text-sm border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-800 dark:text-white transition-colors',
                  passwordErrors.length > 0 && passwordTouched ? 'border-red-500 dark:border-red-500' : 'border-gray-300 dark:border-gray-700'
                ]"
                :placeholder="t('app.users.modal.password_placeholder')"
              />
            </div>
            
            <!-- Password validation errors -->
            <div v-if="passwordErrors.length > 0 && passwordTouched" class="mt-1.5 sm:mt-2 space-y-0.5 sm:space-y-1 p-2 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
              <p v-for="(error, index) in passwordErrors" :key="index" class="text-xs text-red-600 dark:text-red-400 flex items-start gap-1.5">
                <XCircleIcon class="h-3.5 w-3.5 mt-0.5 flex-shrink-0" />
                <span>{{ error }}</span>
              </p>
            </div>
            
            <!-- Password hint (only show if no errors or not touched) -->
            <p v-else class="mt-1.5 text-xs text-gray-500 dark:text-gray-400 flex items-start gap-1.5">
              <InformationCircleIcon class="h-4 w-4 sm:h-5 sm:w-5 flex-shrink-0 mt-0.5" />
              <span>{{ t('app.users.modal.password_hint') }}</span>
            </p>
          </div>

          <!-- Role -->
          <div>
            <label class="block text-xs sm:text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5 sm:mb-2">
              {{ t('app.users.modal.role') }}
            </label>
            <select
              v-model="form.role"
              required
              class="w-full px-3 py-2 sm:py-2.5 text-sm border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-800 dark:text-white transition-colors"
            >
              <option value="admin">{{ t('app.users.roles.admin') }}</option>
              <option value="staff">{{ t('app.users.roles.staff') }}</option>
              <option value="customer">{{ t('app.users.roles.customer') }}</option>
            </select>
          </div>

          <!-- Staff Type (only show if role is staff) -->
          <div v-if="form.role === 'staff'">
            <label class="block text-xs sm:text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5 sm:mb-2">
              {{ t('app.users.modal.staff_type') }}
            </label>
            <select
              v-model="form.staff_type"
              required
              class="w-full px-3 py-2 sm:py-2.5 text-sm border border-gray-300 dark:border-gray-700 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-800 dark:text-white transition-colors"
            >
              <option value="">{{ t('app.users.modal.select_staff_type') }}</option>
              <option value="waiter">{{ t('app.users.staff_types.waiter') }}</option>
              <option value="cashier">{{ t('app.users.staff_types.cashier') }}</option>
              <option value="kitchen">{{ t('app.users.staff_types.kitchen') }}</option>
              <option value="general">{{ t('app.users.staff_types.general') }}</option>
            </select>
            <p class="mt-1.5 text-xs text-gray-500 dark:text-gray-400 flex items-start gap-1.5">
              <InformationCircleIcon class="h-4 w-4 sm:h-5 sm:w-5 flex-shrink-0 mt-0.5" />
              <span>{{ t('app.users.modal.staff_type_hint') }}</span>
            </p>
          </div>

          <!-- Active Status -->
          <div class="flex items-center p-2.5 sm:p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700">
            <input
              v-model="form.is_active"
              type="checkbox"
              id="is_active"
              class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 dark:border-gray-600 rounded"
            />
            <label for="is_active" class="ml-2.5 sm:ml-3 block text-xs sm:text-sm font-medium text-gray-700 dark:text-gray-300">
              {{ t('app.users.modal.is_active') }}
            </label>
          </div>

          <!-- Subscription Limit Alert -->
          <SubscriptionLimitAlert
            v-if="subscriptionLimitError"
            :message="subscriptionLimitError"
            :dismissible="false"
          />
          
          <!-- Generic Error Message -->
          <div v-else-if="errorMessage" class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p class="text-sm text-red-600 dark:text-red-400">{{ errorMessage }}</p>
          </div>

          <!-- Actions -->
          <div class="flex gap-2 sm:gap-3 pt-4 sm:pt-6 border-t border-gray-200 dark:border-gray-700 mt-4 sm:mt-6">
            <button
              type="button"
              @click="$emit('close')"
              class="flex-1 px-3 sm:px-4 py-2 sm:py-2.5 text-sm sm:text-base border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors font-medium"
            >
              {{ t('app.users.modal.cancel') }}
            </button>
            <button
              type="submit"
              :disabled="saving"
              class="flex-1 px-3 sm:px-4 py-2 sm:py-2.5 text-sm sm:text-base bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-sm"
            >
              <span v-if="saving" class="flex items-center justify-center gap-2">
                <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ t('app.users.modal.saving') }}
              </span>
              <span v-else>{{ t('app.users.modal.save') }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import {
  UserIcon,
  EnvelopeIcon,
  LockClosedIcon,
  UserPlusIcon,
  PencilIcon,
  ExclamationCircleIcon,
  XCircleIcon,
  InformationCircleIcon
} from '@heroicons/vue/24/outline';
import restaurantUsersService, { type RestaurantUser, type CreateRestaurantUser, type UpdateRestaurantUser } from '@/services/restaurantUsersService';
import SubscriptionLimitAlert from '@/components/subscription/SubscriptionLimitAlert.vue';

const { t } = useI18n();

interface Props {
  isOpen: boolean;
  user: RestaurantUser | null;
  mode: 'create' | 'edit';
}

const props = defineProps<Props>();
const emit = defineEmits<{
  close: [];
  saved: [];
}>();

const form = ref<CreateRestaurantUser & { id?: number }>({
  email: '',
  full_name: '',
  password: '',
  role: 'staff',
  staff_type: null,
  is_active: true
});

const saving = ref(false);
const errorMessage = ref('');
const subscriptionLimitError = ref('');
const passwordErrors = ref<string[]>([]);
const passwordTouched = ref(false);
const emailError = ref('');
const emailTouched = ref(false);
const fullNameError = ref('');
const fullNameTouched = ref(false);

// Function to reset form to initial state
function resetForm() {
  form.value = {
    email: '',
    full_name: '',
    password: '',
    role: 'staff',
    staff_type: null,
    is_active: true
  };
  errorMessage.value = '';
  subscriptionLimitError.value = '';
  passwordErrors.value = [];
  passwordTouched.value = false;
  emailError.value = '';
  emailTouched.value = false;
  fullNameError.value = '';
  fullNameTouched.value = false;
}

// Watch for user changes to populate form in edit mode
watch(() => props.user, (newUser) => {
  if (newUser && props.mode === 'edit') {
    form.value = {
      id: newUser.id,
      email: newUser.email,
      full_name: newUser.full_name,
      password: '',
      role: newUser.role as 'admin' | 'staff' | 'customer',
      staff_type: newUser.staff_type || null,
      is_active: newUser.is_active
    };
    // Clear errors
    errorMessage.value = '';
    subscriptionLimitError.value = '';
    passwordErrors.value = [];
    passwordTouched.value = false;
    emailError.value = '';
    emailTouched.value = false;
    fullNameError.value = '';
    fullNameTouched.value = false;
  } else if (props.mode === 'create') {
    // Reset form for create mode
    resetForm();
  }
}, { immediate: true });

// Watch for modal close to reset form
watch(() => props.isOpen, (isOpen) => {
  if (!isOpen) {
    // Reset form when modal closes
    setTimeout(() => {
      resetForm();
    }, 300); // Wait for modal close animation
  }
});

function validateEmail() {
  const email = form.value.email;
  
  if (!email) {
    emailError.value = 'El correo electrónico es obligatorio';
    return false;
  }
  
  // Basic email validation
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    emailError.value = 'Formato de correo electrónico inválido (ejemplo: usuario@dominio.com)';
    return false;
  }
  
  // Check for common typos
  const domain = email.split('@')[1];
  if (domain && !domain.includes('.')) {
    emailError.value = 'El dominio debe incluir una extensión (ejemplo: .com, .mx, .net)';
    return false;
  }
  
  emailError.value = '';
  return true;
}

function validatePassword() {
  const password = form.value.password;
  const errors: string[] = [];
  
  // Only validate if password is provided (required for create, optional for edit)
  if (!password && props.mode === 'create') {
    errors.push('La contraseña es obligatoria');
    passwordErrors.value = errors;
    return false;
  }
  
  // Skip validation if password is empty in edit mode
  if (!password && props.mode === 'edit') {
    passwordErrors.value = [];
    return true;
  }
  
  // Length check
  if (password.length < 8) {
    errors.push('Debe tener al menos 8 caracteres');
  }
  
  // Uppercase letter check
  if (!/[A-Z]/.test(password)) {
    errors.push('Debe contener al menos una letra mayúscula');
  }
  
  // Lowercase letter check
  if (!/[a-z]/.test(password)) {
    errors.push('Debe contener al menos una letra minúscula');
  }
  
  // Digit check
  if (!/\d/.test(password)) {
    errors.push('Debe contener al menos un número');
  }
  
  // Special character check
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('Debe contener al menos un carácter especial (!@#$%^&*(),.?":{}|<>)');
  }
  
  passwordErrors.value = errors;
  return errors.length === 0;
}

async function handleSubmit() {
  saving.value = true;
  errorMessage.value = '';
  subscriptionLimitError.value = '';
  passwordTouched.value = true;
  emailTouched.value = true;
  fullNameTouched.value = true;
  
  // Clear previous field errors
  fullNameError.value = '';
  emailError.value = '';
  passwordErrors.value = [];
  
  // Validate email
  if (!validateEmail()) {
    saving.value = false;
    errorMessage.value = 'Por favor corrige los errores de validación';
    return;
  }
  
  // Validate password before submitting
  if (!validatePassword()) {
    saving.value = false;
    errorMessage.value = 'Por favor corrige los errores de validación';
    return;
  }

  try {
    if (props.mode === 'create') {
      await restaurantUsersService.createUser(form.value);
    } else if (props.user) {
      const updateData: UpdateRestaurantUser = {
        email: form.value.email,
        full_name: form.value.full_name,
        role: form.value.role,
        staff_type: form.value.staff_type,
        is_active: form.value.is_active
      };
      
      // Only include password if it was changed
      if (form.value.password) {
        updateData.password = form.value.password;
      }
      
      await restaurantUsersService.updateUser(props.user.id, updateData);
    }
    
    emit('saved');
  } catch (error: any) {
    console.error('Error saving user:', error);
    
    // Handle subscription limit errors (403)
    if (error.response?.status === 403) {
      const message = error.response?.data?.detail || 
                     error.response?.data?.error?.message || 
                     'Límite de suscripción alcanzado. Por favor mejora tu plan.';
      subscriptionLimitError.value = message;
      return;
    }
    
    // Handle backend validation errors
    if (error.response?.data?.error?.validation_errors) {
      const validationErrors = error.response.data.error.validation_errors;
      
      // Map backend field names to frontend error refs
      validationErrors.forEach((err: any) => {
        const field = err.field.replace('body.', ''); // Remove 'body.' prefix
        
        switch (field) {
          case 'full_name':
            fullNameError.value = err.message;
            break;
          case 'email':
            emailError.value = err.message;
            break;
          case 'password':
            passwordErrors.value = [err.message];
            break;
          default:
            // For fields without specific error refs, show in general error
            if (!errorMessage.value) {
              errorMessage.value = err.message;
            }
        }
      });
      
      // Show general message if we have validation errors
      if (!errorMessage.value) {
        errorMessage.value = 'Por favor corrige los errores de validación';
      }
    } else if (error.response?.data?.error?.message) {
      // Handle other error types (like subscription limits)
      errorMessage.value = error.response.data.error.message;
    } else if (error.response?.data?.detail) {
      // Handle HTTPException detail format
      errorMessage.value = error.response.data.detail;
    } else {
      errorMessage.value = t('users.errors.save_failed');
    }
  } finally {
    saving.value = false;
  }
}
</script>
