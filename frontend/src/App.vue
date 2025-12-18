<template>
  <div class="min-h-full">
    <!-- Navigation (hidden on pages with hideNavbar meta) -->
    <AppNavbar v-if="showNavbar" :subscription-features="subscriptionFeatures" />

    <!-- Main content -->
    <main :class="[
      'bg-gray-50 dark:bg-gray-950',
      showNavbar ? 'min-h-[calc(100vh-3.6rem)] sm:min-h-[calc(100vh-4.1rem)]' : 'min-h-screen'
    ]">
      <div :class="[
        'bg-gray-50 dark:bg-gray-950 mx-auto',
        showNavbar ? 'max-w-7xl px-3 py-4 sm:px-6 sm:py-6 lg:px-8' : ''
      ]">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <div class="transition-all duration-200">
              <component :is="Component" />
            </div>
          </transition>
        </router-view>
      </div>
    </main>
    <!-- Confirmation dialog -->
    <ConfirmDialog />
    
    <!-- Global New Order Modal - only mount when needed -->
    <NewOrderModal
      v-if="showNewOrderModal"
      :open="showNewOrderModal"
      @close="showNewOrderModal = false"
      @order-created="handleOrderCreated"
    />

    <!-- Account Suspended Modal -->
    <AccountSuspendedModal
      :is-open="showSuspendedModal"
      :message="subscriptionStatus?.message || ''"
      :status="subscriptionStatus?.status"
      :days-remaining="subscriptionStatus?.days_remaining"
      @close="closeSuspendedModal"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AppNavbar from '@/components/layout/AppNavbar.vue';
import ConfirmDialog from '@/components/ui/ConfirmationDialog.vue';
import NewOrderModal from '@/components/orders/NewOrderModal.vue';
import AccountSuspendedModal from '@/components/subscription/AccountSuspendedModal.vue';
import { subscriptionService } from '@/services/subscriptionService';
import { hasRestaurantContext } from '@/utils/subdomain';
import { useSubscriptionCheck } from '@/composables/useSubscriptionCheck';
import { useToast } from '@/composables/useToast';
import { useI18n } from 'vue-i18n';
import { useOperationMode } from '@/composables/useOperationMode';

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();
const { showInfo } = useToast();
const { t } = useI18n();

// Subscription check
const { subscriptionStatus, showSuspendedModal, closeSuspendedModal } = useSubscriptionCheck();

// Operation mode
const { loadModeConfig } = useOperationMode();

// Subscription features
const subscriptionFeatures = ref({
  has_kitchen_module: false,
  has_ingredients_module: false,
  has_inventory_module: false,
  has_advanced_reports: false
});

const showNewOrderModal = ref(false);

// Computed property to determine if navbar should be shown
const showNavbar = computed(() => {
  return !route.meta.hideNavbar;
});

// Handle order created from modal
function handleOrderCreated(order) {
  // Emit event for other components to refresh their data
  window.dispatchEvent(new CustomEvent('order-created', { detail: order }));
  
  // If not on orders page, navigate to it
  if (route.path !== '/orders') {
    router.push('/orders');
  }
}

// Load subscription features and operation mode
const loadSubscriptionFeatures = async () => {
  // Only load subscription features if we're in a restaurant context (subdomain)
  // and user is authenticated
  if (!authStore.isAuthenticated || !hasRestaurantContext()) {
    return;
  }
  
  try {
    const usage = await subscriptionService.getUsage();
    if (usage.has_subscription && usage.features) {
      subscriptionFeatures.value = {
        has_kitchen_module: usage.features.has_kitchen_module || false,
        has_ingredients_module: usage.features.has_ingredients_module || false,
        has_inventory_module: usage.features.has_inventory_module || false,
        has_advanced_reports: usage.features.has_advanced_reports || false
      };
    }
    
    // Load operation mode configuration from usage response (no separate call needed)
    if (usage.operation_mode && usage.mode_config) {
      const { setModeConfigFromUsage } = useOperationMode();
      setModeConfigFromUsage(usage.operation_mode, usage.mode_config);
    }
  } catch (error) {
    console.error('Error loading subscription features:', error);
  }
};

// Watch for authentication changes to load subscription features
watch(
  () => authStore.isAuthenticated,
  (isAuthenticated) => {
    if (isAuthenticated) {
      // Load subscription features when user logs in
      loadSubscriptionFeatures();
    } else {
      // Reset subscription features when user logs out
      subscriptionFeatures.value = {
        has_kitchen_module: false,
        has_ingredients_module: false,
        has_inventory_module: false,
        has_advanced_reports: false
      };
    }
  },
  { immediate: true }
);

// Listen for custom event to open modal from other components
const handleOpenModalEvent = () => {
  showNewOrderModal.value = true;
};

// Handle PWA update available event (from main.ts registerSW)
const handlePwaUpdateAvailable = (event) => {
  const anyEvent = event as CustomEvent<{ updateSW: (reloadPage?: boolean) => void }>;
  const updateSW = anyEvent.detail?.updateSW;
  if (!updateSW) return;

  // Show informational toast and then trigger update
  showInfo(t('app.messages.new_version_available'), 6000);

  // Give user a short moment, then activate new SW and reload
  setTimeout(() => {
    updateSW(true);
  }, 3000);
};

onMounted(() => {
  window.addEventListener('open-new-order-modal', handleOpenModalEvent);
  window.addEventListener('pwa-update-available', handlePwaUpdateAvailable as EventListener);
});

onUnmounted(() => {
  window.removeEventListener('open-new-order-modal', handleOpenModalEvent);
  window.removeEventListener('pwa-update-available', handlePwaUpdateAvailable as EventListener);
});
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
