<template>
  <div class="mb-16 relative overflow-hidden rounded-3xl bg-gradient-to-r from-indigo-600 to-purple-600 p-8 md:p-12 text-white shadow-2xl">
    <div class="absolute top-0 right-0 -mt-4 -mr-4 w-72 h-72 bg-white/10 rounded-full blur-3xl"></div>
    <div class="absolute bottom-0 left-0 -mb-4 -ml-4 w-72 h-72 bg-white/10 rounded-full blur-3xl"></div>
    
    <div class="relative z-10 text-center max-w-3xl mx-auto">
      <div class="inline-flex items-center justify-center px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full text-sm font-semibold mb-4">
        🎉 Prueba Gratuita Disponible
      </div>
      
      <h2 class="text-3xl md:text-4xl font-extrabold mb-4">
        14 Días Gratis - Sin Tarjeta de Crédito
      </h2>
      
      <p class="text-lg md:text-xl text-white/90 mb-6 max-w-2xl mx-auto">
        Acceso completo al Plan Pro durante 2 semanas. Configura tu restaurante, prueba todas las funciones y decide después.
      </p>
      
      <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
        <span class="inline-flex items-center px-8 py-4 bg-white text-indigo-600 font-bold rounded-xl hover:bg-gray-100 transition-all shadow-lg hover:shadow-xl hover:scale-105">
          Solicita Prueba Gratuita a través del botón de WhatsApp
        </span>
      </div>
      
      <div class="mt-6 flex flex-wrap justify-center gap-6 text-sm text-white/80">
        <div v-for="feature in features" :key="feature.text" class="flex items-center gap-2">
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          </svg>
          {{ feature.text }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Feature {
  icon: string
  text: string
}

interface Props {
  features: Feature[]
}

defineProps<Props>()
</script>
