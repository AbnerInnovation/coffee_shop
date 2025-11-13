<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-3 relative">
    <!-- Actions Menu - Top Right -->
    <div class="absolute top-2 right-2">
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
    </div>

    <!-- User Info -->
    <div class="pr-8">
      <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-0.5">
        {{ user.full_name }}
      </h3>
      <p class="text-xs text-gray-500 dark:text-gray-400 mb-2">
        {{ user.email }}
      </p>

      <!-- Badges Row -->
      <div class="flex flex-wrap gap-1.5">
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
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { PencilIcon, TrashIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/vue/24/outline';
import DropdownMenu from '@/components/ui/DropdownMenu.vue';
import DropdownMenuItem from '@/components/ui/DropdownMenuItem.vue';
import DropdownMenuDivider from '@/components/ui/DropdownMenuDivider.vue';
import type { RestaurantUser } from '@/services/restaurantUsersService';

interface Props {
  user: RestaurantUser;
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
