<template>
  <div class="min-h-screen p-4 sm:p-6">
    <!-- Header -->
    <div class="mb-6 sm:mb-8">
      <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
        {{ t('app.sysadmin.title') }}
      </h1>
      <p class="mt-2 text-sm sm:text-base text-gray-600 dark:text-gray-400">
        {{ t('app.sysadmin.subtitle') }}
      </p>
    </div>

    <!-- Stats Cards -->
    <RestaurantStatsGrid v-if="stats" :stats="stats" />

    <!-- Filters and Search -->
    <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 sm:p-6 mb-6">
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
    <div class="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
      <!-- Loading State -->
      <div v-if="loading" class="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
        <ArrowPathIcon class="h-8 w-8 animate-spin mx-auto mb-2" />
        {{ t('app.common.loading') }}
      </div>

      <!-- Empty State -->
      <div v-else-if="!restaurants || restaurants.length === 0" class="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
        {{ t('app.sysadmin.table.no_results') }}
      </div>

      <!-- Content -->
      <template v-else>
        <!-- Mobile Cards (< md) -->
        <div class="md:hidden">
          <RestaurantCard
            v-for="restaurant in restaurants"
            :key="restaurant.id"
            :restaurant="restaurant"
            @action="handleRestaurantAction"
          />
        </div>

        <!-- Desktop Table (>= md) -->
        <div class="hidden md:block">
          <RestaurantsTable
            :restaurants="restaurants"
            @action="handleRestaurantAction"
          />
        </div>
      </template>
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
import { onMounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { ArrowPathIcon, PlusIcon } from '@heroicons/vue/24/outline';
import { useRestaurants } from '@/composables/useRestaurants';
import { useRestaurantStats } from '@/composables/useRestaurantStats';
import RestaurantStatsGrid from '@/components/sysadmin/RestaurantStatsGrid.vue';
import RestaurantCard from '@/components/sysadmin/RestaurantCard.vue';
import RestaurantsTable from '@/components/sysadmin/RestaurantsTable.vue';
import ManageSubscriptionModal from '@/components/admin/ManageSubscriptionModal.vue';
import CreateRestaurantModal from '@/components/admin/CreateRestaurantModal.vue';

const { t } = useI18n();

// Composables
const {
  restaurants,
  loading,
  searchQuery,
  filterSubscription,
  loadRestaurants,
  debouncedSearch
} = useRestaurants();

const {
  stats,
  loadStats
} = useRestaurantStats();

// Modal state
const selectedRestaurant = ref<any>(null);
const showManageModal = ref(false);
const showCreateModal = ref(false);

// Handlers
const handleRestaurantAction = (restaurant: any) => {
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

const refreshData = async () => {
  await Promise.all([loadStats(), loadRestaurants()]);
};

// Initialize
onMounted(() => {
  refreshData();
});
</script>
