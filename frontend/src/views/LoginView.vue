<template>
  <div class=" flex justify-center bg-gray-50 dark:bg-gray-950 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          {{ t('app.views.auth.login.title') }}
        </h2>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="email-address" class="sr-only">{{ t('app.views.auth.login.email_placeholder') }}</label>
            <input
              id="email-address"
              v-model="email"
              name="email"
              type="email"
              autocomplete="email"
              required
              class="appearance-none rounded-none dark:bg-gray-800 dark:border-gray-700 dark:text-white relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              :placeholder="t('app.views.auth.login.email_placeholder')"
            />
          </div>
          <div>
            <label for="password" class="sr-only">{{ t('app.views.auth.login.password_placeholder') }}</label>
            <input
              id="password"
              v-model="password"
              name="password"
              type="password"
              autocomplete="current-password"
              required
              class="appearance-none rounded-none dark:bg-gray-800 dark:border-gray-700 dark:text-white relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              :placeholder="t('app.views.auth.login.password_placeholder')"
            />
          </div>
        </div>

        <div class="flex items-center justify-between">
          <label class="flex items-center space-x-2 select-none">
            <input type="checkbox" v-model="rememberMe" class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded" />
            <span class="text-sm text-gray-700 dark:text-gray-200">{{ t('app.views.auth.login.remember') }}</span>
          </label>
        </div>

        <div>
          <button
            type="submit"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            :disabled="loading"
          >
            <span v-if="!loading">{{ t('app.views.auth.login.cta') }}</span>
            <span v-else>{{ t('app.views.auth.login.cta_loading') }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useI18n } from 'vue-i18n';
import { useToast } from '@/composables/useToast';

const email = ref('');
const password = ref('');
const rememberMe = ref(true);
const loading = ref(false);
const router = useRouter();
const authStore = useAuthStore();
const { t } = useI18n();
const { showError } = useToast();

const backendResponseTranslations = {
  'Incorrect email or password': 'app.views.auth.login.errors.invalid_credentials',
  'Account is inactive': 'app.views.auth.login.errors.account_inactive',
  "don't have access to this restaurant": 'app.views.auth.login.errors.wrong_subdomain',
  'using your restaurant\'s subdomain': 'app.views.auth.login.errors.subdomain_required'
}

const handleLogin = async () => {
  try {
    loading.value = true;
    
    const success = await authStore.login({
      email: email.value,
      password: password.value
    }, rememberMe.value);
    
    if (success) {
      // Redirect based on user role
      const user = authStore.user;
      let redirectRoute = 'Dashboard';
      
      if (user?.role === 'staff' && user?.staff_type) {
        switch (user.staff_type) {
          case 'cashier':
            redirectRoute = 'CashRegister';
            break;
          case 'waiter':
            redirectRoute = 'Orders';
            break;
          case 'kitchen':
            redirectRoute = 'Kitchen';
            break;
          default:
            redirectRoute = 'Dashboard';
        }
      }
      
      await router.replace({ name: redirectRoute });
    } else {
      const errorMessage = authStore.error || '';
      let translationKey = backendResponseTranslations[errorMessage] || 'app.views.auth.login.errors.failed';
      showError(t(translationKey) as string, 6000);
    }
  } catch (err: any) {
    const errorMsg = err?.response?.data?.error?.message || err?.message || '';
    let translationKey = backendResponseTranslations[errorMsg] || 'app.views.auth.login.errors.generic';
    
    showError(t(translationKey) as string, 6000);
  } finally {
    loading.value = false;
  }
};
</script>
