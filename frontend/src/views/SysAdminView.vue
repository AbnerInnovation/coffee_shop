<template>
  <div class="min-h-screen p-6">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
        {{ t('app.sysadmin.title') }}
      </h1>
      <p class="mt-2 text-gray-600 dark:text-gray-400">
        {{ t('app.sysadmin.subtitle') }}
      </p>
    </div>

    <!-- Stats Cards -->
    <div v-if="stats" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <!-- Total Restaurants -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('app.sysadmin.stats.total_restaurants') }}</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-2">{{ stats.total_restaurants }}</p>
          </div>
          <BuildingStorefrontIcon class="h-12 w-12 text-indigo-500" />
        </div>
        <div class="mt-4 text-sm">
          <span class="text-green-600 dark:text-green-400">{{ stats.restaurants_with_subscription }}</span>
          <span class="text-gray-600 dark:text-gray-400 ml-1"> {{ t('app.sysadmin.stats.with_subscription') }}</span>
        </div>
      </div>

      <!-- Active Subscriptions -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('app.sysadmin.stats.active_subscriptions') }}</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-2">{{ stats.active_subscriptions }}</p>
          </div>
          <CheckCircleIcon class="h-12 w-12 text-green-500" />
        </div>
        <div class="mt-4 text-sm">
          <span class="text-blue-600 dark:text-blue-400">{{ stats.trial_subscriptions }}</span>
          <span class="text-gray-600 dark:text-gray-400 ml-1"> {{ t('app.sysadmin.stats.in_trial') }}</span>
        </div>
      </div>

      <!-- Monthly Revenue -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('app.sysadmin.stats.monthly_revenue') }}</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-2">${{ formatMoney(stats.total_monthly_revenue) }}</p>
          </div>
          <CurrencyDollarIcon class="h-12 w-12 text-yellow-500" />
        </div>
        <div class="mt-4 text-sm">
          <span class="text-gray-600 dark:text-gray-400">{{ t('app.sysadmin.stats.annual') }}: </span>
          <span class="text-green-600 dark:text-green-400">${{ formatMoney(stats.total_annual_revenue) }}</span>
        </div>
      </div>
      
      <!-- Without Subscription -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ t('app.sysadmin.stats.without_subscription') }}</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-2">{{ stats.restaurants_without_subscription }}</p>
          </div>
          <ExclamationTriangleIcon class="h-12 w-12 text-red-500" />
        </div>
        <div class="mt-4 text-sm">
          <span class="text-red-600 dark:text-red-400">{{ stats.cancelled_subscriptions }}</span>
          <span class="text-gray-600 dark:text-gray-400 ml-1"> {{ t('app.sysadmin.stats.cancelled') }}</span>
        </div>
      </div>
    </div>

    <!-- Filters and Search -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Search -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ t('app.sysadmin.filters.search') }}
          </label>
          <input
            v-model="searchQuery"
            type="text"
            :placeholder="t('app.sysadmin.filters.search_placeholder')"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
            @input="debouncedSearch"
          />
        </div>

        <!-- Filter by Subscription -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {{ t('app.sysadmin.filters.subscription_status') }}
          </label>
          <select
            v-model="filterSubscription"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
            @change="loadRestaurants"
          >
            <option :value="null">{{ t('app.sysadmin.filters.all') }}</option>
            <option :value="true">{{ t('app.sysadmin.filters.with_subscription') }}</option>
            <option :value="false">{{ t('app.sysadmin.filters.without_subscription') }}</option>
          </select>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-end gap-2">
          <button
            @click="openCreateRestaurantModal"
            class="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
          >
            <PlusIcon class="h-5 w-5" />
            {{ t('app.sysadmin.actions.new_restaurant') }}
          </button>
         
        </div>
      </div>
    </div>

    <!-- Restaurants List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
      <!-- Loading State -->
      <div v-if="loading" class="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
        <ArrowPathIcon class="h-8 w-8 animate-spin mx-auto mb-2" />
        {{ t('app.common.loading') }}
      </div>

      <!-- Empty State -->
      <div v-else-if="!restaurants || restaurants.length === 0" class="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
        {{ t('app.sysadmin.table.no_results') }}
      </div>

      <!-- Mobile Cards (< md) -->
      <div v-else class="md:hidden divide-y divide-gray-200 dark:divide-gray-700">
        <div v-for="restaurant in restaurants" :key="restaurant.id" class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700">
          <!-- Restaurant Name & Subdomain -->
          <div class="mb-3">
            <div class="text-base font-semibold text-gray-900 dark:text-white">
              {{ restaurant.name }}
            </div>
            <div class="text-sm text-gray-500 dark:text-gray-400">
              {{ restaurant.subdomain }}
            </div>
            <a 
              :href="getRestaurantUrl(restaurant.subdomain)" 
              target="_blank"
              class="inline-flex items-center gap-1 text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 mt-1"
            >
              <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              {{ t('app.sysadmin.actions.open_system') }}
            </a>
          </div>

          <!-- Status Badge -->
          <div class="mb-3">
            <span
              v-if="restaurant.subscription_status"
              :class="getStatusClass(restaurant.subscription_status)"
              class="inline-flex px-2.5 py-1 text-xs font-semibold rounded-full"
            >
              {{ t(`app.sysadmin.status.${restaurant.subscription_status}`) }}
            </span>
            <span v-else class="inline-flex px-2.5 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
              {{ t('app.sysadmin.status.none') }}
            </span>
          </div>

          <!-- Plan & Price -->
          <div class="grid grid-cols-2 gap-3 mb-3 text-sm">
            <div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">{{ t('app.sysadmin.table.plan') }}</div>
              <div v-if="restaurant.plan_name">
                <div class="font-medium text-gray-900 dark:text-white">{{ restaurant.plan_name }}</div>
                <div class="text-xs text-gray-500 dark:text-gray-400">{{ restaurant.plan_tier }}</div>
              </div>
              <div v-else class="text-gray-400 dark:text-gray-500 italic">{{ t('app.sysadmin.table.no_plan') }}</div>
            </div>
            <div>
              <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">{{ t('app.sysadmin.table.price') }}</div>
              <div v-if="restaurant.monthly_price !== null" class="font-medium text-gray-900 dark:text-white">
                ${{ formatMoney(restaurant.monthly_price) }}/{{ t('app.common.month') }}
              </div>
              <div v-else class="text-gray-400 dark:text-gray-500">-</div>
            </div>
          </div>

          <!-- Renewal -->
          <div v-if="restaurant.days_until_renewal !== null" class="mb-3 text-sm">
            <div class="text-xs text-gray-500 dark:text-gray-400 mb-1">{{ t('app.sysadmin.table.renewal') }}</div>
            <div class="text-gray-900 dark:text-white">
              {{ restaurant.days_until_renewal }} {{ t('app.common.days') }}
            </div>
            <div class="text-xs text-gray-500 dark:text-gray-400">
              {{ formatDate(restaurant.current_period_end) }}
            </div>
          </div>

          <!-- Action Button -->
          <button
            v-if="!restaurant.subscription_id"
            @click="openAssignModal(restaurant)"
            class="w-full px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
          >
            {{ t('app.sysadmin.actions.assign_plan') }}
          </button>
          <button
            v-else
            @click="openManageModal(restaurant)"
            class="w-full px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 transition-colors"
          >
            {{ t('app.sysadmin.actions.manage') }}
          </button>
        </div>
      </div>

      <!-- Desktop Table (>= md) -->
      <div class="hidden md:block overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                {{ t('app.sysadmin.table.restaurant') }}
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                {{ t('app.sysadmin.table.plan') }}
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                {{ t('app.sysadmin.table.status') }}
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                {{ t('app.sysadmin.table.price') }}
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                {{ t('app.sysadmin.table.renewal') }}
              </th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                {{ t('app.sysadmin.table.actions') }}
              </th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="restaurant in restaurants" :key="restaurant.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <!-- Restaurant Info -->
              <td class="px-6 py-4">
                <div class="flex items-center">
                  <div>
                    <div class="text-sm font-medium text-gray-900 dark:text-white">
                      {{ restaurant.name }}
                    </div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">
                      {{ restaurant.subdomain }}
                    </div>
                    <a 
                      :href="getRestaurantUrl(restaurant.subdomain)" 
                      target="_blank"
                      class="inline-flex items-center gap-1 text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 mt-1"
                    >
                      <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                      {{ t('app.sysadmin.actions.open_system') }}
                    </a>
                  </div>
                </div>
              </td>

              <!-- Plan -->
              <td class="px-6 py-4">
                <div v-if="restaurant.plan_name" class="text-sm">
                  <div class="font-medium text-gray-900 dark:text-white">
                    {{ restaurant.plan_name }}
                  </div>
                  <div class="text-xs text-gray-500 dark:text-gray-400">
                    {{ restaurant.plan_tier }}
                  </div>
                </div>
                <span v-else class="text-sm text-gray-400 dark:text-gray-500 italic">
                  {{ t('app.sysadmin.table.no_plan') }}
                </span>
              </td>

              <!-- Status -->
              <td class="px-6 py-4">
                <span
                  v-if="restaurant.subscription_status"
                  :class="getStatusClass(restaurant.subscription_status)"
                  class="px-2 py-1 text-xs font-semibold rounded-full"
                >
                  {{ t(`app.sysadmin.status.${restaurant.subscription_status}`) }}
                </span>
                <span v-else class="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
                  {{ t('app.sysadmin.status.none') }}
                </span>
              </td>

              <!-- Price -->
              <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                <span v-if="restaurant.monthly_price !== null">
                  ${{ formatMoney(restaurant.monthly_price) }}/{{ t('app.common.month') }}
                </span>
                <span v-else class="text-gray-400 dark:text-gray-500">-</span>
              </td>

              <!-- Renewal -->
              <td class="px-6 py-4 text-sm">
                <div v-if="restaurant.days_until_renewal !== null">
                  <div class="text-gray-900 dark:text-white">
                    {{ restaurant.days_until_renewal }} {{ t('app.common.days') }}
                  </div>
                  <div class="text-xs text-gray-500 dark:text-gray-400">
                    {{ formatDate(restaurant.current_period_end) }}
                  </div>
                </div>
                <span v-else class="text-gray-400 dark:text-gray-500">-</span>
              </td>

              <!-- Actions -->
              <td class="px-6 py-4 text-right text-sm font-medium">
                <button
                  v-if="!restaurant.subscription_id"
                  @click="openAssignModal(restaurant)"
                  class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300"
                >
                  {{ t('app.sysadmin.actions.assign_plan') }}
                </button>
                <button
                  v-else
                  @click="openManageModal(restaurant)"
                  class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300"
                >
                  {{ t('app.sysadmin.actions.manage') }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Manage Subscription Modal -->
    <ManageSubscriptionModal
      v-if="selectedRestaurant"
      :show="showManageModal"
      :restaurant="selectedRestaurant"
      @close="closeManageModal"
      @updated="handleSubscriptionUpdated"
    />

    <!-- Create Restaurant Modal -->
    <CreateRestaurantModal
      :show="showCreateModal"
      @close="closeCreateModal"
      @created="handleRestaurantCreated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import {
  BuildingStorefrontIcon,
  CheckCircleIcon,
  CurrencyDollarIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  PlusIcon
} from '@heroicons/vue/24/outline';
import ManageSubscriptionModal from '@/components/admin/ManageSubscriptionModal.vue';
import CreateRestaurantModal from '@/components/admin/CreateRestaurantModal.vue';
import { adminService } from '@/services/adminService';

