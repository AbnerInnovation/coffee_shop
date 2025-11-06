<template>
  <div>
    <!-- SYSADMIN Dashboard (when not in restaurant context) -->
    <SysAdminDashboardView v-if="showSysAdminDashboard" />

    <!-- Restaurant Dashboard (normal operations) -->
    <div v-else>
      <!-- Quick Actions Panel -->
      <QuickActions @new-order="openNewOrderModal" />

      <!-- Main Statistics -->
      <StatsGrid :stats="stats" />

      <!-- Kitchen Performance Metrics -->
      <KitchenMetrics :kitchen-stats="kitchenStats" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue';
import QuickActions from '@/components/dashboard/QuickActions.vue';
import StatsGrid from '@/components/dashboard/StatsGrid.vue';
import KitchenMetrics from '@/components/dashboard/KitchenMetrics.vue';
import SysAdminDashboardView from '@/views/SysAdminDashboardView.vue';
import { useDashboardStats } from '@/composables/useDashboardStats';
import { useAuthStore } from '@/stores/auth';
import { hasRestaurantContext } from '@/utils/subdomain';

const authStore = useAuthStore();

// Show SYSADMIN dashboard if user is sysadmin and NOT in a restaurant context
const showSysAdminDashboard = computed(() => {
  return authStore.user?.role === 'sysadmin' && !hasRestaurantContext();
});

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
