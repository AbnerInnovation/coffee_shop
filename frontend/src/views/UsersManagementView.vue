<template>
  <div class="min-h-screen py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-6 sm:mb-8">
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
          {{ t('app.users.title') }}
        </h1>
        <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
          {{ t('app.users.subtitle') }}
        </p>
      </div>

      <!-- Usage Stats Card -->
      <div v-if="usage" class="mb-4 sm:mb-6 bg-white dark:bg-gray-800 rounded-lg shadow p-4 sm:p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          {{ t('app.users.usage_limits') }}
        </h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <!-- Admin Users -->
          <UsageBar
            :label="t('app.subscription.admin_users')"
            :current="usage.usage?.users.admin || 0"
            :max="usage.limits?.max_admin_users || 0"
            :percentage="calculatePercentage(usage.usage?.users.admin || 0, usage.limits?.max_admin_users || 0)"
          />
          
          <!-- Waiter Users -->
          <UsageBar
            :label="t('app.subscription.waiter_users')"
            :current="usage.usage?.users.waiter || 0"
            :max="usage.limits?.max_waiter_users || 0"
            :percentage="calculatePercentage(usage.usage?.users.waiter || 0, usage.limits?.max_waiter_users || 0)"
          />
          
          <!-- Cashier Users -->
          <UsageBar
            :label="t('app.subscription.cashier_users')"
            :current="usage.usage?.users.cashier || 0"
            :max="usage.limits?.max_cashier_users || 0"
            :percentage="calculatePercentage(usage.usage?.users.cashier || 0, usage.limits?.max_cashier_users || 0)"
          />
          
          <!-- Kitchen Users -->
          <UsageBar
            :label="t('app.subscription.kitchen_users')"
            :current="usage.usage?.users.kitchen || 0"
            :max="usage.limits?.max_kitchen_users || 0"
            :percentage="calculatePercentage(usage.usage?.users.kitchen || 0, usage.limits?.max_kitchen_users || 0)"
          />
        </div>
      </div>

      <!-- Actions Bar -->
      <div class="mb-4 sm:mb-6 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <!-- Filter Dropdown -->
        <div class="relative">
          <select
            v-model="currentFilter"
            @change="filterByRole(currentFilter)"
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
          @click="openCreateModal"
          class="flex items-center justify-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors whitespace-nowrap"
        >
          <UserPlusIcon class="h-5 w-5" />
          <span class="hidden sm:inline">{{ t('app.users.create_user') }}</span>
          <span class="sm:hidden">{{ t('app.users.create_user') }}</span>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>

      <!-- Users List -->
      <div v-else>
        <!-- Desktop Table (hidden on mobile) -->
        <div class="hidden md:block bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  {{ t('app.users.table.name') }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  {{ t('app.users.table.email') }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  {{ t('app.users.table.role') }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  {{ t('app.users.table.staff_type') }}
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  {{ t('app.users.table.status') }}
                </th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  {{ t('app.users.table.actions') }}
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ user.full_name }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-500 dark:text-gray-400">
                    {{ user.email }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="getRoleBadgeClass(user.role)" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                    {{ t(`app.users.roles.${user.role}`) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span v-if="user.role === 'staff' && user.staff_type" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                    {{ t(`app.users.staff_types.${user.staff_type}`) }}
                  </span>
                  <span v-else-if="user.role === 'staff'" class="text-xs text-gray-400 dark:text-gray-500 italic">
                    {{ t('app.users.no_staff_type') }}
                  </span>
                  <span v-else class="text-xs text-gray-400 dark:text-gray-500">—</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="user.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'" class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full">
                    {{ user.is_active ? t('app.users.status.active') : t('app.users.status.inactive') }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <DropdownMenu 
                    :id="`user-menu-${user.id}`"
                    button-label="Actions" 
                    width="sm"
                  >
                    <DropdownMenuItem
                      :icon="PencilIcon"
                      variant="primary"
                      @click="openEditModal(user)"
                    >
                      {{ t('app.users.actions.edit') }}
                    </DropdownMenuItem>
                    
                    <DropdownMenuItem
                      :icon="user.is_active ? XCircleIcon : CheckCircleIcon"
                      :variant="user.is_active ? 'warning' : 'success'"
                      @click="toggleUserStatus(user)"
                    >
                      {{ user.is_active ? t('app.users.actions.deactivate') : t('app.users.actions.activate') }}
                    </DropdownMenuItem>
                    
                    <DropdownMenuDivider />
                    
                    <DropdownMenuItem
                      :icon="TrashIcon"
                      variant="danger"
                      @click="confirmDelete(user)"
                    >
                      {{ t('app.users.actions.delete') }}
                    </DropdownMenuItem>
                  </DropdownMenu>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Empty State -->
          <div v-if="users.length === 0" class="text-center py-12">
            <UserGroupIcon class="mx-auto h-12 w-12 text-gray-400" />
            <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">
              {{ t('app.users.empty_state') }}
            </h3>
          </div>
        </div>

        <!-- Mobile Cards (visible on mobile) -->
        <div class="md:hidden space-y-4">
          <div
            v-for="user in users"
            :key="user.id"
            class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 relative"
          >
            <!-- Actions Menu - Top Right -->
            <div class="absolute top-3 right-3">
              <DropdownMenu 
                :id="`user-menu-mobile-${user.id}`"
                button-label="Actions" 
                width="sm"
              >
                <DropdownMenuItem
                  :icon="PencilIcon"
                  variant="primary"
                  @click="openEditModal(user)"
                >
                  {{ t('app.users.actions.edit') }}
                </DropdownMenuItem>
                
                <DropdownMenuItem
                  :icon="user.is_active ? XCircleIcon : CheckCircleIcon"
                  :variant="user.is_active ? 'warning' : 'success'"
                  @click="toggleUserStatus(user)"
                >
                  {{ user.is_active ? t('app.users.actions.deactivate') : t('app.users.actions.activate') }}
                </DropdownMenuItem>
                
                <DropdownMenuDivider />
                
                <DropdownMenuItem
                  :icon="TrashIcon"
                  variant="danger"
                  @click="confirmDelete(user)"
                >
                  {{ t('app.users.actions.delete') }}
                </DropdownMenuItem>
              </DropdownMenu>
            </div>

            <!-- User Info -->
            <div class="pr-10">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                {{ user.full_name }}
              </h3>
              <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">
                {{ user.email }}
              </p>

              <!-- Badges Row -->
              <div class="flex flex-wrap gap-2 mb-3">
                <span :class="getRoleBadgeClass(user.role)" class="px-2 py-1 text-xs font-semibold rounded-full">
                  {{ t(`app.users.roles.${user.role}`) }}
                </span>
                
                <span v-if="user.role === 'staff' && user.staff_type" class="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                  {{ t(`app.users.staff_types.${user.staff_type}`) }}
                </span>
                
                <span :class="user.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'" class="px-2 py-1 text-xs font-semibold rounded-full">
                  {{ user.is_active ? t('app.users.status.active') : t('app.users.status.inactive') }}
                </span>
              </div>
            </div>
          </div>

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
import { ref, onMounted, reactive } from 'vue';
import { useI18n } from 'vue-i18n';
import {
  UserPlusIcon,
  UserGroupIcon,
  PencilIcon,
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/vue/24/outline';
import restaurantUsersService, { type RestaurantUser } from '@/services/restaurantUsersService';
import { subscriptionService, type SubscriptionUsage } from '@/services/subscriptionService';
import UsageBar from '@/components/subscription/UsageBar.vue';
import DropdownMenu from '@/components/ui/DropdownMenu.vue';
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue';
import DropdownMenuDivider from '@/components/ui/DropdownMenuDivider.vue';
import UserFormModal from '@/components/users/UserFormModal.vue';

const { t } = useI18n();

const users = ref<RestaurantUser[]>([]);
const usage = ref<SubscriptionUsage | null>(null);
const loading = ref(false);
const currentFilter = ref('all');

const isModalOpen = ref(false);
const modalMode = ref<'create' | 'edit'>('create');
const selectedUser = ref<RestaurantUser | null>(null);

onMounted(() => {
  loadUsers();
  loadUsage();
});

async function loadUsers() {
  loading.value = true;
  try {
    users.value = await restaurantUsersService.getUsers();
  } catch (error) {
    console.error('Error loading users:', error);
  } finally {
    loading.value = false;
  }
}

async function loadUsage() {
  try {
    usage.value = await subscriptionService.getUsage();
  } catch (error) {
    console.error('Error loading usage:', error);
  }
}

function calculatePercentage(current: number, max: number): number {
  if (max === -1 || max === 0) return 0;
  return Math.round((current / max) * 100);
}

async function filterByRole(role: string) {
  currentFilter.value = role;
  loading.value = true;
  try {
    if (role === 'all') {
      users.value = await restaurantUsersService.getUsers();
    } else {
      users.value = await restaurantUsersService.getUsersByRole(role);
    }
  } catch (error) {
    console.error('Error filtering users:', error);
  } finally {
    loading.value = false;
  }
}

function openCreateModal() {
  modalMode.value = 'create';
  selectedUser.value = null;
  isModalOpen.value = true;
}

function openEditModal(user: RestaurantUser) {
  modalMode.value = 'edit';
  selectedUser.value = user;
  isModalOpen.value = true;
}

function closeModal() {
  isModalOpen.value = false;
  selectedUser.value = null;
}

function handleUserSaved() {
  closeModal();
  loadUsers();
  loadUsage();
}

async function toggleUserStatus(user: RestaurantUser) {
  try {
    await restaurantUsersService.updateUser(user.id, {
      is_active: !user.is_active
    });
    await loadUsers();
  } catch (error: any) {
    console.error('Error toggling user status:', error);
    alert(error.response?.data?.detail || t('app.users.errors.toggle_status_failed'));
  }
}

async function confirmDelete(user: RestaurantUser) {
  if (confirm(t('app.users.confirm_delete', { name: user.full_name }))) {
    try {
      await restaurantUsersService.deleteUser(user.id);
      await loadUsers();
      await loadUsage();
    } catch (error: any) {
      console.error('Error deleting user:', error);
      alert(error.response?.data?.detail || t('app.users.errors.delete_failed'));
    }
  }
}

function getRoleBadgeClass(role: string): string {
  const classes: Record<string, string> = {
    admin: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    staff: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    customer: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
    sysadmin: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
  };
  return classes[role] || classes.customer;
}
</script>
