<template>
  <div class="min-h-full">
    <!-- Navigation -->
    <nav class="bg-gray-800">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 w-full">
        <div class="flex h-16 items-center justify-between">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <h3 class="text-white font-bold">Coffee Shop Admin</h3>
            </div>
            <div class="hidden md:block">
              <div class="ml-10 flex items-baseline space-x-4">
                <router-link
                  v-for="item in navigation"
                  :key="item.name"
                  :to="item.to"
                  :class="[
                    item.current
                      ? 'bg-gray-900 text-white'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white',
                    'rounded-md px-3 py-2 text-sm font-medium'
                  ]"
                  :aria-current="item.current ? 'page' : undefined"
                >
                  {{ item.name }}
                </router-link>
              </div>
            </div>
          </div>
          <div class="hidden md:block">
            <div class="ml-4 flex items-center md:ml-6">
              <!-- Profile dropdown -->
              <div class="relative ml-3">
                <div>
                  <button
                    type="button"
                    class="relative flex max-w-xs items-center rounded-full bg-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-gray-800"
                    id="user-menu-button"
                    aria-expanded="false"
                    aria-haspopup="true"
                    @click="toggleProfileMenu"
                  >
                    <span class="sr-only">Open user menu</span>
                    <div class="h-8 w-8 rounded-full bg-gray-600 flex items-center justify-center text-white">
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
                    class="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
                    role="menu"
                    aria-orientation="vertical"
                    aria-labelledby="user-menu-button"
                    tabindex="-1"
                  >
                    <a
                      href="#"
                      class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      role="menuitem"
                      tabindex="-1"
                      id="user-menu-item-0"
                      @click="handleLogout"
                    >
                      Sign out
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
              class="inline-flex items-center justify-center rounded-md bg-gray-800 p-2 text-gray-400 hover:bg-gray-700 hover:text-white focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-gray-800"
              aria-controls="mobile-menu"
              aria-expanded="false"
              @click="toggleMobileMenu"
            >
              <span class="sr-only">Open main menu</span>
              <Bars3Icon v-if="!isMobileMenuOpen" class="block h-6 w-6" aria-hidden="true" />
              <XMarkIcon v-else class="block h-6 w-6" aria-hidden="true" />
            </button>
          </div>
        </div>
      </div>

      <!-- Mobile menu, show/hide based on menu state. -->
      <div v-if="isMobileMenuOpen" class="md:hidden border-t border-gray-700" id="mobile-menu">
        <div class="space-y-1 px-2 pb-3 pt-2 sm:px-3">
          <router-link
            v-for="item in navigation"
            :key="item.name"
            :to="item.to"
            :class="[
              item.current
                ? 'bg-gray-900 text-white'
                : 'text-gray-300 hover:bg-gray-700 hover:text-white',
              'block rounded-md px-3 py-2 text-base font-medium'
            ]"
            :aria-current="item.current ? 'page' : undefined"
          >
            {{ item.name }}
          </router-link>
        </div>
        <div class="border-t border-gray-700 pb-3 pt-4">
          <div class="flex items-center px-5">
            <div class="flex-shrink-0">
              <div class="h-10 w-10 rounded-full bg-gray-600 flex items-center justify-center text-white">
                {{ userInitials }}
              </div>
            </div>
            <div class="ml-3">
              <div class="text-base font-medium text-white">{{ userName }}</div>
              <div class="text-sm font-medium text-gray-400">{{ userEmail }}</div>
            </div>
          </div>
          <div class="mt-3 space-y-1 px-2">
            <a
              href="#"
              class="block rounded-md px-3 py-2 text-base font-medium text-gray-400 hover:bg-gray-700 hover:text-white"
              @click="handleLogout"
            >
              Sign out
            </a>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main content -->
    <main class="bg-gray-50 min-h-[calc(100vh-4rem)]">
      <div class="mx-auto max-w-7xl p-4 sm:px-6 lg:px-8 py-6">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <div class="transition-all duration-200">
              <component :is="Component" />
            </div>
          </transition>
        </router-view>
      </div>
    </main>

    <!-- Toast notifications -->
    <ToastContainer />
    
    <!-- Confirmation dialog -->
    <ConfirmDialog />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Bars3Icon, XMarkIcon } from '@heroicons/vue/24/outline';
import { useAuthStore } from '@/stores/auth';
import { useToast, ToastContainer } from '@/composables/useToast';
import ConfirmDialog from '@/components/ui/ConfirmationDialog.vue'

const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();
const { showSuccess } = useToast();

const navigation = ref([
  { name: 'Dashboard', to: '/', current: false },
  { name: 'Menu', to: '/menu', current: false },
  { name: 'Orders', to: '/orders', current: false },
  { name: 'Tables', to: '/tables', current: false },
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
    showSuccess('Successfully logged out');
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
