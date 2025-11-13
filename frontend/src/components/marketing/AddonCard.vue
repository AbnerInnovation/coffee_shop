<template>
  <div class="p-6 border rounded-2xl bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 hover:shadow-md transition">
    <h3 class="font-semibold text-slate-900 dark:text-slate-100">{{ title }}</h3>
    <p class="text-sm text-gray-600 dark:text-slate-400 mt-2">{{ description }}</p>
    
    <ul v-if="items" class="mt-3 text-sm space-y-1">
      <li v-for="(item, idx) in items" :key="idx" class="text-slate-700 dark:text-slate-300">
        • {{ item }}
      </li>
    </ul>
    
    <div v-else-if="price" class="mt-4 text-lg font-extrabold text-slate-900 dark:text-slate-100">
      {{ price }}
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string
  description: string
  items?: string[]
  price?: string
}

defineProps<Props>()
</script>
