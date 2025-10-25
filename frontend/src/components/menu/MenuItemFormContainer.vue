<template>
  <div class="fixed inset-0 z-[10001] overflow-y-auto bg-white dark:bg-gray-900 sm:relative sm:z-0 sm:bg-transparent">
    <div class="min-h-screen sm:min-h-0">
      <div class="sm:rounded-lg sm:bg-white sm:dark:bg-gray-900 sm:shadow">
        <div class="px-4 py-4 sm:p-6">
          <MenuItemForm
            v-if="currentItem !== null"
            :menu-item="currentItem"
            :loading="formLoading"
            :errors="formErrors"
            :is-editing="true"
            @submit="$emit('submit', $event)"
            @cancel="$emit('cancel')"
          />
          <MenuItemForm
            v-else
            :loading="formLoading"
            :errors="formErrors"
            :is-editing="false"
            @submit="$emit('submit', $event)"
            @cancel="$emit('cancel')"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import MenuItemForm from './MenuItemForm.vue';
import type { MenuItem } from '@/types/menu';

defineProps<{
  currentItem: MenuItem | null;
  formLoading: boolean;
  formErrors: Record<string, string>;
}>();

defineEmits<{
  submit: [formData: Omit<MenuItem, 'id'>];
  cancel: [];
}>();
</script>
