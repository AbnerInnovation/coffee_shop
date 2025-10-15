<template>
  <div class="sm:flex sm:items-center">
    <div class="sm:flex-auto">
      <h1 class="text-base font-semibold leading-6 text-gray-900 dark:text-gray-100">{{ title }}</h1>
      <p v-if="subtitle" class="mt-2 text-sm text-gray-700 dark:text-gray-400">
        {{ subtitle }}
      </p>
    </div>
    <div v-if="$slots.actions" class="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
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
