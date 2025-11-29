<template>
  <nav class="bg-white/80 dark:bg-gray-900/80 backdrop-blur border-b border-gray-200 dark:border-gray-800 sticky top-0 z-30">
    <div class="mx-auto max-w-7xl px-3 sm:px-4 lg:px-8 w-full">
      <div class="flex h-14 sm:h-16 items-center justify-between">
        <!-- Mobile menu button (left side) and Logo -->
        <div class="flex items-center gap-2">
          <!-- Mobile menu button - Only show when authenticated -->
          <button
            v-if="authStore.isAuthenticated"
            type="button"
            class="inline-flex md:hidden items-center justify-center rounded-md bg-gray-200 dark:bg-gray-800 p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 hover:text-gray-900 dark:hover:bg-gray-700 dark:hover:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-gray-100 dark:focus:ring-offset-gray-900 touch-manipulation"
            aria-controls="mobile-menu"
            aria-expanded="false"
            @click="toggleMobileMenu"
          >
            <span class="sr-only">{{ t('app.actions.open_main_menu') }}</span>
            <Bars3Icon v-if="!isMobileMenuOpen" class="block h-6 w-6" aria-hidden="true" />
            <XMarkIcon v-else class="block h-6 w-6" aria-hidden="true" />
          </button>
          
          <router-link to="/" class="flex-shrink-0">
            <!-- Logo for dark mode -->
            <img 
              v-if="isDark" 
              src="@/assets/DarkModeLogo.png" 
              alt="Logo" 
              class="h-8 sm:h-12 w-auto cursor-pointer hover:opacity-80 transition-opacity"
            />
            <!-- Logo for light mode -->
            <img 
              v-else 
              src="@/assets/Logo.png" 
              alt="Logo" 
              class="h-8 sm:h-12 w-auto cursor-pointer hover:opacity-80 transition-opacity"
            />
          </router-link>
          
          <div v-if="authStore.isAuthenticated" class="hidden md:block">
            <div class="ml-10 flex items-baseline space-x-4">
              <router-link
                v-for="item in navigation"
                :key="item.name"
                :to="item.to"
                :class="[
                  item.current
                    ? 'bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-white'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white',
                  'rounded-md px-3 py-2 text-sm font-medium'
                ]"
                :aria-current="item.current ? 'page' : undefined"
              >
                {{ t(item.labelKey) }}
              </router-link>
            </div>
          </div>
        </div>

        <!-- Desktop user menu -->
        <div v-if="authStore.isAuthenticated" class="hidden md:block">
          <div class="ml-4 flex items-center md:ml-6 gap-2 sm:gap-3">
            <!-- Alerts Badge - Only show in restaurant subdomains -->
            <router-link
              v-if="canViewSubscription && hasRestaurantContext()"
              to="/subscription"
              class="relative rounded-full p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500 touch-manipulation"
              :aria-label="'Alertas de suscripción'"
            >
              <BellAlertIcon class="h-5 w-5 sm:h-6 sm:w-6" />
              <span
                v-if="unreadAlertCount > 0"
                class="absolute top-0 right-0 inline-flex items-center justify-center px-1.5 py-0.5 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full min-w-[18px]"
              >
                {{ unreadAlertCount > 9 ? '9+' : unreadAlertCount }}
              </span>
            </router-link>

            <!-- Theme toggle -->
            <button
              type="button"
              class="rounded-full p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500 touch-manipulation"
              :aria-label="$t('app.actions.toggle_theme')"
              @click="toggleTheme()"
            >
              <SunIcon v-if="isDark" class="h-5 w-5 sm:h-6 sm:w-6" />
              <MoonIcon v-else class="h-5 w-5 sm:h-6 sm:w-6" />
            </button>
            <div class="relative ml-3" ref="profileMenuRef">
              <div>
                <button
                  type="button"
                  class="relative flex max-w-xs items-center rounded-full bg-gray-200 dark:bg-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-gray-100 dark:focus:ring-offset-gray-900"
                  id="user-menu-button"
                  aria-expanded="false"
                  aria-haspopup="true"
                  @click="toggleProfileMenu"
                >
                  <span class="sr-only">{{ t('app.actions.open_user_menu') }}</span>
                  <div class="h-8 w-8 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center text-gray-900 dark:text-white">
                    {{ userInitials }}
                  </div>
                </button>
              </div>

              <!-- Dropdown menu -->
              <transition
                enter-active-class="transition ease-out duration-100"
                enter-from-class="transform opacity-0 scale-95"
                enter-to-class="transform opacity-100 scale-100"
                leave-active-class="transition ease-in duration-75"
                leave-from-class="transform opacity-100 scale-100"
                leave-to-class="transform opacity-0 scale-95"
              >
                <div
                  v-if="isProfileMenuOpen"
                  class="absolute right-0 z-10 mt-2 w-52 origin-top-right rounded-md bg-white dark:bg-gray-800 py-1 shadow-lg ring-1 ring-black/5 dark:ring-white/10 focus:outline-none"
                  role="menu"
                  aria-orientation="vertical"
                  aria-labelledby="user-menu-button"
                  tabindex="-1"
                >
                  <router-link
                    v-if="canManageUsers && hasRestaurantContext()"
                    to="/users"
                    class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700/60"
                    role="menuitem"
                    tabindex="-1"
                    @click="isProfileMenuOpen = false"
                  >
                    {{ t('app.nav.users') }}
                  </router-link>
                  <router-link
                    v-if="canViewSubscription && hasRestaurantContext()"
                    to="/reports"
                    class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700/60"
                    role="menuitem"
                    tabindex="-1"
                    @click="isProfileMenuOpen = false"
                  >
                    {{ t('app.nav.reports') }}
                  </router-link>
                  <div class="border-t border-gray-100 dark:border-gray-700 my-1"></div>
                  <router-link
                    v-if="(authStore.user?.role === 'admin' || authStore.user?.role === 'sysadmin') && hasRestaurantContext()"
                    to="/subscription"
                    class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700/60"
                    role="menuitem"
                    tabindex="-1"
                    @click="isProfileMenuOpen = false"
                  >
                    {{ t('app.nav.subscription') }}
                  </router-link>
                  <router-link
                    to="/profile"
                    class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700/60"
                    role="menuitem"
                    tabindex="-1"
                    id="user-menu-item-0"
                    @click="isProfileMenuOpen = false"
                  >
                    {{ t('app.profile.view_profile') }}
                  </router-link>
                  <a
                    href="#"
                    class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700/60"
                    role="menuitem"
                    tabindex="-1"
                    id="user-menu-item-1"
                    @click="handleLogout"
                  >
                    {{ t('app.actions.sign_out') }}
                  </a>
                  <div class="border-t border-gray-100 dark:border-gray-700 mt-1 pt-1 px-4 pb-1">
                    <p class="text-[11px] leading-tight text-gray-400 dark:text-gray-500">
                      {{ t('app.labels.version') }} {{ appVersion }}
                    </p>
                  </div>
                </div>
              </transition>
            </div>
          </div>
        </div>

        <!-- Theme toggle mobile -->
        <div class="-mr-2 flex md:hidden">
          <button
            type="button"
            class="rounded-full p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500 touch-manipulation"
            :aria-label="$t('app.actions.toggle_theme')"
            @click="toggleTheme()"
          >
            <SunIcon v-if="isDark" class="h-6 w-6" />
            <MoonIcon v-else class="h-6 w-6" />
          </button>
        </div>
      </div>
    </div>

  </nav>

  <!-- Mobile menu overlay and sidebar (using Teleport to render outside nav) -->
  <Teleport to="body">
    <!-- Mobile menu overlay -->
    <transition
      enter-active-class="transition-opacity ease-linear duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity ease-linear duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isMobileMenuOpen && authStore.isAuthenticated"
        class="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-[100] md:hidden"
        @click="isMobileMenuOpen = false"
      ></div>
    </transition>

    <!-- Mobile menu, show/hide based on menu state. -->
    <transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="transform -translate-x-full"
      enter-to-class="transform translate-x-0"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="transform translate-x-0"
      leave-to-class="transform -translate-x-full"
    >
      <div
        v-if="isMobileMenuOpen && authStore.isAuthenticated"
        class="fixed top-0 left-0 bottom-0 w-72 bg-white dark:bg-gray-900 shadow-xl z-[110] md:hidden overflow-y-auto"
        id="mobile-menu"
      >
        <!-- Header with close button -->
        <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <router-link to="/" class="flex-shrink-0" @click="isMobileMenuOpen = false">
            <img 
              v-if="isDark" 
              src="@/assets/DarkModeLogo.png" 
              alt="Logo" 
              class="h-8 w-auto"
            />
            <img 
              v-else 
              src="@/assets/Logo.png" 
              alt="Logo" 
              class="h-8 w-auto"
            />
          </router-link>
          <button
            @click="isMobileMenuOpen = false"
            class="rounded-md p-2 text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
          >
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>

        <!-- Navigation links -->
        <div class="space-y-1 px-3 py-3">
          <router-link
            v-for="item in navigation"
            :key="item.name"
            :to="item.to"
            :class="[
              item.current
                ? 'bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-white'
                : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white',
              'block rounded-md px-3 py-2 text-sm font-medium'
            ]"
            :aria-current="item.current ? 'page' : undefined"
            @click="isMobileMenuOpen = false"
          >
            {{ $t(item.labelKey) }}
          </router-link>
        </div>

        <!-- User section -->
        <div class="border-t border-gray-200 dark:border-gray-700 py-3">
          <div class="flex items-center px-4 mb-3">
            <div class="flex-shrink-0">
              <div class="h-10 w-10 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center text-gray-900 dark:text-white">
                {{ userInitials }}
              </div>
            </div>
            <div class="ml-3 min-w-0 flex-1">
              <div class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ userName }}</div>
              <div class="text-xs font-medium text-gray-500 dark:text-gray-400 truncate">{{ userEmail }}</div>
            </div>
          </div>
          <div class="space-y-1 px-3">
            <router-link
              v-if="canManageUsers && hasRestaurantContext()"
              to="/users"
              class="block rounded-md px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white"
              @click="isMobileMenuOpen = false"
            >
              {{ $t('app.nav.users') }}
            </router-link>
            <router-link
              v-if="canViewSubscription && hasRestaurantContext()"
              to="/reports"
              class="block rounded-md px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white"
              @click="isMobileMenuOpen = false"
            >
              {{ $t('app.nav.reports') }}
            </router-link>
            <div class="border-t border-gray-100 dark:border-gray-700 my-2"></div>
            <router-link
              v-if="(authStore.user?.role === 'admin' || authStore.user?.role === 'sysadmin') && hasRestaurantContext()"
              to="/subscription"
              class="block rounded-md px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white"
              @click="isMobileMenuOpen = false"
            >
              {{ $t('app.nav.subscription') }}
            </router-link>
            <router-link
              to="/profile"
              class="block rounded-md px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white"
              @click="isMobileMenuOpen = false"
            >
              {{ t('app.profile.view_profile') }}
            </router-link>
            <a
              href="#"
              class="block rounded-md px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white"
              @click="handleLogout"
            >
              {{ $t('app.actions.sign_out') }}
            </a>
            <div class="mt-2 pt-2 border-t border-gray-100 dark:border-gray-700">
              <p class="text-[11px] leading-tight text-gray-400 dark:text-gray-500">
                {{ $t('app.labels.version') }} {{ appVersion }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Bars3Icon, XMarkIcon, MoonIcon, SunIcon, BellAlertIcon } from '@heroicons/vue/24/outline';
