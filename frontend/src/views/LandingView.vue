<template>
    <!-- WhatsApp floating button -->
    <a
        href="https://wa.me/526623843359?text=Hola!%20Me%20interesa%20obtener%20mas%20informacion%20sobre%20Cloud%20Restaurant"
        target="_blank"
        rel="noopener noreferrer"
        class="fixed bottom-6 right-6 z-50 flex items-center justify-center w-14 h-14 bg-green-500 hover:bg-green-600 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110"
        aria-label="Contactar por WhatsApp"
    >
        <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
        </svg>
    </a>

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
                <div v-for="highlight in highlights" :key="highlight.title"
                    class="flex items-start gap-4 p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 hover:shadow-lg hover:border-indigo-200 dark:hover:border-indigo-800 transition-all duration-200">
                    <div class="flex-shrink-0 w-12 h-12 rounded-xl bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center">
                        <span class="text-2xl">{{ highlight.icon }}</span>
                    </div>
                    <div>
                        <h3 class="font-semibold text-slate-900 dark:text-slate-100 mb-1">{{ highlight.title }}</h3>
                        <p class="text-sm text-slate-600 dark:text-slate-400">{{ highlight.description }}</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Trial Banner -->
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
                    <span to="/register" 
                        class="inline-flex items-center px-8 py-4 bg-white text-indigo-600 font-bold rounded-xl hover:bg-gray-100 transition-all shadow-lg hover:shadow-xl hover:scale-105">
                        Solicita Prueba Gratuita a traves del boton de whatsapp
                        <!-- <svg class="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"/>
                        </svg> -->
                    </span>
                </div>
                <div class="mt-6 flex flex-wrap justify-center gap-6 text-sm text-white/80">
                    <div class="flex items-center gap-2">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                        </svg>
                        35 mesas
                    </div>
                    <div class="flex items-center gap-2">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                        </svg>
                        400 productos
                    </div>
                    <div class="flex items-center gap-2">
                        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                        </svg>
                        Reportes avanzados
                    </div>
                </div>
            </div>
        </div>

        <div class="mb-12">
            <h2 class="sr-only">Vistas previas</h2>
            <div class="space-y-16">
                <section
                    v-for="(s, i) in previewSlides"
                    :key="i"
                    class="grid md:grid-cols-2 gap-8 lg:gap-12 items-center"
                >
                    <div :class="[ 'relative', i % 2 === 1 ? 'md:order-2' : 'md:order-1' ]">
                        <img
                            :src="s.imageUrl"
                            :alt="s.title || 'Vista previa'"
                            class="w-full h-auto object-cover rounded-3xl shadow-2xl ring-1 ring-black/5 dark:ring-white/10"
                            loading="lazy"
                        />
                        <div class="pointer-events-none absolute -inset-4 rounded-[2rem] blur-3xl opacity-20 bg-gradient-to-br from-indigo-400/30 to-sky-400/20 dark:from-indigo-500/10 dark:to-sky-500/10"></div>
                    </div>
                    <div :class="[ i % 2 === 1 ? 'md:order-1' : 'md:order-2' ]">
                        <h3 class="text-2xl md:text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
                            {{ s.title }}
                        </h3>
                        <p class="mt-3 text-slate-600 dark:text-slate-300 text-base md:text-lg leading-relaxed">
                            {{ s.caption }}
                        </p>
                        <div class="mt-6 h-px bg-gradient-to-r from-transparent via-slate-200 dark:via-slate-700 to-transparent"></div>
                    </div>
                </section>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
            <PricingCard v-for="plan in plans" :key="plan.name" :title="plan.title" :subtitle="plan.subtitle"
                :price="plan.price" :features="plan.features" :highlight="plan.highlight" cta-label="Contratar"
                cta-route-name="Register" />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div v-for="addon in addons" :key="addon.title"
                class="p-6 border rounded-2xl bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 hover:shadow-md transition">
                <h3 class="font-semibold text-slate-900 dark:text-slate-100">{{ addon.title }}</h3>
                <p class="text-sm text-gray-600 dark:text-slate-400 mt-2">{{ addon.description }}</p>
                <ul v-if="addon.items" class="mt-3 text-sm space-y-1">
                    <li v-for="(item, idx) in addon.items" :key="idx" class="text-slate-700 dark:text-slate-300">• {{
                        item }}</li>
                </ul>
                <div v-else class="mt-4 text-lg font-extrabold text-slate-900 dark:text-slate-100">{{ addon.price }}
                </div>
            </div>
        </div>

        <div v-if="false" class="mb-12">
            <h3 class="text-lg font-semibold mb-3">Paquetes recomendados</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div v-for="pack in packs" :key="pack.name"
                    class="p-5 border rounded-2xl bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700 hover:shadow-md transition">
                    <strong class="text-slate-900 dark:text-slate-100">{{ pack.name }}</strong>
                    <p class="text-sm text-gray-600 dark:text-slate-400 mt-2">{{ pack.description }}</p>
                    <div class="mt-2 font-semibold text-slate-900 dark:text-slate-100">{{ pack.price }}</div>
                </div>
            </div>
        </div>

        <div v-if="false"
            class="bg-gray-50 dark:bg-slate-900 p-6 rounded-2xl border border-gray-200 dark:border-slate-700 ring-1 ring-inset ring-gray-100 dark:ring-slate-800">
            <h3 class="font-semibold text-slate-900 dark:text-slate-100">Sucursales y descuentos</h3>
            <p class="text-sm text-gray-600 dark:text-slate-400 mt-2">
                Cada sucursal se toma como un negocio aparte. Ofrecemos descuento por volumen a partir de 3 sucursales —
                ejemplo: 20% de descuento en la tarifa mensual de cada sucursal.
            </p>
            <p class="text-sm text-gray-600 dark:text-slate-400 mt-2">
                A partir de 3 sucursales incluimos el "Superusuario" para el dueño sin costo adicional.
            </p>
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
                    <li>• <strong>Duración:</strong> 14 días calendario desde el registro</li>
                    <li>• <strong>Límites:</strong> 35 mesas, 400 productos, 9 usuarios totales</li>
                    <li>• <strong>Funciones:</strong> Acceso completo a Plan Pro (ingredientes, reportes avanzados, cocina)</li>
                    <li>• <strong>Datos:</strong> Se conservan al actualizar a plan de pago</li>
                    <li>• <strong>Sin compromiso:</strong> No se requiere tarjeta de crédito</li>
                </ul>
            </div>

            <div>
                <h3 class="font-semibold mb-2 text-slate-900 dark:text-slate-100">Información Adicional</h3>
                <ul class="text-sm text-gray-600 dark:text-slate-400 space-y-1">
                    <li>• Todos los precios son en MXN y pueden ajustarse según integraciones adicionales</li>
                    <li>• Soporte básico por WhatsApp incluido en todos los planes</li>
                    <li>• <strong>Pago anual: 25% de descuento</strong> (3 meses gratis)</li>
                    <li>• Descuentos por volumen disponibles para 3+ sucursales (15-35% off)</li>
                    <li>• Upgrade/downgrade disponible en cualquier momento</li>
                </ul>
            </div>
        </div>
    </section>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import PricingCard from '@/components/marketing/PricingCard.vue'
