<template>
  <article
    :class="[
      'group border rounded-2xl p-6 flex flex-col h-full transition-all duration-200 bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700',
      highlight
        ? 'border-2 border-indigo-200 dark:border-indigo-700 bg-indigo-50/60 dark:bg-indigo-900/30 shadow-sm'
        : 'hover:shadow-md hover:-translate-y-0.5',
    ]"
  >
    <div class="flex-1">
      <div class="flex items-start justify-between gap-3">
        <div>
          <h2 class="text-xl font-semibold text-slate-900 dark:text-slate-100">{{ title }}</h2>
          <p class="text-sm text-gray-500 dark:text-slate-400">{{ subtitle }}</p>
        </div>
        <span
          v-if="highlight"
          class="text-xs px-2 py-1 rounded-full bg-indigo-600 text-white shadow-sm"
        >Popular</span>
      </div>

      <div class="mt-6">
        <div class="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-slate-100">{{ price }}</div>
        <div class="mt-4 h-px bg-gradient-to-r from-transparent via-gray-200 dark:via-slate-700 to-transparent"></div>
        <ul class="mt-4 text-sm space-y-2 text-slate-700 dark:text-slate-300">
          <li v-for="(f, i) in features" :key="i" class="flex items-start gap-2">
            <span class="mt-[2px] text-green-600 dark:text-green-400">✓</span>
            <span>{{ f }}</span>
          </li>
        </ul>
      </div>
    </div>

    <div class="mt-6">
      <RouterLink
        :to="{ name: ctaRouteName }"
        class="block text-center rounded-lg py-2.5 px-4 bg-indigo-600 text-white font-medium hover:bg-indigo-700 transition shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-white dark:focus:ring-offset-slate-900"
      >
        {{ ctaLabel }}
      </RouterLink>
    </div>
  </article>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'

interface Props {
  title: string
  subtitle: string
  price: string
  features: string[]
  highlight?: boolean
  ctaLabel?: string
  ctaRouteName?: string
}

withDefaults(defineProps<Props>(), {
  highlight: false,
  ctaLabel: 'Probar gratis',
  ctaRouteName: 'Register',
})
</script>
