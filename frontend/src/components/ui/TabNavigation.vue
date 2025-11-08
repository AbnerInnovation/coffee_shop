<template>
  <div class="border-b border-gray-200 dark:border-gray-700">
    <nav class="-mb-px flex space-x-8" aria-label="Tabs">
      <button
        v-for="(tab, index) in tabs"
        :key="index"
        @click="$emit('change', index)"
        :class="[
          activeTab === index
            ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
          'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors'
        ]"
        :aria-current="activeTab === index ? 'page' : undefined"
      >
        <span class="flex items-center gap-2">
          <span
            :class="[
              'flex items-center justify-center w-6 h-6 rounded-full text-xs font-semibold',
              activeTab === index
                ? 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400'
                : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
            ]"
          >
            {{ index + 1 }}
          </span>
          {{ tab }}
        </span>
      </button>
    </nav>
  </div>
</template>

<script setup lang="ts">
interface Props {
  tabs: string[];
  activeTab: number;
}

defineProps<Props>();

defineEmits<{
  (e: 'change', index: number): void;
}>();
</script>
