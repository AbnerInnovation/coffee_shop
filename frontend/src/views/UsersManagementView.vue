<template>
  <div class="min-h-screen py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          {{ t('app.users.title') }}
        </h1>
        <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
          {{ t('app.users.subtitle') }}
        </p>
      </div>

      <!-- Usage Stats Card -->
      <div v-if="usage" class="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          {{ t('app.users.usage_limits') }}
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <UsageBar
            :label="t('app.subscription.admin_users')"
            :current="usage.usage?.users.admin || 0"
            :max="usage.limits?.max_admin_users || 0"
          />
          <UsageBar
            :label="t('app.subscription.staff_users')"
            :current="(usage.usage?.users as any)?.staff || 0"
            :max="(usage.limits as any)?.max_staff_users || -1"
          />
          <UsageBar
            :label="t('app.subscription.customer_users')"
            :current="(usage.usage?.users as any)?.customer || 0"
            :max="(usage.limits as any)?.max_customer_users || -1"
          />
        </div>
      </div>

      <!-- Actions Bar -->
      <div class="mb-6 flex justify-between items-center">
        <div class="flex gap-2">
          <button
            v-for="role in ['all', 'admin', 'staff', 'customer']"
            :key="role"
            @click="filterByRole(role)"
            :class="[
              'px-4 py-2 rounded-lg font-medium transition-colors',
              currentFilter === role
                ? 'bg-indigo-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
            ]"
          >
            {{ t(`app.users.filter_${role}`) }}
          </button>
        </div>
        
        <button
          @click="openCreateModal"
          class="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        >
          <UserPlusIcon class="h-5 w-5" />
          {{ t('app.users.create_user') }}
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>

      <!-- Users Table -->
      <div v-else class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
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
                <DropdownMenu v-model="openMenus[user.id]" button-label="Actions" width="sm">
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
const openMenus = reactive<Record<number, boolean>>({});

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
