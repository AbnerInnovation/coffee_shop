<template>
  <div class="border border-gray-200 dark:border-gray-700 rounded-lg">
    <div class="p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
        {{ title }}
      </h3>
      <div class="space-y-3">
        <div
          v-for="(count, plan) in distribution"
          :key="plan"
          class="flex items-center justify-between"
        >
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ plan }}</span>
          <div class="flex items-center gap-3">
            <div class="w-32 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                class="bg-primary-600 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${calculatePercentage(count)}%` }"
              ></div>
            </div>
            <span class="text-sm font-semibold text-gray-900 dark:text-white w-8 text-right">
              {{ count }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string;
  distribution: Record<string, number>;
  total: number;
}

const props = defineProps<Props>();

const calculatePercentage = (count: number): number => {
  if (props.total === 0) return 0;
  return Math.round((count / props.total) * 100);
};
</script>
