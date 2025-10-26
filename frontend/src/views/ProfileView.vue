<template>
  <div class="min-h-screen py-8">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-6 sm:mb-8">
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
          {{ t('app.profile.title') }}
        </h1>
        <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
          {{ t('app.profile.subtitle') }}
        </p>
      </div>

      <!-- Profile Card -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <!-- Avatar Section -->
        <div class="bg-gradient-to-r from-indigo-500 to-purple-600 px-6 py-8">
          <div class="flex items-center">
            <div class="h-20 w-20 rounded-full bg-white dark:bg-gray-700 flex items-center justify-center text-2xl font-bold text-indigo-600 dark:text-indigo-400">
              {{ userInitials }}
            </div>
            <div class="ml-6">
              <h2 class="text-2xl font-bold text-white">{{ user?.full_name || user?.name }}</h2>
              <p class="text-indigo-100">{{ user?.email }}</p>
            </div>
          </div>
        </div>

        <!-- Profile Information -->
        <div class="px-6 py-6 space-y-6">
          <!-- Full Name -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ t('app.profile.fields.full_name') }}
            </label>
            <div class="text-base text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-700 px-4 py-3 rounded-lg">
              {{ user?.full_name || user?.name || '-' }}
            </div>
          </div>

          <!-- Email -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ t('app.profile.fields.email') }}
            </label>
            <div class="text-base text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-700 px-4 py-3 rounded-lg">
              {{ user?.email || '-' }}
            </div>
          </div>

          <!-- Role -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ t('app.profile.fields.role') }}
            </label>
            <div class="flex items-center gap-2">
              <span :class="getRoleBadgeClass(user?.role)" class="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold">
                {{ t(`app.users.roles.${user?.role}`) }}
              </span>
              <span v-if="user?.role === 'staff' && user?.staff_type" class="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                {{ t(`app.users.staff_types.${user?.staff_type}`) }}
              </span>
            </div>
          </div>

          <!-- Status -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ t('app.profile.fields.status') }}
            </label>
            <span :class="user?.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'" class="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold">
              {{ user?.is_active ? t('app.users.status.active') : t('app.users.status.inactive') }}
            </span>
          </div>

          <!-- Created At -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              {{ t('app.profile.fields.member_since') }}
            </label>
            <div class="text-base text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-700 px-4 py-3 rounded-lg">
              {{ formatDate(user?.created_at) }}
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="px-6 py-4 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600">
          <button
            @click="openChangePasswordModal"
            class="w-full sm:w-auto px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
          >
            <KeyIcon class="h-5 w-5" />
            {{ t('app.profile.change_password.button') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Change Password Modal -->
    <ChangePasswordModal
      :show="showChangePasswordModal"
      @close="showChangePasswordModal = false"
      @success="handlePasswordChanged"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { KeyIcon } from '@heroicons/vue/24/outline';
import { useAuthStore } from '@/stores/auth';
import { useToast } from '@/composables/useToast';
import ChangePasswordModal from '@/components/profile/ChangePasswordModal.vue';

const { t } = useI18n();
const authStore = useAuthStore();
const { showSuccess } = useToast();

const showChangePasswordModal = ref(false);

const user = computed(() => authStore.user);

const userInitials = computed(() => {
  if (!user.value) return 'U';
  const name = user.value.full_name || user.value.name || user.value.email;
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .substring(0, 2);
});

function getRoleBadgeClass(role: string | undefined): string {
  switch (role) {
    case 'sysadmin':
      return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
    case 'admin':
      return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
    case 'staff':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
    case 'customer':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
    default:
      return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
  }
}

function formatDate(dateString: string | undefined): string {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

function openChangePasswordModal() {
  showChangePasswordModal.value = true;
}

function handlePasswordChanged() {
  showSuccess(t('app.profile.change_password.success'));
}

</script>