const { t } = useI18n();

// State
const loading = ref(false);
const stats = ref<any>(null);
const restaurants = ref<any[]>([]);
const searchQuery = ref('');
const filterSubscription = ref<boolean | null>(null);
const selectedRestaurant = ref<any>(null);
const showManageModal = ref(false);
const showCreateModal = ref(false);

// Methods
const loadStats = async () => {
  try {
    stats.value = await adminService.getStats();
  } catch (error) {
    console.error('Error loading stats:', error);
  }
};

const loadRestaurants = async () => {
  loading.value = true;
  try {
    restaurants.value = await adminService.getRestaurants({
      search: searchQuery.value || undefined,
      has_subscription: filterSubscription.value !== null ? filterSubscription.value : undefined
    });
  } catch (error) {
    console.error('Error loading restaurants:', error);
  } finally {
    loading.value = false;
  }
};

const refreshData = async () => {
  await Promise.all([loadStats(), loadRestaurants()]);
};

let searchTimeout: any = null;
const debouncedSearch = () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    loadRestaurants();
  }, 500);
};

const openAssignModal = (restaurant: any) => {
  selectedRestaurant.value = restaurant;
  showManageModal.value = true;
};

const openManageModal = (restaurant: any) => {
  selectedRestaurant.value = restaurant;
  showManageModal.value = true;
};

const closeManageModal = () => {
  showManageModal.value = false;
  selectedRestaurant.value = null;
};

const handleSubscriptionUpdated = () => {
  closeManageModal();
  refreshData();
};

const openCreateRestaurantModal = () => {
  showCreateModal.value = true;
};

const closeCreateModal = () => {
  showCreateModal.value = false;
};

const handleRestaurantCreated = () => {
  closeCreateModal();
  refreshData();
};

const getRestaurantUrl = (subdomain: string) => {
  // Use current hostname for development, or shopacoffee.com for production
  const hostname = window.location.hostname;
  if (hostname === 'localhost' || hostname.startsWith('127.')) {
    return `http://${subdomain}.shopacoffee.local:3000`;
  }
  return `https://${subdomain}.shopacoffee.com`;
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

const formatMoney = (amount: number) => {
  return amount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
};

const formatDate = (date: string) => {
  if (!date) return '-';
  return new Date(date).toLocaleDateString();
};

// Lifecycle
onMounted(() => {
  refreshData();
});
</script>
