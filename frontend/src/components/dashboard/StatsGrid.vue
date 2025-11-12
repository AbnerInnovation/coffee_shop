<template>
  <div class="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
    <StatsCard
      :label="t('app.dashboard.total_orders_today')"
      :value="stats.totalOrdersToday"
      :comparison="stats.ordersComparison"
      :comparison-label="t('app.dashboard.vs_yesterday')"
    />
    
    <StatsCard
      :label="t('app.dashboard.revenue_today')"
      :value="formatCurrency(stats.revenueToday)"
      :comparison="stats.revenueComparison"
      :comparison-label="t('app.dashboard.vs_yesterday')"
    />
    
    <StatsCard
      :label="t('app.dashboard.active_tables')"
      :value="`${stats.activeTables}/${stats.totalTables}`"
    />
    
    <StatsCard
      :label="t('app.dashboard.popular_item')"
      :value="stats.popularItem || '—'"
    />
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { formatCurrency } from '@/utils/priceHelpers';
import StatsCard from './StatsCard.vue';
import type { DashboardStats } from '@/composables/useDashboardStats';

defineProps<{
  stats: DashboardStats;
}>();

const { t } = useI18n();
</script>
