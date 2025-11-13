<template>
  <div class="py-4 sm:py-6">
    <div class="max-w-3xl mx-auto px-3 sm:px-4 lg:px-6">
      <!-- Header -->
      <div class="mb-4 sm:mb-6">
        <h1 class="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white">
          {{ t('app.profile.title') }}
        </h1>
        <p class="mt-1 text-xs sm:text-sm text-gray-600 dark:text-gray-400">
          {{ t('app.profile.subtitle') }}
        </p>
      </div>

      <!-- Profile Card -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <!-- Avatar Section -->
        <div class="bg-gradient-to-r from-indigo-500 to-purple-600 px-4 py-6 sm:px-6 sm:py-8">
          <div class="flex items-center">
            <div class="h-16 w-16 sm:h-20 sm:w-20 rounded-full bg-white dark:bg-gray-700 flex items-center justify-center text-xl sm:text-2xl font-bold text-indigo-600 dark:text-indigo-400">
              {{ userInitials }}
            </div>
            <div class="ml-4 sm:ml-6">
              <h2 class="text-xl sm:text-2xl font-bold text-white">{{ user?.full_name || user?.name }}</h2>
              <p class="text-sm sm:text-base text-indigo-100">{{ user?.email }}</p>
            </div>
          </div>
        </div>

        <!-- Profile Information -->
        <div class="px-4 py-4 sm:px-6 sm:py-6">
          <div class="grid grid-cols-2 gap-3 sm:gap-4">
            <!-- Full Name -->
            <ProfileField 
              :label="t('app.profile.fields.full_name')" 
              :value="user?.full_name || user?.name"
              full-width
            />

            <!-- Email -->
            <ProfileField 
              :label="t('app.profile.fields.email')" 
              :value="user?.email"
              full-width
            />

            <!-- Role -->
            <ProfileField :label="t('app.profile.fields.role')">
              <div class="flex items-center gap-1.5 flex-wrap">
                <ProfileBadge 
                  :variant="getRoleBadgeVariant(user?.role)"
                  :label="t(`app.users.roles.${user?.role}`)"
                />
                <ProfileBadge 
                  v-if="user?.role === 'staff' && user?.staff_type"
                  variant="staff"
                  :label="t(`app.users.staff_types.${user?.staff_type}`)"
                />
              </div>
            </ProfileField>

            <!-- Status -->
            <ProfileField :label="t('app.profile.fields.status')">
              <ProfileBadge 
                :variant="getStatusBadgeVariant(user?.is_active)"
                :label="user?.is_active ? t('app.users.status.active') : t('app.users.status.inactive')"
              />
            </ProfileField>

            <!-- Created At -->
            <ProfileField 
              :label="t('app.profile.fields.member_since')" 
              :value="formatDate(user?.created_at)"
              full-width
            />
          </div>
        </div>

        <!-- Actions -->
        <div class="px-4 py-3 sm:px-6 sm:py-4 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600">
          <button
            @click="openChangePasswordModal"
            class="w-full sm:w-auto px-4 py-2 text-sm bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center justify-center gap-2"
          >
            <KeyIcon class="h-4 w-4 sm:h-5 sm:w-5" />
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
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { KeyIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'
import { useToast } from '@/composables/useToast'
import { useProfileHelpers } from '@/composables/useProfileHelpers'
import ChangePasswordModal from '@/components/profile/ChangePasswordModal.vue'
import ProfileField from '@/components/profile/ProfileField.vue'
import ProfileBadge from '@/components/profile/ProfileBadge.vue'

const { t } = useI18n()
const authStore = useAuthStore()
const { showSuccess } = useToast()

const showChangePasswordModal = ref(false)
const user = computed(() => authStore.user)

const { 
  userInitials, 
  formatDate, 
  getRoleBadgeVariant, 
  getStatusBadgeVariant 
} = useProfileHelpers(user)

function openChangePasswordModal() {
  showChangePasswordModal.value = true
}

function handlePasswordChanged() {
  showSuccess(t('app.profile.change_password.success'))
}
</script>
