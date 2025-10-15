<template>
  <div class="min-h-full dark:bg-gray-950">
    <main>
      <div class="mx-auto max-w-7xl sm:px-6 lg:px-8 dark:bg-gray-950">
        <slot></slot>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
// Main layout component for consistent screen width across the app
// Max width: 7xl (1280px)
// Responsive padding: sm:px-6 lg:px-8
</script>
