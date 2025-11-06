<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        {{ t('app.sysadmin.dashboard.title') }}
      </h1>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        {{ t('app.sysadmin.dashboard.subtitle') }}
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center items-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <p class="text-red-800 dark:text-red-200">{{ error }}</p>
    </div>

    <!-- Dashboard Content -->
    <div v-else>
      <!-- Quick Stats Grid -->
      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <!-- Total Restaurants -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <BuildingStorefrontIcon class="h-6 w-6 text-gray-400" />
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    {{ t('app.sysadmin.dashboard.total_restaurants') }}
                  </dt>
                  <dd class="flex items-baseline">
                    <div class="text-2xl font-semibold text-gray-900 dark:text-white">
                      {{ stats?.restaurants.total || 0 }}
                    </div>
                    <div class="ml-2 flex items-baseline text-sm font-semibold text-green-600">
                      +{{ stats?.restaurants.new_last_30_days || 0 }} {{ t('app.sysadmin.dashboard.this_month') }}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <!-- Active Restaurants -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <CheckCircleIcon class="h-6 w-6 text-green-400" />
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    {{ t('app.sysadmin.dashboard.active_restaurants') }}
                  </dt>
                  <dd class="flex items-baseline">
                    <div class="text-2xl font-semibold text-gray-900 dark:text-white">
                      {{ stats?.restaurants.active || 0 }}
                    </div>
                    <div class="ml-2 flex items-baseline text-sm text-gray-500 dark:text-gray-400">
                      / {{ stats?.restaurants.total || 0 }}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <!-- Monthly Recurring Revenue -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <CurrencyDollarIcon class="h-6 w-6 text-green-400" />
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    {{ t('app.sysadmin.dashboard.mrr') }}
                  </dt>
                  <dd class="text-2xl font-semibold text-gray-900 dark:text-white">
                    ${{ formatCurrency(stats?.revenue.mrr || 0) }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <!-- Pending Payments -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <ClockIcon class="h-6 w-6 text-amber-400" />
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    {{ t('app.sysadmin.dashboard.pending_payments') }}
                  </dt>
                  <dd class="text-2xl font-semibold text-gray-900 dark:text-white">
                    {{ stats?.revenue.pending_payments || 0 }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Secondary Stats -->
      <div class="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <!-- Trial Restaurants -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <SparklesIcon class="h-6 w-6 text-blue-400" />
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    {{ t('app.sysadmin.dashboard.trial_restaurants') }}
                  </dt>
                  <dd class="text-2xl font-semibold text-gray-900 dark:text-white">
                    {{ stats?.restaurants.trial || 0 }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <!-- Suspended Restaurants -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <ExclamationTriangleIcon class="h-6 w-6 text-red-400" />
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    {{ t('app.sysadmin.dashboard.suspended_restaurants') }}
                  </dt>
                  <dd class="text-2xl font-semibold text-gray-900 dark:text-white">
                    {{ stats?.restaurants.suspended || 0 }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <!-- Total Users -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <UsersIcon class="h-6 w-6 text-indigo-400" />
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    {{ t('app.sysadmin.dashboard.total_users') }}
                  </dt>
                  <dd class="text-2xl font-semibold text-gray-900 dark:text-white">
                    {{ stats?.users.total || 0 }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Activity Stats -->
      <div class="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2">
        <!-- Orders (Last 30 Days) -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <ShoppingBagIcon class="h-6 w-6 text-purple-400" />
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    {{ t('app.sysadmin.dashboard.orders_30d') }}
                  </dt>
                  <dd class="text-2xl font-semibold text-gray-900 dark:text-white">
                    {{ stats?.activity.orders_30d || 0 }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <!-- Revenue (Last 30 Days) -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <BanknotesIcon class="h-6 w-6 text-green-400" />
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                    {{ t('app.sysadmin.dashboard.revenue_30d') }}
                  </dt>
                  <dd class="text-2xl font-semibold text-gray-900 dark:text-white">
                    ${{ formatCurrency(stats?.revenue.revenue_30d || 0) }}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Subscription Distribution -->
      <div class="mt-6 bg-white dark:bg-gray-800 shadow rounded-lg">
        <div class="p-6">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
            {{ t('app.sysadmin.dashboard.subscription_distribution') }}
          </h3>
          <div class="space-y-3">
            <div
              v-for="(count, plan) in stats?.subscription_distribution"
              :key="plan"
              class="flex items-center justify-between"
            >
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ plan }}</span>
              <div class="flex items-center gap-3">
                <div class="w-32 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    class="bg-primary-600 h-2 rounded-full"
                    :style="{ width: `${(count / (stats?.restaurants.total || 1)) * 100}%` }"
                  ></div>
                </div>
                <span class="text-sm font-semibold text-gray-900 dark:text-white w-8 text-right">
                  {{ count }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <router-link
          to="/sysadmin"
          class="relative rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 dark:hover:border-gray-600 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500"
        >
          <div class="flex-shrink-0">
            <BuildingStorefrontIcon class="h-6 w-6 text-primary-600" />
          </div>
          <div class="flex-1 min-w-0">
            <span class="absolute inset-0" aria-hidden="true"></span>
            <p class="text-sm font-medium text-gray-900 dark:text-white">
              {{ t('app.sysadmin.dashboard.manage_restaurants') }}
            </p>
            <p class="text-sm text-gray-500 dark:text-gray-400 truncate">
              {{ t('app.sysadmin.dashboard.view_all_restaurants') }}
            </p>
          </div>
        </router-link>

        <router-link
          to="/sysadmin/payments"
          class="relative rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 dark:hover:border-gray-600 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500"
        >
          <div class="flex-shrink-0">
            <CreditCardIcon class="h-6 w-6 text-green-600" />
          </div>
          <div class="flex-1 min-w-0">
            <span class="absolute inset-0" aria-hidden="true"></span>
            <p class="text-sm font-medium text-gray-900 dark:text-white">
              {{ t('app.sysadmin.dashboard.pending_payments') }}
            </p>
            <p class="text-sm text-gray-500 dark:text-gray-400 truncate">
              {{ stats?.revenue.pending_payments || 0 }} {{ t('app.sysadmin.dashboard.payments_due') }}
            </p>
          </div>
        </router-link>

        <button
          @click="refreshStats"
          class="relative rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 dark:hover:border-gray-600 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500"
        >
          <div class="flex-shrink-0">
            <ArrowPathIcon class="h-6 w-6 text-gray-600" :class="{ 'animate-spin': loading }" />
          </div>
          <div class="flex-1 min-w-0 text-left">
            <p class="text-sm font-medium text-gray-900 dark:text-white">
              {{ t('app.sysadmin.dashboard.refresh_stats') }}
            </p>
            <p class="text-sm text-gray-500 dark:text-gray-400 truncate">
              {{ t('app.sysadmin.dashboard.update_data') }}
            </p>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import {
  BuildingStorefrontIcon,
  CheckCircleIcon,
  CurrencyDollarIcon,
  ClockIcon,
  SparklesIcon,
  ExclamationTriangleIcon,
  UsersIcon,
  ShoppingBagIcon,
  BanknotesIcon,
  CreditCardIcon,
  ArrowPathIcon
} from '@heroicons/vue/24/outline';
import { adminService, type GlobalStats } from '@/services/adminService';
import { useToast } from '@/composables/useToast';

const { t } = useI18n();
const { showError } = useToast();

const stats = ref<GlobalStats | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('es-MX', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
};

const loadStats = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    stats.value = await adminService.getGlobalStats();
  } catch (err: any) {
    const errorMessage: string = err.message || t('app.sysadmin.dashboard.error_loading_stats');
    error.value = errorMessage;
    showError(errorMessage);
  } finally {
    loading.value = false;
  }
};

const refreshStats = () => {
  loadStats();
};

onMounted(() => {
  loadStats();
});
</script>
