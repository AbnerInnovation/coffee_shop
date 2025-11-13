<template>
    <WhatsAppButton />

    <section class="max-w-6xl mx-auto px-6 py-16">
        <div
            class="relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-50 to-white dark:from-slate-900 dark:to-slate-900 ring-1 ring-inset ring-indigo-100 dark:ring-indigo-900/40 mb-14">
            <div
                class="pointer-events-none absolute -top-10 -right-10 h-40 w-40 bg-indigo-200/40 dark:bg-indigo-900/30 rounded-full blur-3xl">
            </div>
            <div
                class="pointer-events-none absolute -bottom-10 -left-10 h-40 w-40 bg-sky-200/40 dark:bg-sky-900/30 rounded-full blur-3xl">
            </div>
            <header class="text-center px-6 py-12 md:py-16">
                <p class="text-xs tracking-widest text-indigo-600 font-semibold">Presentamos</p>
                <div class="mt-4 flex justify-center">
                    <img 
                        v-if="isDark" 
                        src="@/assets/logos/DarkModeLogo.png" 
                        alt="Cloud Restaurant Logo" 
                        class="h-16 md:h-20 w-auto"
                    />
                    <img 
                        v-else 
                        src="@/assets/logos/Logo.png" 
                        alt="Cloud Restaurant Logo" 
                        class="h-16 md:h-20 w-auto"
                    />
                </div>
                <h1 class="mt-4 text-2xl md:text-4xl font-extrabold leading-tight text-slate-900 dark:text-slate-100">
                    Software para restaurantes moderno y listo para crecer
                </h1>
                <p class="mt-4 text-gray-600 dark:text-slate-300 max-w-2xl mx-auto">
                    Optimiza mesas, pedidos, cocina y caja en minutos. Escalable de taquerías a cadenas. Añade módulos
                    cuando los necesites.
                </p>
            </header>
        </div>

        <div class="mb-16">
            <h2 class="text-center text-2xl md:text-3xl font-bold text-slate-900 dark:text-slate-100 mb-8">
                ¿Por qué elegir {{ brand }}?
            </h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <FeatureCard 
                    v-for="highlight in highlights" 
                    :key="highlight.title"
                    :icon="highlight.icon"
                    :title="highlight.title"
                    :description="highlight.description"
                />
            </div>
        </div>

        <TrialBanner :features="trialFeatures" />

        <div class="mb-12">
            <h2 class="sr-only">Vistas previas</h2>
            <div class="space-y-16">
                <PreviewSection
                    v-for="(slide, i) in previewSlides"
                    :key="i"
                    :image-url="slide.imageUrl"
                    :title="slide.title"
                    :caption="slide.caption"
                    :is-reversed="i % 2 === 1"
                />
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
            <PricingCard 
                v-for="plan in plans" 
                :key="plan.name" 
                :title="plan.title" 
                :subtitle="plan.subtitle"
                :price="plan.price" 
                :features="plan.features" 
                :highlight="plan.highlight" 
                cta-label="Contratar"
                cta-route-name="Register" 
            />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <AddonCard 
                v-for="addon in addons" 
                :key="addon.title"
                :title="addon.title"
                :description="addon.description"
                :items="addon.items"
            />
        </div>


        <div class="mt-8 space-y-6">
            <div class="bg-indigo-50 dark:bg-indigo-950/30 p-6 rounded-2xl border border-indigo-200 dark:border-indigo-800">
                <h3 class="font-bold text-indigo-900 dark:text-indigo-100 mb-3 flex items-center gap-2">
                    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                    </svg>
                    Limitaciones de la Versión de Prueba (14 días)
                </h3>
                <ul class="text-sm text-indigo-800 dark:text-indigo-200 space-y-2">
                    <li v-for="limit in trialLimitations" :key="limit.label">
                        • <strong>{{ limit.label }}:</strong> {{ limit.value }}
                    </li>
                </ul>
            </div>

            <div>
                <h3 class="font-semibold mb-2 text-slate-900 dark:text-slate-100">Información Adicional</h3>
                <ul class="text-sm text-gray-600 dark:text-slate-400 space-y-1">
                    <li v-for="info in additionalInfo" :key="info">
                        • <span v-html="info.includes('Pago anual') ? `<strong>${info}</strong>` : info"></span>
                    </li>
                </ul>
            </div>
        </div>
    </section>
</template>

<script setup lang="ts">
import PricingCard from '@/components/marketing/PricingCard.vue'
import WhatsAppButton from '@/components/marketing/WhatsAppButton.vue'
import TrialBanner from '@/components/marketing/TrialBanner.vue'
import FeatureCard from '@/components/marketing/FeatureCard.vue'
import AddonCard from '@/components/marketing/AddonCard.vue'
import PreviewSection from '@/components/marketing/PreviewSection.vue'
import { useTheme } from '@/composables/useTheme'
import { useLandingData } from '@/composables/useLandingData'

const brand = 'Cloud Restaurant'
const { isDark } = useTheme()
const { 
  highlights, 
  plans, 
  previewSlides, 
  addons, 
  trialFeatures, 
  trialLimitations, 
  additionalInfo 
} = useLandingData()
</script>
