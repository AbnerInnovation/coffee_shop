<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center px-4 sm:px-6 lg:px-8">
    <div class="w-full max-w-md space-y-8">
      <div class="text-center">
        <h1 class="text-9xl font-extrabold text-primary-600 dark:text-primary-400 mb-4">404</h1>
        <h2 class="mt-6 text-3xl font-bold text-gray-900 dark:text-white">Page not found</h2>
        <p class="mt-2 text-gray-600 dark:text-gray-300">
          Sorry, we couldn't find the page you're looking for.
        </p>
      </div>
      
      <div class="mt-8 flex flex-col sm:flex-row justify-center gap-4">
        <router-link
          to="/"
          class="btn btn-primary w-full sm:w-auto justify-center"
        >
          <span>Go back home</span>
        </router-link>
        
        <button
          @click="goBack"
          class="btn btn-secondary w-full sm:w-auto justify-center"
        >
          Go back
        </button>
      </div>
      
      <div class="mt-8 text-center">
        <p class="text-sm text-gray-500 dark:text-gray-400">
          Need help? 
          <a href="#" class="font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300">
            Contact our support team
          </a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

const goBack = () => {
  if (window.history.state.back) {
    router.go(-1);
  } else {
    router.push('/');
  }
};
</script>

<style scoped>
/* Custom animations */
h1 {
  background: linear-gradient(45deg, #3b82f6, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-fill-color: transparent;
  line-height: 1;
}

/* Smooth transitions */
.btn {
  transition: all 0.2s ease-in-out;
  transform: translateY(0);
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.btn:active {
  transform: translateY(0);
}
</style>
