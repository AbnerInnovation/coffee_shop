<template>
  <div class="min-h-full">
    <!-- Navigation -->
    <nav class="bg-white/80 dark:bg-gray-900/80 backdrop-blur border-b border-gray-200 dark:border-gray-800">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 w-full">
        <div class="flex h-16 items-center justify-between">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <h3 class="text-gray-900 dark:text-white font-bold">{{ t('app.title') }}</h3>
            </div>
            <div class="hidden md:block">
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
          <div class="hidden md:block">
            <div class="ml-4 flex items-center md:ml-6">
              <!-- Theme toggle -->
              <button
                type="button"
                class="mr-3 rounded-full p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-primary-500"
                :aria-label="$t('app.actions.toggle_theme')"
                @click="toggleTheme()"
              >
                <SunIcon v-if="isDark" class="h-5 w-5" />
                <MoonIcon v-else class="h-5 w-5" />
              </button>
              <div class="relative ml-3">
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
                    class="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white dark:bg-gray-800 py-1 shadow-lg ring-1 ring-black/5 dark:ring-white/10 focus:outline-none"
                    role="menu"
                    aria-orientation="vertical"
                    aria-labelledby="user-menu-button"
                    tabindex="-1"
                  >
                    <a
                      href="#"
                      class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700/60"
                      role="menuitem"
                      tabindex="-1"
                      id="user-menu-item-0"
                      @click="handleLogout"
                    >
                      {{ t('app.actions.sign_out') }}
                    </a>
                  </div>
                </transition>
              </div>
            </div>
          </div>
          <div class="-mr-2 flex md:hidden">
            <!-- Mobile menu button -->
            <button
              type="button"
              class="inline-flex items-center justify-center rounded-md bg-gray-200 dark:bg-gray-800 p-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 hover:text-gray-900 dark:hover:bg-gray-700 dark:hover:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-gray-100 dark:focus:ring-offset-gray-900"
              aria-controls="mobile-menu"
              aria-expanded="false"
              @click="toggleMobileMenu"
            >
              <span class="sr-only">{{ t('app.actions.open_main_menu') }}</span>
              <Bars3Icon v-if="!isMobileMenuOpen" class="block h-6 w-6" aria-hidden="true" />
              <XMarkIcon v-else class="block h-6 w-6" aria-hidden="true" />
            </button>
          </div>
        </div>
      </div>

      <!-- Mobile menu, show/hide based on menu state. -->
      <div v-if="isMobileMenuOpen" class="md:hidden border-t border-gray-200 dark:border-gray-700" id="mobile-menu">
        <div class="space-y-1 px-2 pb-3 pt-2 sm:px-3">
          <router-link
            v-for="item in navigation"
            :key="item.name"
            :to="item.to"
            :class="[
              item.current
                ? 'bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-white'
                : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white',
              'block rounded-md px-3 py-2 text-base font-medium'
            ]"
            :aria-current="item.current ? 'page' : undefined"
          >
            {{ $t(item.labelKey) }}
          </router-link>
        </div>
        <div class="border-t border-gray-200 dark:border-gray-700 pb-3 pt-4">
          <div class="flex items-center px-5">
            <div class="flex-shrink-0">
              <div class="h-10 w-10 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center text-gray-900 dark:text-white">
                {{ userInitials }}
              </div>
            </div>
            <div class="ml-3">
              <div class="text-base font-medium text-gray-900 dark:text-white">{{ userName }}</div>
              <div class="text-sm font-medium text-gray-500 dark:text-gray-400">{{ userEmail }}</div>
            </div>
          </div>
          <div class="mt-3 space-y-1 px-2">
            <a
              href="#"
              class="block rounded-md px-3 py-2 text-base font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-white"
              @click="handleLogout"
            >
              {{ $t('app.actions.sign_out') }}
            </a>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main content -->
    <main class="bg-gray-50 dark:bg-gray-950 min-h-[calc(100vh-4rem)]">
      <div class="bg-gray-50 dark:bg-gray-950 mx-auto max-w-7xl p-4 sm:px-6 lg:px-8 py-6">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <div class="transition-all duration-200">
              <component :is="Component" />
            </div>
          </transition>
        </router-view>
      </div>
    </main>

    <!-- Toast notifications are handled globally by vue-toastification -->
    
    <!-- Confirmation dialog -->
    <ConfirmDialog />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Bars3Icon, XMarkIcon, MoonIcon, SunIcon } from '@heroicons/vue/24/outline';
import { useAuthStore } from '@/stores/auth';
import { useToast } from '@/composables/useToast';
import ConfirmDialog from '@/components/ui/ConfirmationDialog.vue'
import { useI18n } from 'vue-i18n';
import { useTheme } from '@/composables/useTheme';

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();
const { showSuccess } = useToast();
const { t } = useI18n();
const { isDark, toggleTheme } = useTheme();

const navigation = ref([
  { name: 'dashboard', labelKey: 'app.nav.dashboard', to: '/', current: false },
  { name: 'menu', labelKey: 'app.nav.menu', to: '/menu', current: false },
  { name: 'orders', labelKey: 'app.nav.orders', to: '/orders', current: false },
  { name: 'kitchen', labelKey: 'app.nav.kitchen', to: '/kitchen', current: false },
  { name: 'tables', labelKey: 'app.nav.tables', to: '/tables', current: false },
]);

const isMobileMenuOpen = ref(false);
const isProfileMenuOpen = ref(false);

// Update current route in navigation
const updateCurrentRoute = (path) => {
  navigation.value = navigation.value.map(item => ({
    ...item,
    // Match exact paths or subpaths for non-root routes
    current: item.to === path || 
             (item.to === '/' && path === '') ||
             (item.to !== '/' && path.startsWith(item.to) && 
              (path === item.to || path.startsWith(`${item.to}/`)))
  }));
};

// Initialize current route
const initializeRoute = () => {
  const path = window.location.pathname;
  updateCurrentRoute(path);
};

initializeRoute();

// Watch for route changes
watch(() => route.path, (newPath) => {
  updateCurrentRoute(newPath);
}, { immediate: true });

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
    await authStore.logout();
    showSuccess(t('app.messages.logout_success'));
    router.push('/login');
  } catch (error) {
    console.error('Logout failed:', error);
  }
}

// Close mobile menu when route changes
watch(
  () => route.path,
  () => {
    isMobileMenuOpen.value = false;
  }
);
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
