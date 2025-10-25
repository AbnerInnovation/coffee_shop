<template>
  <div class="mt-4 sm:mt-6 grid grid-cols-1 gap-3 sm:gap-6 sm:grid-cols-3">
    <StatsCard
      :label="t('app.dashboard.orders_in_queue')"
      :value="kitchenStats.ordersInQueue"
      :subtitle="t('app.dashboard.pending_and_preparing')"
    />
    
    <StatsCard
      :label="t('app.dashboard.avg_prep_time')"
      :value="kitchenStats.avgPrepTime"
      :subtitle="t('app.dashboard.minutes')"
    />
    
    <StatsCard
      :label="t('app.dashboard.longest_wait')"
      :value="kitchenStats.longestWait"
      :subtitle="t('app.dashboard.minutes')"
    />
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import StatsCard from './StatsCard.vue';
import type { KitchenStats } from '@/composables/useDashboardStats';

defineProps<{
  kitchenStats: KitchenStats;
}>();

const { t } = useI18n();
</script>
