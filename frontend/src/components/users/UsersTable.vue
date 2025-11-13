<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
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
                @click="$emit('edit', user)"
              >
                {{ t('app.users.actions.edit') }}
              </DropdownMenuItem>
              
              <DropdownMenuItem
                :icon="user.is_active ? XCircleIcon : CheckCircleIcon"
                :variant="user.is_active ? 'warning' : 'success'"
                @click="$emit('toggle-status', user)"
              >
                {{ user.is_active ? t('app.users.actions.deactivate') : t('app.users.actions.activate') }}
              </DropdownMenuItem>
              
              <DropdownMenuDivider />
              
              <DropdownMenuItem
                :icon="TrashIcon"
                variant="danger"
                @click="$emit('delete', user)"
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
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { PencilIcon, TrashIcon, CheckCircleIcon, XCircleIcon, UserGroupIcon } from '@heroicons/vue/24/outline';
import DropdownMenu from '@/components/ui/DropdownMenu.vue';
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue';
import DropdownMenuDivider from '@/components/ui/DropdownMenuDivider.vue';
import type { RestaurantUser } from '@/services/restaurantUsersService';

interface Props {
  users: RestaurantUser[];
}

defineProps<Props>();

defineEmits<{
  'edit': [user: RestaurantUser];
  'toggle-status': [user: RestaurantUser];
  'delete': [user: RestaurantUser];
}>();

const { t } = useI18n();

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
