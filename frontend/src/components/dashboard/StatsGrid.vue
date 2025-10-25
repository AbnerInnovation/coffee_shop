<template>
  <div class="grid grid-cols-2 gap-3 sm:gap-6 lg:grid-cols-4">
    <StatsCard
      :label="t('app.dashboard.total_orders_today')"
      :value="stats.totalOrdersToday"
      :comparison="stats.ordersComparison"
      :comparison-label="t('app.dashboard.vs_yesterday')"
    />
    
    <StatsCard
      :label="t('app.dashboard.revenue_today')"
      :value="`$${stats.revenueToday.toFixed(2)}`"
      :comparison="stats.revenueComparison"
      :comparison-label="t('app.dashboard.vs_yesterday')"
    />
    
    <StatsCard
      :label="t('app.dashboard.active_tables')"
      :value="`${stats.activeTables}/${stats.totalTables}`"
    />
    
    <div class="col-span-2 lg:col-span-1">
      <StatsCard
        :label="t('app.dashboard.popular_item')"
        :value="stats.popularItem || '—'"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import StatsCard from './StatsCard.vue';
import type { DashboardStats } from '@/composables/useDashboardStats';

defineProps<{
  stats: DashboardStats;
}>();

const { t } = useI18n();
</script>
