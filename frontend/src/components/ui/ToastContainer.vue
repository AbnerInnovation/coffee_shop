<script setup lang="ts">
import { XMarkIcon } from '@heroicons/vue/20/solid';
import { useToast } from '@/composables/useToast';

const { toasts, removeToast } = useToast();
</script>

<template>
  <div class="fixed bottom-4 right-4 z-50 flex flex-col space-y-2">
    <TransitionGroup
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="transform opacity-0 translate-y-2"
      enter-to-class="transform opacity-100 translate-y-0"
      leave-active-class="transition-all duration-300 ease-in"
      leave-from-class="transform opacity-100 translate-y-0"
      leave-to-class="transform opacity-0 translate-y-2"
    >
      <div 
        v-for="toast in toasts" 
        :key="toast.id"
        class="flex items-center justify-between w-80 rounded-md shadow-lg p-4 text-white"
        :class="{
          'bg-green-500': toast.type === 'success',
          'bg-red-500': toast.type === 'error',
          'bg-blue-500': toast.type === 'info',
          'bg-yellow-500': toast.type === 'warning',
        }"
      >
        <span class="text-sm font-medium">{{ toast.message }}</span>
        <button 
          @click="removeToast(toast.id)" 
          class="ml-4 text-white hover:text-gray-200 focus:outline-none"
        >
          <XMarkIcon class="h-5 w-5" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>
