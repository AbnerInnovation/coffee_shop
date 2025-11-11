<template>
  <div class="flex items-center justify-between gap-3">
    <div class="flex-1 min-w-0">
      <h1 class="text-base font-semibold leading-6 text-gray-900 dark:text-gray-100">{{ title }}</h1>
      <p v-if="subtitle" class="hidden sm:block mt-2 text-sm text-gray-700 dark:text-gray-400">
        {{ subtitle }}
      </p>
    </div>
    <div v-if="$slots.actions" class="flex-shrink-0">
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string;
  subtitle?: string;
}

defineProps<Props>();
</script>
