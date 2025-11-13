<template>
  <div class="flex items-start gap-4 p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:shadow-lg hover:border-indigo-200 dark:hover:border-indigo-800 transition-all duration-200">
    <div class="flex-shrink-0 w-12 h-12 rounded-xl bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
      <span class="text-2xl">{{ icon }}</span>
    </div>
    <div>
      <h3 class="font-semibold text-slate-900 dark:text-slate-100 mb-1">{{ title }}</h3>
      <p class="text-sm text-slate-600 dark:text-slate-400">{{ description }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  icon: string
  title: string
  description: string
}

defineProps<Props>()
</script>
