<template>
  <div class="relative w-full overflow-hidden rounded-2xl border bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700">
    <div class="aspect-[16/9] relative">
      <transition name="fade" mode="out-in">
        <div :key="current" class="absolute inset-0">
          <img
            v-if="slides[current]?.imageUrl"
            :src="slides[current].imageUrl"
            :alt="slides[current]?.title || 'Preview'"
            class="w-full h-full object-cover"
            loading="lazy"
          />
          <div v-else class="w-full h-full grid place-items-center bg-gradient-to-br from-indigo-50 to-sky-50 dark:from-slate-800 dark:to-slate-900">
            <div class="text-center">
              <div class="text-2xl font-bold text-slate-900 dark:text-slate-100">{{ slides[current]?.title || 'Vista previa' }}</div>
              <p class="text-sm text-slate-600 dark:text-slate-300 mt-1">
                {{ slides[current]?.caption || 'Próximamente' }}
              </p>
            </div>
          </div>

          <div class="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/50 to-transparent">
            <div class="text-white">
              <div class="font-semibold">{{ slides[current]?.title }}</div>
              <div class="text-sm opacity-90">{{ slides[current]?.caption }}</div>
            </div>
          </div>
        </div>
      </transition>
    </div>

    <button @click="prev" class="absolute left-2 top-1/2 -translate-y-1/2 p-2 rounded-full bg-white/90 dark:bg-slate-800/80 shadow hover:bg-white dark:hover:bg-slate-800">
      <span class="sr-only">Anterior</span>
      ‹
    </button>
    <button @click="next" class="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-full bg-white/90 dark:bg-slate-800/80 shadow hover:bg-white dark:hover:bg-slate-800">
      <span class="sr-only">Siguiente</span>
      ›
    </button>

    <div class="absolute bottom-3 left-0 right-0 flex items-center justify-center gap-2">
      <button
        v-for="(s, i) in slides"
        :key="i"
        @click="go(i)"
        :class="[
          'h-2.5 w-2.5 rounded-full transition',
          i === current ? 'bg-white ring-2 ring-white/70' : 'bg-white/60 hover:bg-white/90'
        ]"
        :aria-label="`Ir a slide ${i + 1}`"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'

type Slide = {
  imageUrl?: string
  title?: string
  caption?: string
}

const props = defineProps<{
  slides: Slide[]
  autoPlayMs?: number
}>()

const current = ref(0)
let timer: number | undefined

function next() {
  current.value = (current.value + 1) % props.slides.length
}

function prev() {
  current.value = (current.value - 1 + props.slides.length) % props.slides.length
}

function go(i: number) {
  current.value = i
}

function start() {
  if (!props.autoPlayMs) return
  stop()
  timer = window.setInterval(() => {
    next()
  }, props.autoPlayMs)
}

function stop() {
  if (timer) {
    clearInterval(timer)
    timer = undefined
  }
}

onMounted(start)

onUnmounted(() => {
  stop()
})

watch(() => props.autoPlayMs, () => {
  start()
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity .25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