import { useAuthStore } from '@/stores/auth';
import { useToast } from '@/composables/useToast';
import { usePermissions } from '@/composables/usePermissions';
import { hasRestaurantContext } from '@/utils/subdomain';
import { useI18n } from 'vue-i18n';
import { useTheme } from '@/composables/useTheme';
import { alertService } from '@/services/alertService';
import { useAppVersion } from '@/composables/useAppVersion';

const props = defineProps({
  subscriptionFeatures: {
    type: Object,
    default: () => ({
      has_kitchen_module: false,
      has_ingredients_module: false,
      has_inventory_module: false,
      has_advanced_reports: false
    })
  }
});

const authStore = useAuthStore();
const route = useRoute();
const { t } = useI18n();
const { isDark, toggleTheme } = useTheme();
const { appVersion } = useAppVersion();
const { 
  canEditCategories, 
  canManageTables, 
  canAccessCashRegister, 
  canAccessKitchen, 
  canManageUsers, 
  canViewSubscription,
  isSysAdmin 
} = usePermissions();

const isMobileMenuOpen = ref(false);
const isProfileMenuOpen = ref(false);
const unreadAlertCount = ref(0);
const profileMenuRef = ref(null);
let alertCheckInterval = null;

const navigation = computed(() => {
  const path = route.path;
  const isMainDomain = !hasRestaurantContext();
  
  // If on main domain (no subdomain), only show Administration
  if (isMainDomain) {
    const mainDomainNav = [];
    
    // Add SysAdmin links only on main domain
    if (isSysAdmin.value) {
      mainDomainNav.push({ name: 'sysadmin', labelKey: 'app.nav.sysadmin', to: '/sysadmin', current: false, show: true });
      mainDomainNav.push({ name: 'payments', labelKey: 'app.nav.pending_payments', to: '/sysadmin/payments', current: false, show: true });
    }
    
    return mainDomainNav
      .filter(item => item.show)
      .map(item => ({
        ...item,
        current: item.to === path
      }));
  }
  
  // If on subdomain (restaurant context), show restaurant operations
  const baseNav = [
    { name: 'categories', labelKey: 'app.nav.categories', to: '/categories', current: false, show: canEditCategories.value },
    { name: 'menu', labelKey: 'app.nav.menu', to: '/menu', current: false, show: true },
    { name: 'orders', labelKey: 'app.nav.orders', to: '/orders', current: false, show: true },
    { name: 'tables', labelKey: 'app.nav.tables', to: '/tables', current: false, show: canManageTables.value },
    { name: 'cash-register', labelKey: 'app.nav.cash_register', to: '/cash-register', current: false, show: canAccessCashRegister.value },
  ];
  
  // Add kitchen module if subscription allows it AND user has permission
  if (props.subscriptionFeatures.has_kitchen_module && canAccessKitchen.value) {
    baseNav.splice(4, 0, { name: 'kitchen', labelKey: 'app.nav.kitchen', to: '/kitchen', current: false, show: true });
  }
  
  // Users and Reports are now in the user dropdown menu, not in the main navbar
  
  // Filter by show property and update current state based on route
  return baseNav
    .filter(item => item.show)
    .map(item => ({
      ...item,
      current: item.to === path || 
               (item.to === '/' && path === '') ||
               (item.to !== '/' && path.startsWith(item.to) && 
                (path === item.to || path.startsWith(`${item.to}/`)))
    }));
});

