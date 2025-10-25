<template>
  <div>
    <!-- Quick Actions Panel -->
    <QuickActions @new-order="openNewOrderModal" />

    <!-- Main Statistics -->
    <StatsGrid :stats="stats" />

    <!-- Kitchen Performance Metrics -->
    <KitchenMetrics :kitchen-stats="kitchenStats" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue';
import QuickActions from '@/components/dashboard/QuickActions.vue';
import StatsGrid from '@/components/dashboard/StatsGrid.vue';
import KitchenMetrics from '@/components/dashboard/KitchenMetrics.vue';
import { useDashboardStats } from '@/composables/useDashboardStats';

// Use the composable for all dashboard logic
const { stats, kitchenStats, loading, error, loadStats } = useDashboardStats();

// Open new order modal
function openNewOrderModal() {
  window.dispatchEvent(new CustomEvent('open-new-order-modal'));
}

// Listen for order-created event to refresh dashboard
const handleOrderCreatedEvent = () => {
  loadStats();
};

onMounted(() => {
  window.addEventListener('order-created', handleOrderCreatedEvent);
  loadStats();
});

onUnmounted(() => {
  window.removeEventListener('order-created', handleOrderCreatedEvent);
});
</script>