import { useTheme } from '@/composables/useTheme'

const brand = 'Cloud Restaurant'
const { isDark } = useTheme()

const highlights = [
        {
        icon: '⚡',
        title: 'Rápido, sencillo y moderno',
        description: 'Interfaz intuitiva y ágil diseñada para que tu equipo la domine en minutos.'
    },
    {
        icon: '☁️',
        title: 'Información almacenada en la nube',
        description: 'Tus datos seguros y accesibles en cualquier momento sin preocuparte por respaldos manuales.'
    },
    {
        icon: '📱',
        title: 'Compatible con móvil, tablet, PC',
        description: 'Accede desde cualquier dispositivo con total flexibilidad y comodidad.'
    },
    {
        icon: '🌐',
        title: 'Información disponible 24/7',
        description: 'Consulta tu negocio desde cualquier lugar del mundo, en cualquier momento.'
    },
    {
        icon: '🤝',
        title: 'Atención personalizada',
        description: 'Soporte dedicado para resolver tus dudas y ayudarte a crecer.'
    },
    {
        icon: '🛠️',
        title: 'Desarrollo de funciones extra',
        description: 'Solicita funcionalidades personalizadas adaptadas a las necesidades de tu negocio.'
    }
]

const plans = [
    {
        name: 'starter',
        title: 'Starter',
        subtitle: 'Food trucks y cafeterías pequeñas',
        price: '$399 / mes',
        features: [
            '1 admin + 2 meseros',
            'Hasta 10 mesas',
            '50 productos en menú',
            'Módulos: Mesas, Pedidos, Menú, Caja',
            'Reportes básicos (7 días)',
        ],
    },
    {
        name: 'basic',
        title: 'Básico',
        subtitle: 'Taquerías y restaurantes pequeños',
        price: '$699 / mes',
        features: [
            '1 admin + 3 meseros + 1 cocina',
            'Hasta 20 mesas',
            '150 productos en menú',
            'Módulo de Ingredientes incluido 🎁',
            'Reportes básicos (15 días)',
        ],
    },
    {
        name: 'pro',
        title: 'Pro',
        subtitle: 'Restaurantes familiares en crecimiento',
        price: '$999 / mes',
        highlight: true,
        features: [
            '1 admin + 4 meseros + 2 cajeros + 2 cocina',
            'Hasta 35 mesas',
            '400 productos en menú',
            'Ingredientes + Reportes Avanzados incluidos 🎁'
        ],
    },
    {
        name: 'business',
        title: 'Business',
        subtitle: 'Restaurantes establecidos',
        price: '$1,499 / mes',
        features: [
            '2 admin + 8 meseros + 3 cajeros + 3 cocina',
            'Hasta 60 mesas',
            '800 productos en menú',
            'Todos los módulos incluidos 🎁',
        ],
    },
    {
        name: 'enterprise',
        title: 'Enterprise',
        subtitle: 'Cadenas y franquicias',
        price: '$2,199 / mes',
        features: [
            '1 dueño + 4 admin + 15 meseros + 5 cajeros + 5 cocina',
            'Hasta 150 mesas',
            'Productos ilimitados',
            'Multi-sucursal + Gerente de cuenta',
        ],
    },
]

