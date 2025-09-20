<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 flex items-center justify-center bg-black/50 z-50"
  >
    <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-6 max-w-sm w-full border border-gray-200 dark:border-gray-800">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white">{{ options?.title }}</h2>
      <p class="text-gray-600 dark:text-gray-300 mt-2">{{ options?.message }}</p>

      <div class="flex justify-end gap-2 mt-6">
        <button
          class="px-4 py-2 rounded-xl border border-gray-300 text-gray-700 hover:bg-gray-100 dark:border-gray-700 dark:text-gray-200 dark:hover:bg-gray-800"
          @click="onCancel"
        >
          {{ options?.cancelText }}
        </button>
        <button
          class="px-4 py-2 rounded-xl text-white"
          :class="options?.confirmClass"
          @click="onConfirm"
        >
          {{ options?.confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useConfirm } from '@/composables/useConfirm'

const { isOpen, options, onConfirm, onCancel } = useConfirm()
</script>
