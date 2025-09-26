<template>
  <button
    type="button"
    class="text-red-600 hover:text-red-800 dark:text-red-400"
    @click="handleClick"
  >
    <slot>{{ label }}</slot>
  </button>
</template>

<script setup lang="ts">
import { useConfirm } from '@/composables/useConfirm';
import { useI18n } from 'vue-i18n';

const props = withDefaults(defineProps<{
  label?: string;
  title?: string;
  message?: string;
  confirmText?: string;
  cancelText?: string;
  confirmClass?: string;
}>(), {
  label: 'Delete',
  title: 'Delete',
  message: 'Are you sure?',
  confirmText: 'Delete',
  cancelText: 'Cancel',
  confirmClass: 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
});

const emit = defineEmits<{ (e: 'confirm'): void }>();

const { confirm } = useConfirm();
const { t } = useI18n();

async function handleClick() {
  const confirmed = await confirm(
    props.title || t('app.actions.delete') as string,
    props.message || '',
    props.confirmText,
    props.cancelText,
    props.confirmClass
  );
  if (confirmed) emit('confirm');
}
</script>