const previewSlides = [
    {
        imageUrl: new URL('../assets/marketing/screenshots/tables.png', import.meta.url).toString(),
        title: 'Mesas en tiempo real',
        caption: 'Visualiza ocupación y estado de cada mesa al instante.'
    },
    {
        imageUrl: new URL('../assets/marketing/screenshots/menu.png', import.meta.url).toString(),
        title: 'Gestión de Menú',
        caption: 'Crea categorías, productos y modificadores fácilmente.'
    },
    {
        imageUrl: new URL('../assets/marketing/screenshots/orders.png', import.meta.url).toString(),
        title: 'Toma de pedidos',
        caption: 'Agiliza pedidos por mesa, para llevar o delivery.'
    },
    {
        imageUrl: new URL('../assets/marketing/screenshots/orders2.png', import.meta.url).toString(),
        title: 'Toma de pedidos',
        caption: 'Agiliza pedidos por mesa, para llevar o delivery.'
    },
    {
        imageUrl: new URL('../assets/marketing/screenshots/kitchen.png', import.meta.url).toString(),
        title: 'Pantalla de Cocina',
        caption: 'Prioriza y controla la preparación de platillos.'
    },
    {
        imageUrl: new URL('../assets/marketing/screenshots/cash.png', import.meta.url).toString(),
        title: 'Caja y cobros',
        caption: 'Cierra cuentas con múltiples métodos de pago.'
    },
    {
        imageUrl: new URL('../assets/marketing/screenshots/dashboard.png', import.meta.url).toString(),
        title: 'Dashboard',
        caption: 'Información general de la operación diaria'
    }

]

const addons = [
    {
        title: 'Módulos Extra',
        description: 'Agrega funcionalidades adicionales',
        items: [
            'Inventario: $199/mes',
            'Reportes Avanzados: $149/mes',
            'Módulo de Cocina (solo Starter): $99/mes',
        ],
    },
    {
        title: 'Recursos Adicionales',
        description: 'Incrementa los límites de tu plan',
        items: [
            'Usuario Extra: $79/mes',
            '10 Mesas Extra: $39/mes',
            '100 Productos Extra: $79/mes',
        ],
    },
    {
        title: 'Servicios One-Time',
        description: 'Pago único',
        items: [
            'Capacitación Small: $900',
            'Capacitación Medium: $1,300',
            'Capacitación Large: $1,800',
            'Carga de Menú: $300',
            'Diseño Personalizado: desde $400/mes',
        ],
    },
]

const packs = [
    { name: 'Analítica', description: 'Reportes avanzados + exportes', price: '$300 / mes' },
    { name: 'Gestión', description: 'Inventario + reportes avanzados', price: '$400 / mes' },
    { name: 'Full Pro', description: 'Todos los extras + diseño', price: '$600 / mes' },
]
</script>
