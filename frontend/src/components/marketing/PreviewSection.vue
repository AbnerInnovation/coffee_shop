<template>
  <section class="grid md:grid-cols-2 gap-8 lg:gap-12 items-center">
    <div :class="['relative', isReversed ? 'md:order-2' : 'md:order-1']">
      <img
        :src="imageUrl"
        :alt="title || 'Vista previa'"
        class="w-full h-auto object-cover rounded-3xl shadow-2xl ring-1 ring-black/5 dark:ring-white/10"
        loading="lazy"
      />
      <div class="pointer-events-none absolute -inset-4 rounded-[2rem] blur-3xl opacity-20 bg-gradient-to-br from-indigo-400/30 to-sky-400/20 dark:from-indigo-500/10 dark:to-sky-500/10"></div>
    </div>
    
    <div :class="[isReversed ? 'md:order-1' : 'md:order-2']">
      <h3 class="text-2xl md:text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
        {{ title }}
      </h3>
      <p class="mt-3 text-slate-600 dark:text-slate-300 text-base md:text-lg leading-relaxed">
        {{ caption }}
      </p>
      <div class="mt-6 h-px bg-gradient-to-r from-transparent via-slate-200 dark:via-slate-700 to-transparent"></div>
    </div>
  </section>
</template>

<script setup lang="ts">
interface Props {
  imageUrl: string
  title: string
  caption: string
  isReversed?: boolean
}

defineProps<Props>()
</script>
