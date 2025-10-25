<template>
  <div class="mb-6 grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
    <button
      v-for="action in actions"
      :key="action.name"
      @click="action.onClick"
      :class="[
        'flex items-center justify-center gap-2 rounded-lg px-3 py-3 sm:px-4 text-sm font-semibold text-white shadow-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 touch-manipulation',
        action.colorClass
      ]"
    >
      <component :is="action.icon" class="h-5 w-5" />
      <span class="hidden sm:inline">{{ action.label }}</span>
      <span class="sm:hidden">{{ action.shortLabel }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { PlusIcon, BanknotesIcon, FireIcon, DocumentPlusIcon } from '@heroicons/vue/24/outline';

const router = useRouter();
const { t } = useI18n();

const emit = defineEmits<{
  newOrder: []
}>();

const actions = computed(() => [
  {
    name: 'new-order',
    label: t('app.dashboard.quick_actions.new_order'),
    shortLabel: t('app.dashboard.quick_actions.new_order').split(' ')[0],
    icon: PlusIcon,
    colorClass: 'bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 focus-visible:outline-indigo-600',
    onClick: () => emit('newOrder')
  },
  {
    name: 'cash-register',
    label: t('app.dashboard.quick_actions.cash_register'),
    shortLabel: t('app.dashboard.quick_actions.cash_register').split(' ')[0],
    icon: BanknotesIcon,
    colorClass: 'bg-green-600 hover:bg-green-500 active:bg-green-700 focus-visible:outline-green-600',
    onClick: () => router.push('/cash-register')
  },
  {
    name: 'kitchen',
    label: t('app.dashboard.quick_actions.kitchen'),
    shortLabel: t('app.dashboard.quick_actions.kitchen').split(' ')[0],
    icon: FireIcon,
    colorClass: 'bg-orange-600 hover:bg-orange-500 active:bg-orange-700 focus-visible:outline-orange-600',
    onClick: () => router.push('/kitchen')
  },
  {
    name: 'menu',
    label: t('app.dashboard.quick_actions.add_menu_item'),
    shortLabel: 'Menu',
    icon: DocumentPlusIcon,
    colorClass: 'bg-purple-600 hover:bg-purple-500 active:bg-purple-700 focus-visible:outline-purple-600',
    onClick: () => router.push('/menu')
  }
]);
</script>