const userInitials = computed(() => {
  if (!authStore.user) return 'U';
  const name = authStore.user.name || authStore.user.email;
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .substring(0, 2);
});

const userName = computed(() => {
  return authStore.user?.name || 'User';
});

const userEmail = computed(() => {
  return authStore.user?.email || '';
});

function toggleMobileMenu() {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
}

function toggleProfileMenu() {
  isProfileMenuOpen.value = !isProfileMenuOpen.value;
}

async function handleLogout() {
  try {
    // Close the profile menu
    isProfileMenuOpen.value = false;
    
    await authStore.logout();
    // Note: authStore.logout() uses window.location.href, so this code won't execute
    // The page will reload before we get here
  } catch (error) {
    console.error('Logout failed:', error);
    // If logout fails, force navigation with full page reload
    window.location.href = '/login';
  }
}

// Load alert count
async function loadAlertCount() {
  if (canViewSubscription.value && hasRestaurantContext()) {
    try {
      unreadAlertCount.value = await alertService.getUnreadCount();
    } catch (error) {
      // Silently fail - alerts are not critical
      console.error('Failed to load alert count:', error);
    }
  }
}

// Handle click outside profile menu
function handleClickOutside(event) {
  if (profileMenuRef.value && !profileMenuRef.value.contains(event.target)) {
    isProfileMenuOpen.value = false;
  }
}

// Start periodic alert check
onMounted(() => {
  loadAlertCount();
  // Check every 2 minutes
  alertCheckInterval = setInterval(loadAlertCount, 120000);
  
  // Add click outside listener for profile menu
  document.addEventListener('click', handleClickOutside);
});

// Cleanup
onUnmounted(() => {
  if (alertCheckInterval) {
    clearInterval(alertCheckInterval);
  }
  
  // Remove click outside listener
  document.removeEventListener('click', handleClickOutside);
});

// Close menus when route changes
watch(
  () => route.path,
  () => {
    isMobileMenuOpen.value = false;
    isProfileMenuOpen.value = false;
  }
);
</script>
