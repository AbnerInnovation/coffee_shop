<template>
  <div class="min-h-screen py-4 sm:py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-4 sm:mb-6">
        <h1 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
          {{ t('app.users.title') }}
        </h1>
        <p class="mt-1 text-xs sm:text-sm text-gray-600 dark:text-gray-400">
          {{ t('app.users.subtitle') }}
        </p>
      </div>

      <!-- Usage Stats Card -->
      <div v-if="usage" class="mb-3 sm:mb-4 bg-white dark:bg-gray-800 rounded-lg shadow p-3 sm:p-4">
        <h2 class="text-base font-semibold text-gray-900 dark:text-white mb-3">
          {{ t('app.users.usage_limits') }}
        </h2>
        <div class="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-3">
          <UsageBar
            :label="t('app.subscription.admin_users')"
            :current="usage.usage?.users.admin || 0"
            :max="usage.limits?.max_admin_users || 0"
            :percentage="calculatePercentage(usage.usage?.users.admin || 0, usage.limits?.max_admin_users || 0)"
          />
          
          <UsageBar
            :label="t('app.subscription.waiter_users')"
            :current="usage.usage?.users.waiter || 0"
            :max="usage.limits?.max_waiter_users || 0"
            :percentage="calculatePercentage(usage.usage?.users.waiter || 0, usage.limits?.max_waiter_users || 0)"
          />
          
          <UsageBar
            :label="t('app.subscription.cashier_users')"
            :current="usage.usage?.users.cashier || 0"
            :max="usage.limits?.max_cashier_users || 0"
            :percentage="calculatePercentage(usage.usage?.users.cashier || 0, usage.limits?.max_cashier_users || 0)"
          />
          
          <UsageBar
            :label="t('app.subscription.kitchen_users')"
            :current="usage.usage?.users.kitchen || 0"
            :max="usage.limits?.max_kitchen_users || 0"
            :percentage="calculatePercentage(usage.usage?.users.kitchen || 0, usage.limits?.max_kitchen_users || 0)"
          />
        </div>
      </div>

      <!-- Actions Bar -->
      <div class="mb-3 sm:mb-4 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3">
        <!-- Filter Dropdown -->
        <div class="relative">
          <select
            v-model="currentFilter"
            @change="handleFilterChange"
            class="block w-full sm:w-auto px-4 py-2 pr-10 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors appearance-none cursor-pointer"
          >
            <option value="all">{{ t('app.users.filter_all') }}</option>
            <option value="admin">{{ t('app.users.filter_admin') }}</option>
            <option value="staff">{{ t('app.users.filter_staff') }}</option>
            <option value="customer">{{ t('app.users.filter_customer') }}</option>
          </select>
          <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-gray-500 dark:text-gray-400">
            <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </div>
        </div>
        
        <!-- Create Button -->
        <button
          @click="handleCreateUser"
          class="flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors whitespace-nowrap"
        >
          <UserPlusIcon class="h-5 w-5" />
          <span>{{ t('app.users.create_user') }}</span>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>

      <!-- Users List -->
      <div v-else>
        <!-- Desktop Table -->
        <div class="hidden md:block">
          <UsersTable
            :users="users"
            @edit="handleEditUser"
            @toggle-status="handleToggleStatus"
            @delete="handleDeleteUser"
          />
        </div>

        <!-- Mobile Cards -->
        <div class="md:hidden space-y-3">
          <UserCard
            v-for="user in users"
            :key="user.id"
            :user="user"
            @edit="handleEditUser"
            @toggle-status="handleToggleStatus"
            @delete="handleDeleteUser"
          />

          <!-- Empty State -->
          <div v-if="users.length === 0" class="bg-white dark:bg-gray-800 rounded-lg shadow text-center py-12">
            <UserGroupIcon class="mx-auto h-12 w-12 text-gray-400" />
            <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">
              {{ t('app.users.empty_state') }}
            </h3>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit User Modal -->
    <UserFormModal
      :is-open="isModalOpen"
      :user="selectedUser"
      :mode="modalMode"
      @close="closeModal"
      @saved="handleUserSaved"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useToast } from 'vue-toastification';
import { UserPlusIcon, UserGroupIcon } from '@heroicons/vue/24/outline';
import { useUsers } from '@/composables/useUsers';
import { useSubscriptionUsage } from '@/composables/useSubscriptionUsage';
import { useConfirm } from '@/composables/useConfirm';
import UsageBar from '@/components/subscription/UsageBar.vue';
import UserCard from '@/components/users/UserCard.vue';
import UsersTable from '@/components/users/UsersTable.vue';
import UserFormModal from '@/components/users/UserFormModal.vue';
import type { RestaurantUser } from '@/services/restaurantUsersService';

const { t } = useI18n();
const toast = useToast();
const { confirm } = useConfirm();

// Composables
const {
  users,
  loading,
  currentFilter,
  loadUsers,
  filterByRole,
  toggleUserStatus,
  deleteUser
} = useUsers();

const {
  usage,
  loadUsage,
  calculatePercentage
} = useSubscriptionUsage();

// Modal state
const isModalOpen = ref(false);
const modalMode = ref<'create' | 'edit'>('create');
const selectedUser = ref<RestaurantUser | null>(null);

// Initialize
onMounted(() => {
  loadUsers();
  loadUsage();
});

// Handlers
const handleFilterChange = () => {
  filterByRole(currentFilter.value);
};

const handleCreateUser = () => {
  modalMode.value = 'create';
  selectedUser.value = null;
  isModalOpen.value = true;
};

const handleEditUser = (user: RestaurantUser) => {
  modalMode.value = 'edit';
  selectedUser.value = user;
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
  selectedUser.value = null;
};

const handleUserSaved = () => {
  closeModal();
  loadUsers();
  loadUsage();
};

const handleToggleStatus = async (user: RestaurantUser) => {
  const result = await toggleUserStatus(user);
  
  if (result.success) {
    toast.success(
      result.wasActive 
        ? t('app.users.success.deactivated') 
        : t('app.users.success.activated')
    );
  } else {
    toast.error(t('app.users.errors.toggle_status_failed'));
  }
};

const handleDeleteUser = async (user: RestaurantUser) => {
  const confirmed = await confirm(
    t('app.users.confirm_delete_title'),
    t('app.users.confirm_delete_message', { name: user.full_name }),
    t('app.actions.delete'),
    t('app.actions.cancel'),
    'bg-red-600 hover:bg-red-700 focus:ring-red-500'
  );

  if (confirmed) {
    const result = await deleteUser(user.id);
    
    if (result.success) {
      await loadUsage();
      toast.success(t('app.users.success.deleted'));
    } else {
      toast.error(t('app.users.errors.delete_failed'));
    }
  }
};
</script>
