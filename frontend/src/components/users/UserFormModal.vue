<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-[10001] overflow-y-auto"
    @click.self="$emit('close')"
  >
    <div class="flex min-h-screen items-center justify-center p-4">
      <!-- Backdrop -->
      <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity"></div>

      <!-- Modal -->
      <div class="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
        <!-- Header -->
        <div class="mb-6">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white">
            {{ mode === 'create' ? t('app.users.modal.create_title') : t('app.users.modal.edit_title') }}
          </h3>
        </div>

        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Full Name -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ t('app.users.modal.full_name') }}
            </label>
            <input
              v-model="form.full_name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
              :placeholder="t('app.users.modal.full_name_placeholder')"
            />
          </div>

          <!-- Email -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ t('app.users.modal.email') }}
            </label>
            <input
              v-model="form.email"
              type="email"
              required
              @blur="validateEmail"
              @input="emailTouched = true"
              :class="[
                'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white',
                emailError && emailTouched ? 'border-red-500 dark:border-red-500' : 'border-gray-300 dark:border-gray-600'
              ]"
              :placeholder="t('app.users.modal.email_placeholder')"
            />
            <p v-if="emailError && emailTouched" class="mt-1 text-xs text-red-600 dark:text-red-400">
              {{ emailError }}
            </p>
          </div>

          <!-- Password -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ t('app.users.modal.password') }}
              <span v-if="mode === 'edit'" class="text-xs text-gray-500">
                ({{ t('app.users.modal.password_optional') }})
              </span>
            </label>
            <input
              v-model="form.password"
              type="password"
              :required="mode === 'create'"
              minlength="8"
              @blur="validatePassword"
              @input="passwordTouched = true"
              :class="[
                'w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white',
                passwordErrors.length > 0 && passwordTouched ? 'border-red-500 dark:border-red-500' : 'border-gray-300 dark:border-gray-600'
              ]"
              :placeholder="t('app.users.modal.password_placeholder')"
            />
            
            <!-- Password validation errors -->
            <div v-if="passwordErrors.length > 0 && passwordTouched" class="mt-2 space-y-1">
              <p v-for="(error, index) in passwordErrors" :key="index" class="text-xs text-red-600 dark:text-red-400">
                • {{ error }}
              </p>
            </div>
            
            <!-- Password hint (only show if no errors or not touched) -->
            <p v-else class="mt-1 text-xs text-gray-500 dark:text-gray-400">
              {{ t('app.users.modal.password_hint') }}
            </p>
          </div>

          <!-- Role -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ t('app.users.modal.role') }}
            </label>
            <select
              v-model="form.role"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="admin">{{ t('app.users.roles.admin') }}</option>
              <option value="staff">{{ t('app.users.roles.staff') }}</option>
              <option value="customer">{{ t('app.users.roles.customer') }}</option>
            </select>
          </div>

          <!-- Staff Type (only show if role is staff) -->
          <div v-if="form.role === 'staff'">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {{ t('app.users.modal.staff_type') }}
            </label>
            <select
              v-model="form.staff_type"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="">{{ t('app.users.modal.select_staff_type') }}</option>
              <option value="waiter">{{ t('app.users.staff_types.waiter') }}</option>
              <option value="cashier">{{ t('app.users.staff_types.cashier') }}</option>
              <option value="kitchen">{{ t('app.users.staff_types.kitchen') }}</option>
              <option value="general">{{ t('app.users.staff_types.general') }}</option>
            </select>
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
              {{ t('app.users.modal.staff_type_hint') }}
            </p>
          </div>

          <!-- Active Status -->
          <div class="flex items-center">
            <input
              v-model="form.is_active"
              type="checkbox"
              id="is_active"
              class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <label for="is_active" class="ml-2 block text-sm text-gray-700 dark:text-gray-300">
              {{ t('app.users.modal.is_active') }}
            </label>
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p class="text-sm text-red-600 dark:text-red-400">{{ errorMessage }}</p>
          </div>

          <!-- Actions -->
          <div class="flex gap-3 pt-4">
            <button
              type="button"
              @click="$emit('close')"
              class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              {{ t('app.users.modal.cancel') }}
            </button>
            <button
              type="submit"
              :disabled="saving"
              class="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ saving ? t('app.users.modal.saving') : t('app.users.modal.save') }}
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
import restaurantUsersService, { type RestaurantUser, type CreateRestaurantUser, type UpdateRestaurantUser } from '@/services/restaurantUsersService';

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
const passwordErrors = ref<string[]>([]);
const passwordTouched = ref(false);
const emailError = ref('');
const emailTouched = ref(false);

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
  } else {
    // Reset form for create mode
    form.value = {
      email: '',
      full_name: '',
      password: '',
      role: 'staff',
      staff_type: null,
      is_active: true
    };
  }
  errorMessage.value = '';
  passwordErrors.value = [];
  passwordTouched.value = false;
  emailError.value = '';
  emailTouched.value = false;
}, { immediate: true });

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
  passwordTouched.value = true;
  emailTouched.value = true;
  
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
    errorMessage.value = error.response?.data?.detail || t('users.errors.save_failed');
  } finally {
    saving.value = false;
  }
}
</script>
